"""LLM document summary endpoint tests."""

import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_llm_gateway import LlmCompletionResult, get_llm_settings

from api.core.feature_flags import get_feature_flags
from api.core.job_queue import JobMessage, JobType
from api.modules.documents.models import Document
from tests.documents.conftest import sample_pdf_upload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(job_type=job_type, payload=payload or {}, job_id="test-ocr-job")


@pytest.fixture(autouse=True)
def mock_ocr_enqueue() -> Generator[None]:
    with patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue):
        yield


@pytest.fixture(autouse=True)
def memory_storage() -> Generator[None]:
    from api.modules.documents.storage import (
        MemoryDocumentStorage,
        reset_document_storage,
        set_document_storage,
    )

    storage = MemoryDocumentStorage()
    reset_document_storage()
    set_document_storage(storage)
    yield
    reset_document_storage()


@pytest.fixture
def llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()


@pytest.fixture
def mock_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    completion = LlmCompletionResult(
        content="Credit report document with one tradeline ready for staff review.",
        model="gpt-4o-mini",
        provider="openai",
    )

    class StubLlmClient:
        async def complete(self, *_args: object, **_kwargs: object) -> LlmCompletionResult:
            return completion

    monkeypatch.setattr(
        "api.modules.documents.llm_summary.get_llm_completion_client",
        lambda *_args, **_kwargs: StubLlmClient(),
    )


def _upload_document(api_client: TestClient, headers: dict[str, str], case_id: str) -> str:
    filename, file_obj, content_type = sample_pdf_upload()
    response = api_client.post(
        "/api/v1/documents",
        headers=headers,
        data={"title": "LLM Summary Document", "case_id": case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def sample_case_id(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Document LLM Case", "client_name": "Doc Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
async def document_with_ocr(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> str:
    document_id = _upload_document(api_client, manager_headers, sample_case_id)
    document = await db_session.get(Document, uuid.UUID(document_id))
    assert document is not None
    document.ocr_text = "Sample OCR text for tradeline ABC Bank."
    await db_session.commit()
    return document_id


def test_generate_document_llm_summary(
    api_client: TestClient,
    manager_headers: dict[str, str],
    document_with_ocr: str,
    llm_env: None,
    mock_llm_client: None,
) -> None:
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["document_id"] == document_with_ocr
    assert "tradeline" in payload["summary"]
    assert payload["model"] == "gpt-4o-mini"
    assert payload["provider"] == "openai"
    assert len(payload["prompt_hash"]) == 64
    assert payload["pii_scrubbed"] is True


def test_generate_document_llm_summary_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    document_with_ocr: str,
    llm_env: None,
    mock_llm_client: None,
) -> None:
    response = api_client.post(
        f"/api/v1/documents/{document_with_ocr}/llm-summary",
        headers=readonly_headers,
    )
    assert response.status_code == 403


def test_generate_document_llm_summary_blocked_when_llm_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()

    document_id = _upload_document(api_client, manager_headers, sample_case_id)
    response = api_client.post(
        f"/api/v1/documents/{document_id}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 503
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()


def test_generate_document_llm_summary_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/documents/{uuid.uuid4()}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 404
