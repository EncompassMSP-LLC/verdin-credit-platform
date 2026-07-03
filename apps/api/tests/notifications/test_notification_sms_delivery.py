"""Production SMS delivery tests."""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.core.sms_delivery import SmsSendResult, get_sms_delivery_settings
from api.modules.auth.models import Organization, User


@pytest.fixture
def sms_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "true")
    monkeypatch.setenv("SMS_PROVIDER", "twilio")
    monkeypatch.setenv("SMS_FROM_NUMBER", "+15555550100")
    monkeypatch.setenv("SMS_TWILIO_ACCOUNT_SID", "ACtest123")
    monkeypatch.setenv("SMS_TWILIO_AUTH_TOKEN", "test-token")
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()


@pytest.fixture
async def case_manager_with_phone(
    db_session: AsyncSession,
    test_org: Organization,
    case_manager_user: User,
) -> User:
    case_manager_user.phone_number = "+15555550123"
    db_session.add(case_manager_user)
    await db_session.commit()
    await db_session.refresh(case_manager_user)
    return case_manager_user


@pytest.fixture
def mock_send_sms(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(
        return_value=SmsSendResult(success=True, provider_message_id="SMtest123"),
    )
    monkeypatch.setattr("api.modules.notifications.service.send_sms_message", mock)
    return mock


def test_sms_status_ready_when_configured(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sms_env: None,
) -> None:
    response = api_client.get("/api/v1/notifications/sms/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["provider"] == "twilio"
    assert payload["from_number"] == "+15555550100"
    assert payload["blockers"] == []


def test_sms_status_blocked_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "false")
    monkeypatch.setenv("SMS_PROVIDER", "none")
    monkeypatch.delenv("SMS_FROM_NUMBER", raising=False)
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()

    response = api_client.get("/api/v1/notifications/sms/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["ready"] is False
    assert "ENABLE_SMS_DELIVERY is false" in payload["blockers"]


def test_send_sms_creates_audit_log(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_with_phone: User,
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_with_phone.id),
            "body": "Your case was updated.",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["status"] == "sent"
    assert payload["provider"] == "twilio"
    assert payload["recipient_phone"] == "+15555550123"
    assert payload["provider_message_id"] == "SMtest123"
    mock_send_sms.assert_awaited_once()


def test_send_sms_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_with_phone: User,
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms/send",
        headers=manager_headers,
        json={
            "recipient_user_id": str(case_manager_with_phone.id),
            "body": "Should not send",
        },
    )
    assert response.status_code == 403
    mock_send_sms.assert_not_awaited()


def test_send_sms_not_ready_returns_503(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_with_phone: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "false")
    get_feature_flags.cache_clear()
    get_sms_delivery_settings.cache_clear()

    response = api_client.post(
        "/api/v1/notifications/sms/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_with_phone.id),
            "body": "Should not send",
        },
    )
    assert response.status_code == 503


def test_create_notification_with_deliver_sms(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_with_phone: User,
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_with_phone.id),
            "title": "SMS-backed alert",
            "body": "Please review the case.",
            "deliver_sms": True,
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["title"] == "SMS-backed alert"
    assert payload["sms_delivery"]["attempted"] is True
    assert payload["sms_delivery"]["status"] == "sent"
    assert payload["sms_delivery"]["delivery_log_id"] is not None
    mock_send_sms.assert_awaited_once()


def test_list_sms_deliveries(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_with_phone: User,
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    api_client.post(
        "/api/v1/notifications/sms/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_with_phone.id),
            "body": "Logged delivery",
        },
    )

    response = api_client.get("/api/v1/notifications/sms/deliveries", headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] >= 1
    assert any(item["body"] == "Logged delivery" for item in data["items"])


def test_send_sms_missing_phone_returns_422(
    api_client: TestClient,
    admin_headers: dict[str, str],
    case_manager_user: User,
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "body": "No phone on user",
        },
    )
    assert response.status_code == 422
    mock_send_sms.assert_not_awaited()


def test_send_sms_rejects_unknown_recipient(
    api_client: TestClient,
    admin_headers: dict[str, str],
    sms_env: None,
    mock_send_sms: AsyncMock,
) -> None:
    response = api_client.post(
        "/api/v1/notifications/sms/send",
        headers=admin_headers,
        json={
            "recipient_user_id": str(uuid.uuid4()),
            "body": "No recipient",
        },
    )
    assert response.status_code == 404
    mock_send_sms.assert_not_awaited()
