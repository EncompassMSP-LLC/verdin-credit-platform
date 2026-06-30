"""Measure the Sprint 4.3.1 Operational Core performance baseline.

This script is intentionally lightweight and local-stack oriented. It uses the
same synthetic credit-report fixture as the golden-path E2E suite, creates an
isolated organization/user directly in the database, then measures the running
API and worker through HTTP.

Usage from the repository root:

    python docs/quality/performance/measure_v431_baseline.py

Required services: API on E2E_BASE_URL, worker, PostgreSQL, Redis, and MinIO.
"""

from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


def find_repo_root(start: Path) -> Path:
    """Find the repository root regardless of where this script is located."""
    for candidate in (start, *start.parents):
        if (candidate / "apps").exists() and (candidate / "packages").exists():
            return candidate
    raise RuntimeError(f"Could not find repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
API_ROOT = REPO_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import api.models  # noqa: F401, E402
from tests.e2e.fixtures import documents as doc  # noqa: E402
from tests.e2e.fixtures.organization import (  # noqa: E402
    create_organization,
    delete_organization,
)
from tests.e2e.fixtures.users import create_owner_user  # noqa: E402
from tests.e2e.helpers import auth  # noqa: E402

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_URL_SYNC = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://verdin:verdin@localhost:5432/verdin_credit",
)
ITERATIONS = int(os.environ.get("PERF_ITERATIONS", "10"))
PIPELINE_ITERATIONS = int(os.environ.get("PERF_PIPELINE_ITERATIONS", "5"))
POLL_INTERVAL_SECONDS = float(os.environ.get("PERF_POLL_INTERVAL_SECONDS", "0.05"))
POLL_TIMEOUT_SECONDS = float(os.environ.get("PERF_POLL_TIMEOUT_SECONDS", "30"))


