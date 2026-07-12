"""End-to-end validation of the complete case lifecycle.

A single automated test exercises the full customer journey across the running
platform and serves as the Sprint 4.3.1 release gate:

    Organization → User → Authenticate → Case → Account → Document Upload
    → OCR → Classification → Metadata → Entity Resolution → Timeline
    → Task → Mission Control dashboard

The organization and owner user are seeded directly in the database; every
other step goes through the HTTP API, and the asynchronous document pipeline is
driven by the real worker process.
"""

from __future__ import annotations

import httpx

from tests.e2e.fixtures import documents as doc
from tests.e2e.fixtures.organization import OrganizationRecord
from tests.e2e.fixtures.users import UserRecord
from tests.e2e.helpers import auth
from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.assertions import expect_ok
from tests.e2e.helpers.wait_for_worker import poll_until


def test_full_case_lifecycle(
    http: httpx.Client,
    owner: UserRecord,
    organization: OrganizationRecord,
    artifacts: ArtifactCollector,
) -> None:
    # ---------------------------------------------------------------- Stage 1
    # Authentication: login, inspect identity/permissions, refresh, reuse.
    tokens = auth.login(http, owner.email, owner.password)
    artifacts.record("stage1_login", {"token_type": tokens.token_type})
    assert tokens.access_token and tokens.refresh_token

    me = expect_ok(
        http.get("/api/v1/auth/me", headers=tokens.headers),
        label="stage1_me",
        artifacts=artifacts,
    )
    assert me["email"] == owner.email
    assert me["role"] == owner.role

    refreshed = auth.refresh(http, tokens.refresh_token)
    headers = refreshed.headers
    expect_ok(
        http.get("/api/v1/auth/me", headers=headers),
        label="stage1_me_after_refresh",
        artifacts=artifacts,
    )

    # Baseline dashboard counts for this freshly-seeded organization.
    baseline = expect_ok(
        http.get("/api/v1/dashboard", headers=headers),
        label="stage1_dashboard_baseline",
        artifacts=artifacts,
    )

    # ---------------------------------------------------------------- Stage 2
    # Case creation.
    case = expect_ok(
        http.post("/api/v1/cases", headers=headers, json=doc.CASE_PAYLOAD),
        label="stage2_case",
        artifacts=artifacts,
        expected_status=201,
    )
    case_id = case["id"]
    assert case["title"] == doc.CASE_PAYLOAD["title"]

    # ---------------------------------------------------------------- Stage 3
    # Account creation linked to the case; dashboard account count increases.
    account_payload = {**doc.ACCOUNT_PAYLOAD, "case_id": case_id}
    account = expect_ok(
        http.post("/api/v1/accounts", headers=headers, json=account_payload),
        label="stage3_account",
        artifacts=artifacts,
        expected_status=201,
    )
    account_id = account["id"]
    assert account["case_id"] == case_id
    assert account["creditor_name"] == doc.EXPECTED_CREDITOR

    after_account = expect_ok(
        http.get("/api/v1/dashboard", headers=headers),
        label="stage3_dashboard",
        artifacts=artifacts,
    )
    assert after_account["accounts"]["total"] > baseline["accounts"]["total"]

    # ---------------------------------------------------------------- Stage 4
    # Document upload (no explicit account link — entity resolution will link).
    pdf_bytes = doc.build_credit_report_pdf()
    upload = expect_ok(
        http.post(
            "/api/v1/documents",
            headers=headers,
            data={"title": doc.DOCUMENT_TITLE, "case_id": case_id},
            files={"file": (doc.DOCUMENT_FILENAME, pdf_bytes, doc.DOCUMENT_MIME_TYPE)},
        ),
        label="stage4_upload",
        artifacts=artifacts,
        expected_status=201,
    )
    document_id = upload["id"]
    assert upload["mime_type"] == doc.DOCUMENT_MIME_TYPE
    assert upload["version_number"] == 1
    assert upload["processing_status"] in {"queued", "pending", "processing"}

    versions_response = http.get(
        f"/api/v1/documents/{document_id}/versions", headers=headers
    )
    versions_list = versions_response.json()
    artifacts.record(
        "stage4_versions",
        {"status_code": versions_response.status_code, "versions": versions_list},
    )
    assert versions_response.status_code == 200
    assert isinstance(versions_list, list) and len(versions_list) == 1
    assert versions_list[0]["version_number"] == 1

    # The stored object must be retrievable (proves MinIO persistence).
    download = http.get(f"/api/v1/documents/{document_id}/download", headers=headers)
    artifacts.record(
        "stage4_download",
        {"status_code": download.status_code, "bytes": len(download.content)},
    )
    assert download.status_code == 200
    assert download.content == pdf_bytes

    # ---------------------------------------------------------------- Stage 5
    # OCR — poll until the worker completes extraction.
    def fetch_ocr() -> httpx.Response:
        return http.get(f"/api/v1/documents/{document_id}/ocr", headers=headers)

    ocr_response = poll_until(
        fetch_ocr,
        lambda r: (
            r.status_code == 200 and r.json().get("processing_status") == "completed"
        ),
        description="document OCR processing_status == completed",
    )
    ocr_body = ocr_response.json()
    artifacts.record("stage5_ocr", ocr_body)
    assert ocr_body["ocr_text"], "OCR produced no text"
    assert "equifax" in ocr_body["ocr_text"].lower()

    # ---------------------------------------------------------------- Stage 6
    # Classification — worker classifies after OCR.
    def fetch_classification() -> httpx.Response:
        return http.get(
            f"/api/v1/documents/{document_id}/classification", headers=headers
        )

    classification_response = poll_until(
        fetch_classification,
        lambda r: r.status_code == 200 and r.json().get("document_type") is not None,
        description="document classification completed",
    )
    classification = classification_response.json()
    artifacts.record("stage6_classification", classification)
    assert classification["document_type"] == doc.EXPECTED_DOCUMENT_TYPE
    assert classification["confidence_score"] is not None
    assert classification["confidence_score"] > 0
    assert classification["classified_at"] is not None

    # ---------------------------------------------------------------- Stage 7
    # Metadata extraction — /metadata 404s until the worker has extracted it.
    def fetch_metadata() -> httpx.Response:
        return http.get(f"/api/v1/documents/{document_id}/metadata", headers=headers)

    metadata_response = poll_until(
        fetch_metadata,
        lambda r: (
            r.status_code == 200 and r.json().get("metadata_status") == "extracted"
        ),
        description="document metadata extracted",
    )
    metadata = metadata_response.json()
    artifacts.record("stage7_metadata", metadata)
    assert metadata["creditor"] == doc.EXPECTED_CREDITOR
    assert metadata["bureau"] == doc.EXPECTED_BUREAU
    assert metadata["account_number_masked"] == doc.EXPECTED_ACCOUNT_MASKED
    assert metadata["report_date"] == doc.EXPECTED_REPORT_DATE

    # ---------------------------------------------------------------- Stage 7b
    # Parsed report — structured parser output must be persisted for UI review.
    parsed_report = expect_ok(
        http.get(
            f"/api/v1/documents/{document_id}/parsed-credit-report",
            headers=headers,
        ),
        label="stage7b_parsed_credit_report",
        artifacts=artifacts,
    )
    assert parsed_report["bureau"] == doc.EXPECTED_BUREAU
    assert parsed_report["parser_name"] == doc.EXPECTED_BUREAU
    assert parsed_report["schema_version"] == "1.1"
    assert parsed_report["is_partial"] is False
    assert parsed_report["parser_confidence"] > 0
    accounts = parsed_report["parsed_report"]["accounts"]
    assert len(accounts) == 1
    assert accounts[0]["creditor_name"] == doc.EXPECTED_CREDITOR
    assert accounts[0]["account_number_masked"] == doc.EXPECTED_ACCOUNT_MASKED
    assert accounts[0]["balance"] == doc.EXPECTED_BALANCE
    assert accounts[0]["date_reported"] == "05/01/2026"

    # ---------------------------------------------------------------- Stage 8
    # Entity resolution — the account tradeline must match the seeded account.
    def fetch_resolutions() -> httpx.Response:
        return http.get(f"/api/v1/documents/{document_id}/resolutions", headers=headers)

    def account_matched(response: httpx.Response) -> bool:
        if response.status_code != 200:
            return False
        for row in response.json().get("resolutions", []):
            if (
                row["entity_type"] == "account"
                and row["resolution_status"] == "matched"
            ):
                return True
        return False

    resolutions_response = poll_until(
        fetch_resolutions,
        account_matched,
        description="account entity resolution matched",
    )
    resolutions = resolutions_response.json()
    artifacts.record("stage8_resolutions", resolutions)
    account_resolution = next(
        row for row in resolutions["resolutions"] if row["entity_type"] == "account"
    )
    assert account_resolution["matched_entity_id"] == account_id

    # The matched account should now be linked on the document itself.
    linked_document = poll_until(
        lambda: http.get(f"/api/v1/documents/{document_id}", headers=headers),
        lambda r: r.status_code == 200 and r.json().get("account_id") == account_id,
        description="document linked to resolved account",
    ).json()
    artifacts.record("stage8_document_linked", linked_document)
    assert linked_document["account_id"] == account_id

    # ---------------------------------------------------------------- Stage 9
    # Timeline — every pipeline milestone must have produced an event.
    timeline = expect_ok(
        http.get(
            "/api/v1/timeline",
            headers=headers,
            params={"document_id": document_id, "page_size": 100},
        ),
        label="stage9_timeline",
        artifacts=artifacts,
    )
    event_types = {item["event_type"] for item in timeline["items"]}
    artifacts.record("stage9_event_types", sorted(event_types))
    for expected_event in (
        "DOCUMENT_UPLOADED",
        "OCR_COMPLETED",
        "CLASSIFICATION_COMPLETED",
        "METADATA_EXTRACTED",
        "ENTITY_RESOLVED",
    ):
        assert expected_event in event_types, (
            f"missing timeline event: {expected_event}"
        )

    # --------------------------------------------------------------- Stage 10
    # Task creation.
    task_payload = {
        "title": "Review resolved tradeline",
        "description": "Confirm the matched account and prepare dispute review.",
        "priority": "high",
        "case_id": case_id,
        "account_id": account_id,
        "document_id": document_id,
    }
    task = expect_ok(
        http.post("/api/v1/tasks", headers=headers, json=task_payload),
        label="stage10_task",
        artifacts=artifacts,
        expected_status=201,
    )
    assert task["case_id"] == case_id
    assert task["status"] == "open"

    # --------------------------------------------------------------- Stage 11
    # Mission Control reflects the new operational state.
    dashboard = expect_ok(
        http.get("/api/v1/dashboard", headers=headers),
        label="stage11_mission_control",
        artifacts=artifacts,
    )
    overview = dashboard["overview"]
    assert overview["open_cases"] >= 1
    assert overview["documents"] >= 1
    assert overview["active_accounts"] >= 1

    assert dashboard["cases"]["open"] >= 1
    assert dashboard["documents"]["total"] >= 1
    assert dashboard["tasks"]["pending"] >= 1

    assert isinstance(dashboard["timeline"], list) and len(dashboard["timeline"]) >= 1

    alerts = dashboard["alerts"]
    assert alerts["total"] == len(alerts["items"])
