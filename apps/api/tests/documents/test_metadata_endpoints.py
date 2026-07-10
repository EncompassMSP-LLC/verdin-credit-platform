"""Document metadata and entity resolution endpoint tests."""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.models import Document
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from tests.accounts.conftest import sample_account_payload
from tests.documents.conftest import sample_pdf_upload
from tests.documents.test_metadata_extraction import SAMPLE_CREDIT_REPORT_TEXT


@pytest.fixture
async def document_with_ocr(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> str:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Metadata Test", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert create.status_code == 201, create.text
    document_id = uuid.UUID(create.json()["id"])

    document = await db_session.get(Document, document_id)
    assert document is not None
    document.ocr_text = SAMPLE_CREDIT_REPORT_TEXT
    document.processing_status = "completed"
    await db_session.commit()
    return str(document_id)


def test_extract_metadata_persists_fields(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["consumer_name"] == "Doc Client"
    assert data["creditor"] == "Example Bank"
    assert data["bureau"] == "equifax"
    assert data["metadata_status"] == "extracted"
    assert data["confidence_score"] > 0


def test_get_metadata_after_extract(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    response = api_client.get(
        f"/api/v1/documents/{document_with_ocr}/metadata",
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.json()["account_number_masked"] == "****1234"


def test_get_document_includes_metadata_status_after_extract(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    response = api_client.get(
        f"/api/v1/documents/{document_with_ocr}",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["metadata_status"] == "extracted"


def test_get_parsed_credit_report_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    response = api_client.get(
        f"/api/v1/documents/{document_with_ocr}/parsed-credit-report",
        headers=manager_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Parsed credit report not found"


async def test_get_parsed_credit_report(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
    db_session: AsyncSession,
) -> None:
    document_id = uuid.UUID(document_with_ocr)
    document = await db_session.get(Document, document_id)
    assert document is not None

    now = datetime.now(UTC)
    parsed = DocumentParsedCreditReport(
        id=uuid.uuid4(),
        document_id=document.id,
        organization_id=document.organization_id,
        schema_version="1.0",
        bureau="equifax",
        parser_name="equifax",
        parser_confidence=0.98,
        parsed_report={
            "schema_version": "1.0",
            "bureau": "equifax",
            "accounts": [{"creditor_name": "Example Bank"}],
        },
        is_partial=False,
        warnings=[],
        parsed_at=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(parsed)
    await db_session.commit()

    response = api_client.get(
        f"/api/v1/documents/{document_with_ocr}/parsed-credit-report",
        headers=manager_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == document_with_ocr
    assert data["bureau"] == "equifax"
    assert data["parser_name"] == "equifax"
    assert data["parser_confidence"] == 0.98
    assert data["parsed_report"]["accounts"][0]["creditor_name"] == "Example Bank"
    assert data["is_partial"] is False
    assert data["warnings"] == []


def test_resolve_entities_matched_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    document_with_ocr: str,
) -> None:
    account = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    assert account.status_code == 201

    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/resolve",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    resolutions = response.json()["resolutions"]
    account_resolution = next(row for row in resolutions if row["entity_type"] == "account")
    assert account_resolution["resolution_status"] == "matched"
    assert account_resolution["matched_entity_id"] is not None


def test_resolve_entities_unmatched_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/resolve",
        headers=manager_headers,
    )
    assert response.status_code == 200
    account_resolution = next(
        row for row in response.json()["resolutions"] if row["entity_type"] == "account"
    )
    assert account_resolution["resolution_status"] == "unmatched"


def test_confirm_ambiguous_resolution(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    document_with_ocr: str,
) -> None:
    first = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    second_payload = sample_account_payload(sample_case_id)
    second_payload["creditor_name"] = "Example Bank NA"
    second = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=second_payload,
    )
    assert first.status_code == 201 and second.status_code == 201

    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    resolved = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/resolve",
        headers=manager_headers,
    )
    account_resolution = next(
        row for row in resolved.json()["resolutions"] if row["entity_type"] == "account"
    )
    assert account_resolution["resolution_status"] == "ambiguous"
    candidate_id = account_resolution["candidate_entity_ids"][0]

    confirm = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/{account_resolution['id']}/confirm",
        headers=manager_headers,
        json={"matched_entity_id": candidate_id},
    )
    assert confirm.status_code == 200
    confirmed = next(
        row for row in confirm.json()["resolutions"] if row["entity_type"] == "account"
    )
    assert confirmed["resolution_status"] == "confirmed"
    assert confirmed["matched_entity_id"] == candidate_id


def test_reject_resolution(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    document_with_ocr: str,
) -> None:
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    resolved = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/resolve",
        headers=manager_headers,
    )
    account_resolution = next(
        row for row in resolved.json()["resolutions"] if row["entity_type"] == "account"
    )

    reject = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/resolutions/{account_resolution['id']}/reject",
        headers=manager_headers,
        json={"reason": "Incorrect match"},
    )
    assert reject.status_code == 200
    rejected = next(row for row in reject.json()["resolutions"] if row["entity_type"] == "account")
    assert rejected["resolution_status"] == "rejected"
    assert rejected["matched_entity_id"] is None


def test_list_documents_metadata_status_filter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    api_client.post(
        f"/api/v1/documents/{document_with_ocr}/metadata/extract",
        headers=manager_headers,
    )
    response = api_client.get(
        "/api/v1/documents",
        headers=manager_headers,
        params={"metadata_status": "extracted"},
    )
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert document_with_ocr in ids
