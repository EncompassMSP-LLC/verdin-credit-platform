"""End-to-end Version 4.5 golden path over the HTTP API.

    Authenticate → Case → Credit report upload → OCR → Parse
    → Account candidate → Create account → Dispute draft → Letter lifecycle
"""

from __future__ import annotations

from typing import Any

import httpx

from tests.e2e.fixtures import documents as doc
from tests.e2e.fixtures.users import UserRecord
from tests.e2e.helpers import auth
from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.assertions import expect_ok
from tests.e2e.helpers.dispute_lifecycle import run_dispute_letter_lifecycle
from tests.e2e.helpers.wait_for_worker import poll_until


def _candidate_to_account_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_id": candidate["case_id"],
        "bureau": candidate["bureau"],
        "creditor_name": candidate["creditor_name"],
        "original_creditor": candidate.get("original_creditor"),
        "account_number_masked": candidate.get("account_number_masked"),
        "account_type": candidate["account_type"],
        "account_status": candidate["account_status"],
        "payment_status": candidate["payment_status"],
        "remarks": candidate.get("remarks"),
    }
    if candidate.get("balance") is not None:
        payload["balance"] = float(candidate["balance"])
    if candidate.get("past_due_amount") is not None:
        payload["past_due_amount"] = float(candidate["past_due_amount"])
    return payload


def test_import_to_dispute_lifecycle(
    http: httpx.Client,
    owner: UserRecord,
    artifacts: ArtifactCollector,
) -> None:
    tokens = auth.login(http, owner.email, owner.password)
    headers = tokens.headers

    case = expect_ok(
        http.post("/api/v1/cases", headers=headers, json=doc.CASE_PAYLOAD),
        label="import_case",
        artifacts=artifacts,
        expected_status=201,
    )
    case_id = case["id"]

    pdf_bytes = doc.build_credit_report_pdf()
    upload = expect_ok(
        http.post(
            "/api/v1/documents",
            headers=headers,
            data={"title": doc.DOCUMENT_TITLE, "case_id": case_id},
            files={"file": (doc.DOCUMENT_FILENAME, pdf_bytes, doc.DOCUMENT_MIME_TYPE)},
        ),
        label="import_upload",
        artifacts=artifacts,
        expected_status=201,
    )
    document_id = upload["id"]

    ocr_response = poll_until(
        lambda: http.get(f"/api/v1/documents/{document_id}/ocr", headers=headers),
        lambda response: (
            response.status_code == 200
            and response.json().get("processing_status") == "completed"
        ),
        description="document OCR processing_status == completed",
    )
    artifacts.record("import_ocr", ocr_response.json())
    assert ocr_response.json()["ocr_text"]

    metadata_response = poll_until(
        lambda: http.get(f"/api/v1/documents/{document_id}/metadata", headers=headers),
        lambda response: (
            response.status_code == 200
            and response.json().get("metadata_status") == "extracted"
        ),
        description="document metadata extracted",
    )
    metadata = metadata_response.json()
    artifacts.record("import_metadata", metadata)
    assert metadata["creditor"] == doc.EXPECTED_CREDITOR

    parsed_report = expect_ok(
        http.get(
            f"/api/v1/documents/{document_id}/parsed-credit-report",
            headers=headers,
        ),
        label="import_parsed_credit_report",
        artifacts=artifacts,
    )
    assert parsed_report["bureau"] == doc.EXPECTED_BUREAU
    assert parsed_report["parsed_report"]["accounts"]

    candidates_response = poll_until(
        lambda: http.get(
            f"/api/v1/documents/{document_id}/parsed-credit-report/account-candidates",
            headers=headers,
        ),
        lambda response: (
            response.status_code == 200 and len(response.json().get("candidates", [])) > 0
        ),
        description="parsed report account candidates available",
    )
    candidates_body = candidates_response.json()
    artifacts.record("import_account_candidates", candidates_body)
    candidate = candidates_body["candidates"][0]
    assert candidate["creditor_name"] == doc.EXPECTED_CREDITOR
    assert candidate["case_id"] == case_id

    account = expect_ok(
        http.post(
            "/api/v1/accounts",
            headers=headers,
            json=_candidate_to_account_payload(candidate),
        ),
        label="import_create_account",
        artifacts=artifacts,
        expected_status=201,
    )
    account_id = account["id"]
    assert account["creditor_name"] == doc.EXPECTED_CREDITOR
    assert account["account_number_masked"] == doc.EXPECTED_ACCOUNT_MASKED

    run_dispute_letter_lifecycle(
        http,
        headers,
        account_id,
        expected_creditor=doc.EXPECTED_CREDITOR,
        artifacts=artifacts,
        label_prefix="import_",
    )
