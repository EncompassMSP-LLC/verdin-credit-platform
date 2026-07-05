"""LLM dispute draft augment endpoint tests."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from verdin_llm_gateway import LlmCompletionResult, get_llm_settings

from api.core.feature_flags import get_feature_flags
from tests.llm.conftest import sample_account_payload


@pytest.fixture
def llm_dispute_augment_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("ENABLE_LLM_DISPUTE_DRAFT_AUGMENT", "true")
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
        content="Revised dispute letter body with clearer verification request.",
        model="gpt-4o-mini",
        provider="openai",
    )

    class StubLlmClient:
        async def complete(self, *_args: object, **_kwargs: object) -> LlmCompletionResult:
            return completion

    monkeypatch.setattr(
        "api.modules.accounts.dispute_draft_augment_service.get_llm_completion_client",
        lambda *_args, **_kwargs: StubLlmClient(),
    )
    return AsyncMock(return_value=completion)


def _create_account(
    api_client: TestClient,
    headers: dict[str, str],
    sample_case_id: str,
) -> str:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json=sample_account_payload(sample_case_id),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_dispute_draft_augment_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("ENABLE_LLM_DISPUTE_DRAFT_AUGMENT", "false")
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()
    response = api_client.get("/api/v1/llm/dispute-draft/status", headers=manager_headers)
    assert response.status_code == 404
    get_feature_flags.cache_clear()
    get_llm_settings.cache_clear()


def test_dispute_draft_augment_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_dispute_augment_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/dispute-draft/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["llm_ready"] is True
    assert payload["blockers"] == []


def test_create_dispute_draft_llm_augment(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    llm_dispute_augment_env: None,
    mock_llm_client: None,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/llm-augment",
        headers=manager_headers,
        json={"recipient_type": "credit_bureau"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["account_id"] == account_id
    assert payload["status"] == "completed"
    assert "Revised dispute letter body" in payload["augmented_body"]
    assert payload["model"] == "gpt-4o-mini"
    assert payload["pii_scrubbed"] is True


def test_create_dispute_draft_llm_augment_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
    llm_dispute_augment_env: None,
    mock_llm_client: None,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/llm-augment",
        headers=readonly_headers,
        json={"recipient_type": "credit_bureau"},
    )
    assert response.status_code == 403


def test_list_dispute_draft_llm_augments(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    llm_dispute_augment_env: None,
    mock_llm_client: None,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)
    create = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/llm-augment",
        headers=manager_headers,
        json={"recipient_type": "credit_bureau"},
    )
    assert create.status_code == 200, create.text

    listing = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-draft/llm-augments",
        headers=manager_headers,
    )
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["account_id"] == account_id
