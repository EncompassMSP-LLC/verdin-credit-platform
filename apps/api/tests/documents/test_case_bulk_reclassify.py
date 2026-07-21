"""Case-level bulk document re-classify tests."""

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
        job_id=f"bulk-classify-{payload.get('document_id', 'unknown') if payload else 'unknown'}",
    )


@pytest.fixture
async def case_with_mixed_ocr_documents(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> dict[str, str]:
    eligible_ids: list[str] = []
    for title in ("Experian", "Collection Letter"):
        filename, file_obj, content_type = sample_pdf_upload()
        create = api_client.post(
            "/api/v1/documents",
            headers=manager_headers,
            data={"title": title, "case_id": sample_case_id},
            files={"file": (filename, file_obj, content_type)},
        )
        assert create.status_code == 201, create.text
        document_id = uuid.UUID(create.json()["id"])
        document = await db_session.get(Document, document_id)
        assert document is not None
        document.ocr_text = SAMPLE_CREDIT_REPORT_TEXT
        document.document_type = "credit_report" if title == "Experian" else "collection_letter"
        document.processing_status = "completed"
        eligible_ids.append(str(document_id))

    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "No OCR", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    missing_ocr_id = uuid.UUID(create.json()["id"])
    document = await db_session.get(Document, missing_ocr_id)
    assert document is not None
    document.document_type = "credit_report"
    document.processing_status = "completed"

    await db_session.commit()
    return {
        "case_id": sample_case_id,
        "eligible": eligible_ids,
        "missing_ocr": str(missing_ocr_id),
    }


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_bulk_reclassify_queues_eligible_and_skips_missing_ocr(
    mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_with_mixed_ocr_documents: dict[str, str],
) -> None:
    case_id = case_with_mixed_ocr_documents["case_id"]
    response = api_client.post(
        f"/api/v1/cases/{case_id}/classify/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["case_id"] == case_id
    assert data["queued_count"] == 2
    assert data["skipped_count"] >= 1
    queued_ids = {item["document_id"] for item in data["queued"]}
    assert queued_ids == set(case_with_mixed_ocr_documents["eligible"])
    skip_by_id = {item["document_id"]: item["reason"] for item in data["skipped"]}
    assert skip_by_id[case_with_mixed_ocr_documents["missing_ocr"]] == "missing_ocr"
    assert mock_enqueue.call_count == 2
    for document_id in case_with_mixed_ocr_documents["eligible"]:
        mock_enqueue.assert_any_call(
            JobType.DOCUMENT_CLASSIFY,
            {"document_id": document_id},
        )


@patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue)
def test_bulk_reclassify_returns_503_when_disabled(
    _mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_with_mixed_ocr_documents: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "document_classification_enabled", False)

    response = api_client.post(
        f"/api/v1/cases/{case_with_mixed_ocr_documents['case_id']}/classify/reclassify",
        headers=manager_headers,
    )
    assert response.status_code == 503
    assert "classification is disabled" in response.json()["detail"]
