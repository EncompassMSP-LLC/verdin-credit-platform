"""Case-level bulk OCR retry tests."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import get_settings
from api.core.job_queue import JobMessage, JobType
from api.modules.documents.models import Document
from tests.documents.conftest import sample_pdf_upload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(
        job_type=job_type,
        payload=payload or {},
        job_id="test-bulk-ocr-retry-job-id-36ch",
    )


@pytest.fixture
async def case_with_mixed_ocr_status(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> dict[str, str]:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Failed OCR", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert create.status_code == 201, create.text
    failed_id = uuid.UUID(create.json()["id"])
    failed = await db_session.get(Document, failed_id)
    assert failed is not None
    failed.processing_status = "failed"
    failed.ocr_error = "boom"
    failed.ocr_text = None

    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Completed OCR", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    completed_id = uuid.UUID(create.json()["id"])
    completed = await db_session.get(Document, completed_id)
    assert completed is not None
    completed.processing_status = "completed"
    completed.ocr_text = "sample text"

    await db_session.commit()
    return {
        "case_id": sample_case_id,
        "failed": str(failed_id),
        "completed": str(completed_id),
    }


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_bulk_ocr_retry_queues_failed_and_skips_not_failed(
    mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_with_mixed_ocr_status: dict[str, str],
) -> None:
    case_id = case_with_mixed_ocr_status["case_id"]
    response = api_client.post(
        f"/api/v1/cases/{case_id}/ocr/retry",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["case_id"] == case_id
    assert data["queued_count"] == 1
    assert data["skipped_count"] >= 1
    queued_ids = {item["document_id"] for item in data["queued"]}
    assert queued_ids == {case_with_mixed_ocr_status["failed"]}
    skip_by_id = {item["document_id"]: item["reason"] for item in data["skipped"]}
    assert skip_by_id[case_with_mixed_ocr_status["completed"]] == "not_failed"
    mock_enqueue.assert_any_call(
        JobType.OCR,
        {
            "document_id": case_with_mixed_ocr_status["failed"],
            "version_number": 1,
        },
    )


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_bulk_ocr_retry_returns_503_when_disabled(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_with_mixed_ocr_status: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "document_ocr_enabled", False)

    response = api_client.post(
        f"/api/v1/cases/{case_with_mixed_ocr_status['case_id']}/ocr/retry",
        headers=manager_headers,
    )
    assert response.status_code == 503
    assert "OCR is disabled" in response.json()["detail"]
