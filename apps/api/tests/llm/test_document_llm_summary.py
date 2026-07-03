"""LLM document summary endpoint tests."""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from verdin_llm_gateway import LlmCompletionResult, get_llm_settings

from api.core.feature_flags import get_feature_flags
from tests.documents.conftest import sample_pdf_upload


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
def mock_llm_client(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    completion = LlmCompletionResult(
        content="Document is a credit report with two tradelines flagged for dispute review.",
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
    return AsyncMock(return_value=completion)


def _create_case(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": "LLM Document Case", "client_name": "Doc Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


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


def test_generate_document_llm_summary(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_env: None,
    mock_llm_client: None,
) -> None:
    case_id = _create_case(api_client, manager_headers)
    document_id = _upload_document(api_client, manager_headers, case_id)
    response = api_client.post(
        f"/api/v1/documents/{document_id}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["document_id"] == document_id
    assert "dispute review" in payload["summary"]
    assert payload["model"] == "gpt-4o-mini"
    assert payload["provider"] == "openai"
    assert len(payload["prompt_hash"]) == 64
    assert payload["pii_scrubbed"] is True


def test_generate_document_llm_summary_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    llm_env: None,
    mock_llm_client: None,
) -> None:
    case_id = _create_case(api_client, manager_headers)
    document_id = _upload_document(api_client, manager_headers, case_id)
    response = api_client.post(
        f"/api/v1/documents/{document_id}/llm-summary",
        headers=readonly_headers,
    )
    assert response.status_code == 403


def test_generate_document_llm_summary_blocked_when_llm_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()

    case_id = _create_case(api_client, manager_headers)
    document_id = _upload_document(api_client, manager_headers, case_id)
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
