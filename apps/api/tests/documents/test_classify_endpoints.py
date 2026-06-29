"""Document classification integration tests."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_document_classification import ClassificationContext, classify_document
from verdin_document_classification.constants import DocumentType

from api.core.job_queue import JobMessage, JobType
from api.modules.documents.models import Document
from tests.documents.conftest import sample_pdf_upload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(job_type=job_type, payload=payload or {}, job_id="test-job")


async def _set_document_ocr_text(
    db_session: AsyncSession,
    document_id: str,
    ocr_text: str,
) -> None:
    document = await db_session.get(Document, uuid.UUID(document_id))
    assert document is not None
    document.ocr_text = ocr_text
    document.processing_status = "completed"
    await db_session.commit()


@pytest.mark.asyncio
async def test_manual_classification_endpoint(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Bureau Pull", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    await _set_document_ocr_text(
        db_session,
        document_id,
        "EQUIFAX consumer credit report tradeline fico score",
    )

    response = api_client.post(
        f"/api/v1/documents/{document_id}/classification",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_type"] == "credit_report"
    assert data["classification_method"] == "rules"
    assert data["confidence_score"] is not None
    assert data["classified_at"] is not None


@pytest.mark.asyncio
async def test_reclassify_endpoint(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Utility", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    await _set_document_ocr_text(
        db_session,
        document_id,
        "utility bill electric service period meter reading kwh",
    )

    api_client.post(
        f"/api/v1/documents/{document_id}/classification",
        headers=manager_headers,
    )
    response = api_client.post(
        f"/api/v1/documents/{document_id}/classification/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.json()["document_type"] == "utility_bill"


@pytest.mark.asyncio
async def test_classification_metadata_persists(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Collector", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]
    await _set_document_ocr_text(
        db_session,
        document_id,
        "This is an attempt to collect a debt. Amount due immediately.",
    )

    api_client.post(
        f"/api/v1/documents/{document_id}/classification",
        headers=manager_headers,
    )
    get_doc = api_client.get(f"/api/v1/documents/{document_id}", headers=manager_headers)
    assert get_doc.json()["document_type"] == "collection_letter"

    get_class = api_client.get(
        f"/api/v1/documents/{document_id}/classification",
        headers=manager_headers,
    )
    assert get_class.json()["document_type"] == "collection_letter"


def test_unknown_document_fallback() -> None:
    context = ClassificationContext(
        ocr_text="lorem ipsum dolor sit amet",
        file_name="notes.pdf",
        title="Misc",
        mime_type="application/pdf",
    )
    result = classify_document(context)
    assert result.document_type == DocumentType.UNKNOWN
    assert result.confidence_score <= 0.2


def test_highest_confidence_classifier_wins() -> None:
    context = ClassificationContext(
        ocr_text=(
            "EQUIFAX consumer credit report tradeline fico score "
            "collection agency amount due validation of debt"
        ),
        file_name="mixed.pdf",
        title="Mixed signals",
        mime_type="application/pdf",
    )
    result = classify_document(context)
    assert result.document_type == DocumentType.CREDIT_REPORT
    assert result.confidence_score >= 0.5


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_list_documents_filter_by_document_type(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    credit = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={
            "title": "Equifax consumer credit report tradeline",
            "case_id": sample_case_id,
        },
        files={"file": (filename, file_obj, content_type)},
    )
    credit_id = credit.json()["id"]
    api_client.post(
        f"/api/v1/documents/{credit_id}/classification",
        headers=manager_headers,
    )

    other = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Random misc", "case_id": sample_case_id},
        files={"file": ("other.pdf", b"%PDF other", "application/pdf")},
    )
    other_id = other.json()["id"]
    api_client.post(
        f"/api/v1/documents/{other_id}/classification",
        headers=manager_headers,
    )

    response = api_client.get(
        "/api/v1/documents?document_type=credit_report",
        headers=manager_headers,
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["document_type"] == "credit_report"
