"""LLM gateway and policy gate tests."""

import pytest
from fastapi.testclient import TestClient
from verdin_llm_gateway import (
    LlmFeatureDisabledError,
    LlmGatewaySettings,
    LlmPiiPolicyError,
    LlmProvider,
    evaluate_llm_gate,
    get_llm_settings,
    redact_pii,
    require_llm_ready,
    scrub_payload,
)

from api.core.feature_flags import FeatureFlag, get_feature_flags, is_feature_enabled
from api.core.llm import get_llm_gate_status, require_llm_gateway


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


def test_evaluate_llm_gate_blocked_when_feature_disabled() -> None:
    settings = LlmGatewaySettings(
        llm_provider=LlmProvider.OPENAI,
        llm_api_key="key",
        llm_model="gpt-4o-mini",
    )
    status = evaluate_llm_gate(feature_enabled=False, settings=settings)
    assert status.ready is False
    assert "ENABLE_LLM is false" in status.blockers


def test_evaluate_llm_gate_blocked_when_provider_missing() -> None:
    settings = LlmGatewaySettings(llm_provider=LlmProvider.NONE)
    status = evaluate_llm_gate(feature_enabled=True, settings=settings)
    assert status.ready is False
    assert "LLM provider credentials or model are not configured" in status.blockers


def test_require_llm_ready_when_configured() -> None:
    settings = LlmGatewaySettings(
        llm_provider=LlmProvider.OPENAI,
        llm_api_key="key",
        llm_model="gpt-4o-mini",
    )
    status = require_llm_ready(feature_enabled=True, settings=settings)
    assert status.ready is True


def test_require_llm_ready_raises_for_pii_without_opt_in() -> None:
    settings = LlmGatewaySettings(
        llm_provider=LlmProvider.OPENAI,
        llm_api_key="key",
        llm_model="gpt-4o-mini",
        llm_allow_external_pii_export=False,
    )
    with pytest.raises(LlmPiiPolicyError):
        require_llm_ready(feature_enabled=True, settings=settings, requires_pii_export=True)


def test_redact_pii_patterns() -> None:
    text = "Contact jane@example.com or 555-123-4567. SSN 123-45-6789."
    redacted = redact_pii(text)
    assert "jane@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "123-45-6789" not in redacted


def test_scrub_payload_removes_known_fields() -> None:
    payload = {
        "client_name": "Jane",
        "email": "jane@example.com",
        "nested": {"phone": "555-123-4567", "note": "Call 555-123-4567"},
    }
    scrubbed = scrub_payload(payload)
    assert scrubbed["email"] == "[REDACTED]"
    assert scrubbed["nested"]["phone"] == "[REDACTED]"
    assert "[REDACTED_PHONE]" in scrubbed["nested"]["note"]


def test_api_llm_wrapper_respects_feature_flag(llm_env: None) -> None:
    assert is_feature_enabled(FeatureFlag.ENABLE_LLM) is True
    status = get_llm_gate_status()
    assert status.ready is True
    require_llm_gateway()


def test_api_llm_wrapper_raises_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_feature_flags.cache_clear()
    with pytest.raises(LlmFeatureDisabledError):
        require_llm_gateway()
    get_feature_flags.cache_clear()


def test_get_llm_status_endpoint(
    api_client: TestClient,
    manager_headers: dict[str, str],
    llm_env: None,
) -> None:
    response = api_client.get("/api/v1/llm/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ready"] is True
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o-mini"


def test_get_llm_status_requires_auth(api_client: TestClient, llm_env: None) -> None:
    response = api_client.get("/api/v1/llm/status")
    assert response.status_code == 401
