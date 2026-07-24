"""Tests for credit-analysis run export (text + PDF) and the cases export endpoint."""

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_export import (
    build_credit_analysis_export,
    build_credit_analysis_pdf_bytes,
    build_credit_analysis_text,
    export_filename,
    sanitize_content_disposition_filename,
)
from api.modules.accounts.credit_analysis_schemas import CreditAnalysisRunResponse
from tests.accounts.conftest import sample_account_payload

# ---------------------------------------------------------------------------
# Pure-formatter unit tests
# ---------------------------------------------------------------------------


def _sample_run(**overrides: object) -> CreditAnalysisRunResponse:
    now = datetime.now(UTC)
    base = CreditAnalysisRunResponse(
        id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        generated_at=now,
        reports_evaluated=3,
        tradelines_evaluated=5,
        borrower_readiness_score=72,
        mortgage_readiness_score=72,
        schema_version="lrs.v1",
        band="near_ready",
        status="published",
        payload={
            "disclaimer": ADVISORY_DISCLAIMER,
            "dimensions": [
                {
                    "key": "payment_derogs",
                    "label": "Payment / derogs",
                    "score": 68,
                    "weight": 0.25,
                }
            ],
            "blockers": [
                {
                    "id": "acct-1",
                    "title": "Capital One (equifax)",
                    "impact": "High-risk tradeline may delay lending readiness.",
                    "action": "Dispute inaccurate account status with furnisher",
                }
            ],
            "accounts": [],
            "trend": None,
            "partial_bureau_coverage": True,
            "formula_version": "lrs.v1.0",
            "score_version": "lrs.v1",
        },
        formula_version="lrs.v1.0",
        score_version="lrs.v1",
        inputs_hash="abc123" * 5,
        published_at=now,
    )
    for k, v in overrides.items():
        object.__setattr__(base, k, v)
    return base


def test_export_filename_text() -> None:
    run = _sample_run()
    name = export_filename(run, "text")
    assert name.startswith("mortgage-readiness-")
    assert name.endswith(".txt")


def test_export_filename_pdf() -> None:
    run = _sample_run()
    name = export_filename(run, "pdf")
    assert name.endswith(".pdf")


def test_sanitize_filename_removes_spaces() -> None:
    assert sanitize_content_disposition_filename("my file.pdf") == "my_file.pdf"


def test_build_text_contains_disclaimer() -> None:
    run = _sample_run()
    text = build_credit_analysis_text(run)
    assert ADVISORY_DISCLAIMER[:40] in text


def test_build_text_contains_score() -> None:
    run = _sample_run()
    text = build_credit_analysis_text(run)
    assert "72/100" in text
    assert "near_ready" in text


def test_build_text_contains_dimensions() -> None:
    run = _sample_run()
    text = build_credit_analysis_text(run)
    assert "Payment / derogs" in text


def test_build_text_contains_blockers() -> None:
    run = _sample_run()
    text = build_credit_analysis_text(run)
    assert "Capital One" in text


def test_build_pdf_returns_bytes() -> None:
    run = _sample_run()
    data = build_credit_analysis_pdf_bytes(run)
    assert isinstance(data, bytes)
    assert data[:4] == b"%PDF"


def test_build_export_text_tuple() -> None:
    run = _sample_run()
    content, filename, media_type = build_credit_analysis_export(run, "text")
    assert isinstance(content, bytes)
    assert filename.endswith(".txt")
    assert media_type == "text/plain; charset=utf-8"
    assert ADVISORY_DISCLAIMER[:20] in content.decode("utf-8")


def test_build_export_pdf_tuple() -> None:
    run = _sample_run()
    content, filename, media_type = build_credit_analysis_export(run, "pdf")
    assert content[:4] == b"%PDF"
    assert filename.endswith(".pdf")
    assert media_type == "application/pdf"


# ---------------------------------------------------------------------------
# API integration: cases credit-analysis export endpoint
# ---------------------------------------------------------------------------


def test_credit_analysis_export_text(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    """Create a run then export it as text."""
    # Seed a tradeline so the run has real data
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )

    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert create.status_code == 201, create.text
    run_id = create.json()["id"]

    export = api_client.get(
        f"/api/v1/cases/{sample_case_id}/credit-analysis/runs/{run_id}/export",
        headers=manager_headers,
        params={"export_format": "text"},
    )
    assert export.status_code == 200, export.text
    assert export.headers["content-type"].startswith("text/plain")
    assert "Content-Disposition" in export.headers
    assert "mortgage-readiness-" in export.headers["Content-Disposition"]
    body_text = export.text
    assert "DISCLAIMER" in body_text
    assert "Lending Readiness" in body_text


def test_credit_analysis_export_pdf(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    """Export an existing run as PDF."""
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/credit-analysis/runs",
        headers=manager_headers,
    )
    assert create.status_code == 201, create.text
    run_id = create.json()["id"]

    export = api_client.get(
        f"/api/v1/cases/{sample_case_id}/credit-analysis/runs/{run_id}/export",
        headers=manager_headers,
        params={"export_format": "pdf"},
    )
    assert export.status_code == 200, export.text
    assert export.headers["content-type"] == "application/pdf"
    assert export.content[:4] == b"%PDF"


def test_credit_analysis_export_wrong_run_404(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    """Requesting a non-existent run_id must 404."""
    export = api_client.get(
        f"/api/v1/cases/{sample_case_id}/credit-analysis/runs/{uuid.uuid4()}/export",
        headers=manager_headers,
        params={"export_format": "text"},
    )
    assert export.status_code == 404
