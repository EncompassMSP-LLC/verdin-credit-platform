"""Portal push notification tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.core.portal_push import get_portal_push_settings
from api.modules.client_portal.push_models import PortalPushDeliveryLog, PortalPushDeliveryStatus


@pytest.fixture
def portal_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def portal_push_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_PORTAL_PUSH", "true")
    monkeypatch.setenv("PORTAL_PUSH_PROVIDER", "web_push")
    monkeypatch.setenv("PORTAL_PUSH_VAPID_PUBLIC_KEY", "test-public-key")
    monkeypatch.setenv("PORTAL_PUSH_VAPID_PRIVATE_KEY", "test-private-key")
    monkeypatch.setenv("PORTAL_PUSH_VAPID_SUBJECT", "mailto:push@verdin.demo")
    get_feature_flags.cache_clear()
    get_portal_push_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_portal_push_settings.cache_clear()


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json={"display_name": f"Push Client {uuid.uuid4().hex[:6]}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_portal_user(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
    *,
    email: str,
) -> None:
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201, response.text


def _portal_login(api_client: TestClient, email: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_portal_push_endpoints_hidden_when_disabled(
    api_client: TestClient,
    portal_enabled: None,
) -> None:
    response = api_client.get("/api/v1/portal/push/status")
    assert response.status_code == 404


def test_portal_push_status_when_enabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    portal_push_env: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"push-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    portal_headers = _portal_login(api_client, email)

    response = api_client.get("/api/v1/portal/push/status", headers=portal_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["provider"] == "web_push"
    assert payload["active_subscription_count"] == 0


def test_subscribe_portal_push(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    portal_push_env: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"push-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    portal_headers = _portal_login(api_client, email)

    response = api_client.post(
        "/api/v1/portal/push/subscribe",
        headers=portal_headers,
        json={
            "endpoint": "https://push.example.test/subscription/1",
            "p256dh_key": "test-p256dh",
            "auth_key": "test-auth",
            "user_agent": "pytest",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["is_active"] is True

    status_response = api_client.get("/api/v1/portal/push/status", headers=portal_headers)
    assert status_response.json()["active_subscription_count"] == 1


@pytest.mark.asyncio
async def test_staff_message_creates_portal_push_delivery_log(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    portal_push_env: None,
    db_session: AsyncSession,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"push-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    portal_headers = _portal_login(api_client, email)

    subscribe = api_client.post(
        "/api/v1/portal/push/subscribe",
        headers=portal_headers,
        json={
            "endpoint": "https://push.example.test/subscription/2",
            "p256dh_key": "test-p256dh",
            "auth_key": "test-auth",
        },
    )
    assert subscribe.status_code == 201, subscribe.text

    case_response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Push messaging case", "client_id": client_id},
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    message_response = api_client.post(
        f"/api/v1/cases/{case_id}/message-thread/messages",
        headers=manager_headers,
        json={"body": "Staff reply for push notification test"},
    )
    assert message_response.status_code == 201, message_response.text

    result = await db_session.execute(select(PortalPushDeliveryLog))
    logs = list(result.scalars().all())
    assert len(logs) >= 1
    assert logs[0].status == PortalPushDeliveryStatus.SENT
