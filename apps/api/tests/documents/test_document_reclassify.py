"""Operator async document re-classify enqueue tests."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import get_settings
from api.core.job_queue import JobMessage, JobType
from api.modules.documents.models import Document
from tests.documents.conftest import sample_pdf_upload
from tests.documents.test_metadata_extraction import SAMPLE_CREDIT_REPORT_TEXT


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(
        job_type=job_type,
        payload=payload or {},
        job_id="test-reclassify-job",
    )


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
        data={"title": "Reclassify Test", "case_id": sample_case_id},
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


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_reclassify_enqueues_job(
    mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
) -> None:
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/classify/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == document_with_ocr
    assert data["job_id"] == "test-reclassify-job"
    assert data["job_type"] == JobType.DOCUMENT_CLASSIFY.value
    assert data["queued"] is True
    mock_enqueue.assert_any_call(
        JobType.DOCUMENT_CLASSIFY,
        {"document_id": document_with_ocr},
    )


def test_reclassify_requires_ocr_text(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "No OCR", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/documents/{document_id}/classify/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 422
    assert "OCR text" in response.json()["detail"]


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_reclassify_returns_503_when_disabled(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "document_classification_enabled", False)

    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/classify/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 503
    assert "classification is disabled" in response.json()["detail"]
