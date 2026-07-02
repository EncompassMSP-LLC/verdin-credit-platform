"""Production email delivery tests."""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from api.core.email_delivery import EmailSendResult, get_email_delivery_settings
from api.core.feature_flags import get_feature_flags
from api.modules.auth.models import User


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


@pytest.fixture
def mock_send_email(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(
        return_value=EmailSendResult(success=True, provider_message_id="provider-msg-1"),
    )
    monkeypatch.setattr("api.modules.notifications.service.send_email_message", mock)
    return mock


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


def test_send_email_creates_audit_log(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    email_env: None,
    mock_send_email: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/email/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "subject": "Case update",
            "body": "Your case was updated.",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["status"] == "sent"
    assert payload["provider"] == "smtp"
    assert payload["recipient_email"] == case_manager_user.email
    assert payload["provider_message_id"] == "provider-msg-1"
    mock_send_email.assert_awaited_once()


def test_send_email_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_user: User,
    email_env: None,
    mock_send_email: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/email/send",
        headers=manager_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "subject": "Blocked",
            "body": "Should not send",
        },
    )
    assert response.status_code == 403
    mock_send_email.assert_not_awaited()


def test_send_email_not_ready_returns_503(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_EMAIL_DELIVERY", "false")
    get_feature_flags.cache_clear()
    get_email_delivery_settings.cache_clear()

    response = api_client.post(
        "/api/v1/notifications/email/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "subject": "Blocked",
            "body": "Should not send",
        },
    )
    assert response.status_code == 503


def test_create_notification_with_deliver_email(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    email_env: None,
    mock_send_email: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "title": "Email-backed alert",
            "body": "Please review the case.",
            "deliver_email": True,
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["title"] == "Email-backed alert"
    assert payload["email_delivery"]["attempted"] is True
    assert payload["email_delivery"]["status"] == "sent"
    assert payload["email_delivery"]["delivery_log_id"] is not None
    mock_send_email.assert_awaited_once()


def test_list_email_deliveries(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    email_env: None,
    mock_send_email: AsyncMock,
) -> None:
    api_client.post(
        "/api/v1/notifications/email/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "subject": "Audit trail",
            "body": "Logged delivery",
        },
    )

    response = api_client.get("/api/v1/notifications/email/deliveries", headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] >= 1
    assert any(item["subject"] == "Audit trail" for item in data["items"])


def test_send_email_provider_failure_records_failed_audit_log(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    email_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock = AsyncMock(return_value=EmailSendResult(success=False, error="SMTP rejected"))
    monkeypatch.setattr("api.modules.notifications.service.send_email_message", mock)

    response = api_client.post(
        "/api/v1/notifications/email/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "subject": "Failure case",
            "body": "Should fail at provider",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["error_message"] == "SMTP rejected"

    deliveries = api_client.get("/api/v1/notifications/email/deliveries", headers=admin_headers)
    assert deliveries.status_code == 200
    assert any(item["status"] == "failed" for item in deliveries.json()["items"])


def test_send_email_rejects_unknown_recipient(
    api_client: TestClient,
    admin_headers: dict[str, str],
    email_env: None,
    mock_send_email: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/email/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(uuid.uuid4()),
            "subject": "Missing user",
            "body": "No recipient",
        },
    )
    assert response.status_code == 404
    mock_send_email.assert_not_awaited()
