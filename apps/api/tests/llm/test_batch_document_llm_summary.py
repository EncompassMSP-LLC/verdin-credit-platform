"""Batch document LLM summary tests."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.job_queue import JobType
from api.modules.documents.batch_summary_models import BatchSummaryRunStatus


@pytest.fixture
def batch_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("ENABLE_BATCH_LLM_SUMMARIES", "true")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "gpt-test")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def document_id(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> str:
    case_response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Batch LLM Case", "client_name": "Batch Client"},
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    from tests.documents.conftest import sample_pdf_upload

    filename, file_obj, content_type = sample_pdf_upload()
    document_response = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Batch Summary Document", "case_id": case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert document_response.status_code == 201, document_response.text
    return document_response.json()["id"]


def test_batch_summary_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/documents/batch-llm-summaries/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_batch_summary_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    batch_llm_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/documents/batch-llm-summaries/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["blockers"] == []


@patch("api.modules.documents.batch_summary_service.enqueue_job")
def test_enqueue_batch_summary_run(
    mock_enqueue,
    api_client: TestClient,
    manager_headers: dict[str, str],
    batch_llm_env: None,
    document_id: str,
) -> None:
    mock_enqueue.return_value = type("Msg", (), {"job_id": "job-batch-1"})()

    response = api_client.post(
        "/api/v1/documents/batch-llm-summaries/run",
        headers=manager_headers,
        json={"document_ids": [document_id]},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["job_id"] == "job-batch-1"
    assert payload["run"]["status"] == BatchSummaryRunStatus.PENDING.value
    assert payload["run"]["documents_queued"] == 1
    mock_enqueue.assert_called_once()
    args = mock_enqueue.call_args
    assert args[0][0] is JobType.BATCH_DOCUMENT_LLM_SUMMARY


def test_enqueue_batch_summary_requires_write_role(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    batch_llm_env: None,
    document_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/documents/batch-llm-summaries/run",
        headers=readonly_headers,
        json={"document_ids": [document_id]},
    )
    assert response.status_code == 403


def test_enqueue_batch_summary_unknown_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    batch_llm_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/documents/batch-llm-summaries/run",
        headers=manager_headers,
        json={"document_ids": [str(uuid.uuid4())]},
    )
    assert response.status_code == 404
