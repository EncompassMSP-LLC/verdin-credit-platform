"""LLM account recommendation endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from verdin_llm_gateway import LlmCompletionResult, get_llm_settings

from api.core.feature_flags import get_feature_flags
from tests.accounts.conftest import sample_account_payload


@pytest.fixture
def llm_account_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("ENABLE_LLM_ACCOUNT_RECOMMENDATIONS", "true")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()


@pytest.fixture
def mock_account_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    completion = LlmCompletionResult(
        content="Prepare and send a bureau dispute after confirming tradeline evidence.",
        model="gpt-4o-mini",
        provider="openai",
    )

    class StubLlmClient:
        async def complete(self, *_args: object, **_kwargs: object) -> LlmCompletionResult:
            return completion

    monkeypatch.setattr(
        "api.modules.accounts.account_llm_recommendation.get_llm_completion_client",
        lambda *_args, **_kwargs: StubLlmClient(),
    )


def test_generate_account_llm_recommendation(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    llm_account_env: None,
    mock_account_llm_client: None,
) -> None:
    created = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    assert created.status_code == 201, created.text
    account_id = created.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/llm-recommendation",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["account_id"] == account_id
    assert "bureau dispute" in payload["recommendation"]
    assert payload["model"] == "gpt-4o-mini"
    assert len(payload["prompt_hash"]) == 64

    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert account.status_code == 200
    assert account.json()["ai_recommended_next_action"] == payload["recommendation"]


def test_generate_account_llm_recommendation_disabled_without_flag(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LLM_ACCOUNT_RECOMMENDATIONS", "false")
    get_feature_flags.cache_clear()

    created = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = created.json()["id"]
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/llm-recommendation",
        headers=manager_headers,
    )
    assert response.status_code == 404
