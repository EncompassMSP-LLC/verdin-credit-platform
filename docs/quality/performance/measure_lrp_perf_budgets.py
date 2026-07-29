"""Measure LRP V1.0 performance budgets (LRP-504).

Exercises mortgage-partner dashboard + readiness report/export against a running
API. Writes JSON results and optionally soft/hard-fails vs documented budgets.

Usage from the repository root:

    python docs/quality/performance/measure_lrp_perf_budgets.py

Requires: API on E2E_BASE_URL, PostgreSQL, ENABLE_MORTGAGE_PARTNER=true.
"""

from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def find_repo_root(start: Path) -> Path:
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
from api.modules.auth.models import Organization  # noqa: E402
from tests.e2e.fixtures.organization import (  # noqa: E402
    create_organization,
    delete_organization,
)
from tests.e2e.fixtures.users import create_owner_user  # noqa: E402
from tests.e2e.helpers import auth  # noqa: E402

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_URL_SYNC = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://verdin:verdin@localhost:5432/verdin_credit_test",
)
ITERATIONS = int(os.environ.get("PERF_ITERATIONS", "10"))
ENFORCE = os.environ.get("PERF_LRP_ENFORCE", "observe").strip().lower()
OUT_PATH = Path(
    os.environ.get(
        "PERF_LRP_OUT",
        str(REPO_ROOT / "docs" / "quality" / "performance" / "_artifacts" / "lrp-perf.json"),
    )
)

# Product budgets (local/staging p95) and CI observe ceilings (ms).
BUDGETS: dict[str, dict[str, float]] = {
    "partner_dashboard_summary": {"product_p95": 500.0, "ci_observe_p95": 3000.0},
    "readiness_report_json": {"product_p95": 750.0, "ci_observe_p95": 4000.0},
    "readiness_export_text": {"product_p95": 1500.0, "ci_observe_p95": 6000.0},
    "platform_dashboard": {"product_p95": 500.0, "ci_observe_p95": 3000.0},
}


def elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0


def percentile(sorted_values: list[float], percent: int) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * (percent / 100)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def summarize(values: list[float]) -> dict[str, float]:
    timings = sorted(float(value) for value in values)
    return {
        "avg": round(statistics.fmean(timings), 2),
        "median": round(statistics.median(timings), 2),
        "p95": round(percentile(timings, 95), 2),
        "max": round(max(timings), 2),
        "n": float(len(timings)),
    }


def measure_http(
    call: Callable[[], httpx.Response],
    *,
    iterations: int,
    expected_status: int = 200,
) -> dict[str, float]:
    warm = call()
    if warm.status_code != expected_status:
        raise RuntimeError(
            f"Warm-up expected {expected_status}, got {warm.status_code}: {warm.text}"
        )
    timings: list[float] = []
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


