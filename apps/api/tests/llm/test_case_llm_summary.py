"""LLM case summary endpoint tests."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from verdin_llm_gateway import LlmCompletionResult, get_llm_settings

from api.core.feature_flags import get_feature_flags


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
        content="Case is in intake with two tradelines ready for dispute review.",
        model="gpt-4o-mini",
        provider="openai",
    )

    class StubLlmClient:
        async def complete(self, *_args: object, **_kwargs: object) -> LlmCompletionResult:
            return completion

    monkeypatch.setattr(
        "api.modules.cases.llm_summary.get_llm_completion_client",
        lambda *_args, **_kwargs: StubLlmClient(),
    )
    return AsyncMock(return_value=completion)


def _create_case(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": "LLM Summary Case", "client_name": "Summary Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_generate_case_llm_summary(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_env: None,
    mock_llm_client: None,
) -> None:
    case_id = _create_case(api_client, manager_headers)
    response = api_client.post(
        f"/api/v1/cases/{case_id}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["case_id"] == case_id
    assert "dispute review" in payload["summary"]
    assert payload["model"] == "gpt-4o-mini"
    assert payload["provider"] == "openai"
    assert len(payload["prompt_hash"]) == 64
    assert payload["pii_scrubbed"] is True


def test_generate_case_llm_summary_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    llm_env: None,
    mock_llm_client: None,
) -> None:
    case_id = _create_case(api_client, manager_headers)
    response = api_client.post(
        f"/api/v1/cases/{case_id}/llm-summary",
        headers=readonly_headers,
    )
    assert response.status_code == 403


def test_generate_case_llm_summary_blocked_when_llm_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()

    case_id = _create_case(api_client, manager_headers)
    response = api_client.post(
        f"/api/v1/cases/{case_id}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 503
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()


def test_generate_case_llm_summary_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_env: None,
) -> None:
    import uuid

    response = api_client.post(
        f"/api/v1/cases/{uuid.uuid4()}/llm-summary",
        headers=manager_headers,
    )
    assert response.status_code == 404
