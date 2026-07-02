"""Email delivery scaffold status endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.email_delivery import get_email_delivery_settings
from api.core.feature_flags import get_feature_flags


@pytest.fixture
def email_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_EMAIL_DELIVERY", "true")
    monkeypatch.setenv("EMAIL_PROVIDER", "smtp")
    monkeypatch.setenv("EMAIL_FROM_ADDRESS", "no-reply@verdin.example")
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.verdin.example")
    get_feature_flags.cache_clear()
    get_email_delivery_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_email_delivery_settings.cache_clear()


def test_email_status_ready_when_configured(
    api_client: TestClient,
    manager_headers: dict[str, str],
    email_env: None,
) -> None:
    response = api_client.get("/api/v1/notifications/email/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["provider"] == "smtp"
    assert payload["from_address"] == "no-reply@verdin.example"
    assert payload["blockers"] == []


def test_email_status_blocked_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_EMAIL_DELIVERY", "false")
    monkeypatch.setenv("EMAIL_PROVIDER", "none")
    monkeypatch.delenv("EMAIL_FROM_ADDRESS", raising=False)
    get_feature_flags.cache_clear()
    get_email_delivery_settings.cache_clear()

    response = api_client.get("/api/v1/notifications/email/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["ready"] is False
    assert "ENABLE_EMAIL_DELIVERY is false" in payload["blockers"]
