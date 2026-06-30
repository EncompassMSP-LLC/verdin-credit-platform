"""OCR pipeline endpoint tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.core.job_queue import JobMessage, JobType
from tests.documents.conftest import sample_pdf_upload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(job_type=job_type, payload=payload or {}, job_id="test-ocr-job")


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_upload_queues_ocr_for_pdf(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    response = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "OCR PDF", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["processing_status"] == "queued"
    assert data["mime_type"] == "application/pdf"


def test_upload_skips_ocr_for_text_file(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Notes", "case_id": sample_case_id},
        files={"file": ("notes.txt", b"plain notes", "text/plain")},
    )
    assert response.status_code == 201, response.text
    assert response.json()["processing_status"] == "skipped"


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_get_ocr_result(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "OCR Detail", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/documents/{document_id}/ocr",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == document_id
    assert data["processing_status"] == "queued"
    assert data["ocr_text"] is None


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_retry_ocr(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Retry OCR", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/documents/{document_id}/ocr/retry",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["processing_status"] == "queued"