def seed_partner_org(session: Session) -> Organization:
    suffix = uuid.uuid4().hex[:8]
    org = Organization(
        id=uuid.uuid4(),
        name=f"LRP Perf Lender {suffix}",
        slug=f"lrp-perf-lender-{suffix}",
        is_active=True,
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


def main() -> int:
    engine = create_engine(DATABASE_URL_SYNC, pool_pre_ping=True, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with session_factory() as session:
        organization = create_organization(session)
        owner = create_owner_user(session, organization.id)
        partner = seed_partner_org(session)

    results: dict[str, Any] = {
        "schema_version": "lrp-perf-budgets-v1",
        "measured_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "base_url": BASE_URL,
        "iterations": ITERATIONS,
        "enforce_mode": ENFORCE,
        "budgets": BUDGETS,
        "metrics": {},
        "budget_results": {},
    }

    exit_code = 0
    try:
        with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
            health = client.get("/api/v1/health")
            health.raise_for_status()
            tokens = auth.login(client, owner.email, owner.password)
            headers = tokens.headers

            partnership = client.post(
                "/api/v1/mortgage-partner/partnerships",
                headers=headers,
                json={
                    "partner_organization_id": str(partner.id),
                    "display_name": f"LRP Perf Partnership {partner.slug}",
                    "partner_type": "lender",
                    "status": "active",
                },
            )
            partnership.raise_for_status()
            partnership_id = partnership.json()["id"]

            client_body = client.post(
                "/api/v1/clients",
                headers=headers,
                json={
                    "display_name": f"LRP Perf Borrower {uuid.uuid4().hex[:6]}",
                    "email": f"lrp-perf-{uuid.uuid4().hex[:8]}@verdin-e2e.com",
                    "mailing_address_line1": "200 Perf Lane",
                    "mailing_city": "Austin",
                    "mailing_state": "TX",
                    "mailing_postal_code": "78701",
                    "status": "active",
                },
            )
            client_body.raise_for_status()
            client_id = client_body.json()["id"]

            case = client.post(
                "/api/v1/cases",
                headers=headers,
                json={
                    "title": f"LRP Perf Case {uuid.uuid4().hex[:6]}",
                    "client_id": client_id,
                },
            )
            case.raise_for_status()
            case_id = case.json()["id"]

            account = client.post(
                "/api/v1/accounts",
                headers=headers,
                json={
                    "case_id": case_id,
                    "creditor_name": "LRP Perf Bank",
                    "bureau": "equifax",
                    "account_type": "credit_card",
                    "account_status": "open",
                    "payment_status": "late_60",
                    "account_number_masked": "****9999",
                    "balance": "900.00",
                    "past_due_amount": "100.00",
                },
            )
            account.raise_for_status()

            analysis = client.post(
                f"/api/v1/cases/{case_id}/credit-analysis/runs",
                headers=headers,
            )
            analysis.raise_for_status()

            referral = client.post(
                f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
                headers=headers,
                json={
                    "client_id": client_id,
                    "case_id": case_id,
                    "source_label": "LRP-504 perf harness",
                    "status": "new",
                },
            )
            referral.raise_for_status()
            referral_id = referral.json()["id"]

            metrics = {
                "platform_dashboard": measure_http(
                    lambda: client.get("/api/v1/dashboard", headers=headers),
                    iterations=ITERATIONS,
                ),
                "partner_dashboard_summary": measure_http(
                    lambda: client.get(
                        f"/api/v1/mortgage-partner/partnerships/{partnership_id}"
                        "/dashboard-summary",
                        headers=headers,
                    ),
                    iterations=ITERATIONS,
                ),
                "readiness_report_json": measure_http(
                    lambda: client.get(
                        f"/api/v1/mortgage-partner/partnerships/{partnership_id}"
                        f"/referrals/{referral_id}/readiness-report",
                        headers=headers,
                    ),
                    iterations=ITERATIONS,
                ),
                "readiness_export_text": measure_http(
                    lambda: client.get(
                        f"/api/v1/mortgage-partner/partnerships/{partnership_id}"
                        f"/referrals/{referral_id}/readiness-report/export",
                        headers=headers,
                        params={"format": "text"},
                    ),
                    iterations=ITERATIONS,
                ),
            }
            results["metrics"] = metrics

            use_ci_ceiling = ENFORCE in {"observe", "ci", "0", "false", ""}
            for name, stats in metrics.items():
                budget = BUDGETS[name]
                ceiling = (
                    budget["ci_observe_p95"] if use_ci_ceiling else budget["product_p95"]
                )
                passed = stats["p95"] <= ceiling
                results["budget_results"][name] = {
                    "p95_ms": stats["p95"],
                    "ceiling_ms": ceiling,
                    "product_p95_budget_ms": budget["product_p95"],
                    "passed": passed,
                }
                status = "PASS" if passed else "FAIL"
                print(
                    f"{status} {name}: p95={stats['p95']} ms "
                    f"(ceiling {ceiling} ms; product budget {budget['product_p95']} ms)"
                )
                if not passed and ENFORCE in {"1", "true", "enforce", "product"}:
                    exit_code = 1
                elif not passed and ENFORCE == "observe":
                    print(f"  (observe mode — soft fail for {name})")

    finally:
        with session_factory() as session:
            try:
                delete_organization(session, organization.id)
            except Exception:  # noqa: BLE001 — teardown best-effort
                session.rollback()
            try:
                delete_organization(session, partner.id)
            except Exception:  # noqa: BLE001
                session.rollback()
        engine.dispose()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