def main() -> None:
    engine = create_engine(DATABASE_URL_SYNC, pool_pre_ping=True, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with session_factory() as session:
        organization = create_organization(session)
        owner = create_owner_user(session, organization.id)

    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            health = client.get("/api/v1/health")
            health.raise_for_status()

            tokens = auth.login(client, owner.email, owner.password)
            headers = tokens.headers

            results = {
                "environment": collect_environment(),
                "measured_at": datetime.now(UTC).isoformat(),
                "base_url": BASE_URL,
                "iterations": ITERATIONS,
                "pipeline_iterations": PIPELINE_ITERATIONS,
                "metrics": {},
            }

            results["metrics"]["login_ms"] = measure_sync(
                lambda: auth.login(client, owner.email, owner.password),
                iterations=ITERATIONS,
            )
            results["metrics"]["dashboard_api_ms"] = measure_http(
                lambda: client.get("/api/v1/dashboard", headers=headers),
                iterations=ITERATIONS,
            )
            results["metrics"]["create_case_ms"] = measure_http(
                lambda: client.post(
                    "/api/v1/cases",
                    headers=headers,
                    json={**doc.CASE_PAYLOAD, "title": unique_title("Perf Case")},
                ),
                iterations=ITERATIONS,
                expected_status=201,
            )

            case = create_case(client, headers)
            account = create_account(client, headers, case["id"])

            results["metrics"]["upload_document_ms"] = measure_http(
                lambda: upload_document(client, headers, case["id"], pages=1),
                iterations=ITERATIONS,
                expected_status=201,
            )

            one_page_pipeline = [
                run_pipeline_measurement(
                    client,
                    headers,
                    case["id"],
                    account["id"],
                    session_factory,
                    pages=1,
                )
                for _ in range(PIPELINE_ITERATIONS)
            ]
            multi_page_pipeline = [
                run_pipeline_measurement(
                    client,
                    headers,
                    case["id"],
                    account["id"],
                    session_factory,
                    pages=3,
                )
                for _ in range(PIPELINE_ITERATIONS)
            ]

            results["metrics"]["ocr_1_page_ms"] = summarize(
                item["ocr_ms"] for item in one_page_pipeline
            )
            results["metrics"]["ocr_3_page_ms"] = summarize(
                item["ocr_ms"] for item in multi_page_pipeline
            )
            results["metrics"]["classification_ms"] = summarize(
                item["classification_ms"] for item in one_page_pipeline
            )
            results["metrics"]["metadata_extraction_ms"] = summarize(
                item["metadata_extraction_ms"] for item in one_page_pipeline
            )
            results["metrics"]["entity_resolution_ms"] = summarize(
                item["entity_resolution_ms"] for item in one_page_pipeline
            )
            results["metrics"]["timeline_write_ms"] = summarize(
                measure_timeline_write(client, headers) for _ in range(ITERATIONS)
            )

            print(json.dumps(results, indent=2))
    finally:
        with session_factory() as session:
            try:
                delete_organization(session, organization.id)
            except Exception:
                session.rollback()
        engine.dispose()


def measure_http(
    call: Callable[[], httpx.Response],
    *,
    iterations: int,
    expected_status: int = 200,
) -> dict[str, float]:
    call().raise_for_status()  # warm-up
    timings = []
    for _ in range(iterations):
        start = time.perf_counter()
        response = call()
        elapsed = elapsed_ms(start)
        if response.status_code != expected_status:
            raise RuntimeError(
                f"Expected {expected_status}, got {response.status_code}: {response.text}"
            )
        timings.append(elapsed)
    return summarize(timings)


def measure_sync(call: Callable[[], Any], *, iterations: int) -> dict[str, float]:
    call()  # warm-up
    timings = []
    for _ in range(iterations):
        start = time.perf_counter()
        call()
        timings.append(elapsed_ms(start))
    return summarize(timings)


def summarize(values: Any) -> dict[str, float]:
    timings = sorted(float(value) for value in values)
    return {
        "avg": round(statistics.fmean(timings), 2),
        "median": round(statistics.median(timings), 2),
        "p95": round(percentile(timings, 95), 2),
        "max": round(max(timings), 2),
    }


def percentile(sorted_values: list[float], percent: int) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * (percent / 100)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def create_case(client: httpx.Client, headers: dict[str, str]) -> dict[str, Any]:
    response = client.post(
        "/api/v1/cases",
        headers=headers,
        json={**doc.CASE_PAYLOAD, "title": unique_title("Perf Pipeline Case")},
    )
    response.raise_for_status()
    return response.json()


def create_account(
    client: httpx.Client, headers: dict[str, str], case_id: str
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/accounts",
        headers=headers,
        json={**doc.ACCOUNT_PAYLOAD, "case_id": case_id},
    )
    response.raise_for_status()
    return response.json()


def upload_document(
    client: httpx.Client,
    headers: dict[str, str],
    case_id: str,
    *,
    pages: int,
) -> httpx.Response:
    pdf = build_pdf(pages=pages)
    return client.post(
        "/api/v1/documents",
        headers=headers,
        data={
            "title": unique_title(f"Perf {pages}-page Credit Report"),
            "case_id": case_id,
        },
        files={"file": (doc.DOCUMENT_FILENAME, pdf, doc.DOCUMENT_MIME_TYPE)},
    )


def run_pipeline_measurement(
    client: httpx.Client,
    headers: dict[str, str],
    case_id: str,
    account_id: str,
    session_factory: sessionmaker[Session],
    *,
    pages: int,
) -> dict[str, float]:
    upload_started = datetime.now(UTC)
    response = upload_document(client, headers, case_id, pages=pages)
    response.raise_for_status()
    document_id = response.json()["id"]

    wait_until(
        lambda: (
            client.get(f"/api/v1/documents/{document_id}/ocr", headers=headers)
            .json()
            .get("processing_status")
            == "completed"
        ),
        f"OCR completed for {document_id}",
    )
    wait_until(
        lambda: (
            client.get(
                f"/api/v1/documents/{document_id}/classification", headers=headers
            )
            .json()
            .get("document_type")
            is not None
        ),
        f"classification completed for {document_id}",
    )
    wait_until(
        lambda: metadata_ready(client, headers, document_id),
        f"metadata extracted for {document_id}",
    )
    wait_until(
        lambda: account_resolution_ready(client, headers, document_id, account_id),
        f"entity resolution linked account for {document_id}",
    )

    with session_factory() as session:
        row = (
            session.execute(
                text(
                    """
                SELECT
                  d.ocr_processed_at,
                  d.classified_at,
                  dm.extracted_at,
                  MAX(der.created_at) AS resolved_at
                FROM documents d
                LEFT JOIN document_metadata dm ON dm.document_id = d.id
                LEFT JOIN document_entity_resolutions der ON der.document_id = d.id
                WHERE d.id = :document_id
                GROUP BY d.id, dm.extracted_at
                """
                ),
                {"document_id": document_id},
            )
            .mappings()
            .one()
        )

    ocr_at = ensure_aware(row["ocr_processed_at"])
    classified_at = ensure_aware(row["classified_at"])
    extracted_at = ensure_aware(row["extracted_at"])
    resolved_at = ensure_aware(row["resolved_at"])

    return {
        "ocr_ms": delta_ms(upload_started, ocr_at),
        "classification_ms": delta_ms(ocr_at, classified_at),
        "metadata_extraction_ms": delta_ms(classified_at, extracted_at),
        "entity_resolution_ms": delta_ms(extracted_at, resolved_at),
    }


def metadata_ready(
    client: httpx.Client, headers: dict[str, str], document_id: str
) -> bool:
    response = client.get(f"/api/v1/documents/{document_id}/metadata", headers=headers)
    return (
        response.status_code == 200
        and response.json().get("metadata_status") == "extracted"
    )


def account_resolution_ready(
    client: httpx.Client,
    headers: dict[str, str],
    document_id: str,
    account_id: str,
) -> bool:
    response = client.get(
        f"/api/v1/documents/{document_id}/resolutions", headers=headers
    )
    if response.status_code != 200:
        return False
    for resolution in response.json().get("resolutions", []):
        if (
            resolution["entity_type"] == "account"
            and resolution["resolution_status"] == "matched"
            and resolution["matched_entity_id"] == account_id
        ):
            return True
    return False


def measure_timeline_write(client: httpx.Client, headers: dict[str, str]) -> float:
    started_at = datetime.now(UTC)
    case = create_case(client, headers)
    response = client.get(
        "/api/v1/timeline",
        headers=headers,
        params={"case_id": case["id"], "event_type": "CASE_CREATED", "page_size": 1},
    )
    response.raise_for_status()
    items = response.json()["items"]
    if not items:
        raise RuntimeError("CASE_CREATED timeline event was not visible")
    created_at = ensure_aware(
        datetime.fromisoformat(items[0]["created_at"].replace("Z", "+00:00"))
    )
    return delta_ms(started_at, created_at)


def wait_until(predicate: Callable[[], bool], description: str) -> None:
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(description)


def build_pdf(*, pages: int) -> bytes:
    if pages == 1:
        return doc.build_credit_report_pdf()

    from io import BytesIO

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    for page in range(pages):
        text_object = pdf.beginText(72, 720)
        text_object.setFont("Helvetica", 11)
        text_object.textLine(f"Page {page + 1} of {pages}")
        for line in doc.CREDIT_REPORT_LINES:
            text_object.textLine(line)
        pdf.drawText(text_object)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def collect_environment() -> dict[str, str]:
    return {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python": platform.python_version(),
        "node": run_capture("node --version"),
        "git_ref": run_capture("git rev-parse --short HEAD"),
        "postgres": "postgres:16-alpine via docker compose",
        "redis": "redis:7-alpine via docker compose",
        "minio": "minio/minio:latest via docker compose",
        "api_workers": "1 uvicorn process",
        "background_workers": "1 worker process",
        "dataset": "isolated org, owner user, golden-path case/account/document/task shape",
    }


def run_capture(command: str) -> str:
    import subprocess

    try:
        return subprocess.check_output(
            command.split(), text=True, cwd=REPO_ROOT
        ).strip()
    except Exception as exc:  # noqa: BLE001
        return f"unavailable ({exc})"


def unique_title(prefix: str) -> str:
    return f"{prefix} {time.time_ns()}"


def elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000


def delta_ms(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() * 1000


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


if __name__ == "__main__":
    main()
