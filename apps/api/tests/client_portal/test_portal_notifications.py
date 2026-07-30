"""Portal notifications feed + read state (LRP-302A)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.modules.client_portal.notification_models import PortalNotification
from api.modules.client_portal.notification_service import sanitize_portal_action_url
from api.modules.notifications.models import NotificationCategory
from tests.helpers.client_payload import sample_client_payload


@pytest.fixture
def portal_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json=sample_client_payload(display_name=f"Notif Client {uuid.uuid4().hex[:6]}"),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_and_login(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    email: str | None = None,
    password: str = "password123",
) -> tuple[str, dict[str, str], str]:
    client_id = _create_client(api_client, headers)
    portal_email = email or f"notif-{uuid.uuid4().hex[:8]}@example.com"
    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": portal_email, "password": password, "send_invite": False},
    )
    assert provision.status_code == 201, provision.text
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": portal_email, "password": password},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return client_id, {"Authorization": f"Bearer {token}"}, provision.json()["id"]


def test_sanitize_portal_action_url() -> None:
    assert sanitize_portal_action_url("/portal/messages") == "/portal/messages"
    assert sanitize_portal_action_url("/portal/documents?tab=1") == "/portal/documents?tab=1"
    assert sanitize_portal_action_url("https://evil.example/portal/x") is None
    assert sanitize_portal_action_url("/lender/dashboard") is None
    assert sanitize_portal_action_url("/portal/../admin") is None


async def test_list_unread_mark_read_idempotent_and_mark_all(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    db_session: AsyncSession,
) -> None:
    _client_id, portal_headers, portal_user_id = _provision_and_login(api_client, manager_headers)
    me = api_client.get("/api/v1/portal/auth/me", headers=portal_headers)
    assert me.status_code == 200
    org_id = uuid.UUID(me.json()["organization_id"])
    client_id = uuid.UUID(me.json()["client_id"])
    recipient = uuid.UUID(portal_user_id)

    now = datetime.now(UTC)
    older = PortalNotification(
        id=uuid.uuid4(),
        organization_id=org_id,
        client_id=client_id,
        recipient_portal_user_id=recipient,
        title="Older notice",
        body="Body A",
        category=NotificationCategory.SYSTEM,
        action_url="/portal/dashboard",
        created_at=now - timedelta(minutes=5),
        updated_at=now - timedelta(minutes=5),
    )
    newer = PortalNotification(
        id=uuid.uuid4(),
        organization_id=org_id,
        client_id=client_id,
        recipient_portal_user_id=recipient,
        title="Newer notice",
        body="Body B",
        category=NotificationCategory.DOCUMENT,
        action_url="https://evil.example/steal",
        created_at=now,
        updated_at=now,
    )
    db_session.add_all([older, newer])
    await db_session.commit()

    listed = api_client.get("/api/v1/portal/notifications", headers=portal_headers)
    assert listed.status_code == 200, listed.text
    data = listed.json()
    assert data["total"] == 2
    assert data["items"][0]["title"] == "Newer notice"
    assert data["items"][0]["action_url"] is None  # unsafe deep link stripped
    assert data["items"][1]["title"] == "Older notice"
    assert data["items"][1]["action_url"] == "/portal/dashboard"

    unread = api_client.get("/api/v1/portal/notifications/unread-count", headers=portal_headers)
    assert unread.status_code == 200
    assert unread.json()["unread_count"] == 2

    first_read = api_client.post(
        f"/api/v1/portal/notifications/{newer.id}/read",
        headers=portal_headers,
    )
    assert first_read.status_code == 200
    assert first_read.json()["read_at"] is not None
    read_at = first_read.json()["read_at"]

    second_read = api_client.post(
        f"/api/v1/portal/notifications/{newer.id}/read",
        headers=portal_headers,
    )
    assert second_read.status_code == 200
    assert second_read.json()["read_at"] == read_at

    unread_mid = api_client.get("/api/v1/portal/notifications/unread-count", headers=portal_headers)
    assert unread_mid.json()["unread_count"] == 1

    cleared = api_client.post(
        "/api/v1/portal/notifications/mark-all-read",
        headers=portal_headers,
    )
    assert cleared.status_code == 200
    assert cleared.json()["unread_count"] == 0

    unread_only = api_client.get(
        "/api/v1/portal/notifications",
        headers=portal_headers,
        params={"unread_only": True},
    )
    assert unread_only.json()["total"] == 0


async def test_borrower_cannot_read_other_borrower_notifications(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
    db_session: AsyncSession,
) -> None:
    _a_client, a_headers, a_portal_id = _provision_and_login(
        api_client, manager_headers, email=f"a-{uuid.uuid4().hex[:8]}@example.com"
    )
    _b_client, b_headers, b_portal_id = _provision_and_login(
        api_client, manager_headers, email=f"b-{uuid.uuid4().hex[:8]}@example.com"
    )

    a_me = api_client.get("/api/v1/portal/auth/me", headers=a_headers).json()
    notification = PortalNotification(
        id=uuid.uuid4(),
        organization_id=uuid.UUID(a_me["organization_id"]),
        client_id=uuid.UUID(a_me["client_id"]),
        recipient_portal_user_id=uuid.UUID(a_portal_id),
        title="Private to A",
        body="Secret",
        category=NotificationCategory.TASK,
    )
    db_session.add(notification)
    await db_session.commit()

    stolen = api_client.post(
        f"/api/v1/portal/notifications/{notification.id}/read",
        headers=b_headers,
    )
    assert stolen.status_code == 404

    b_list = api_client.get("/api/v1/portal/notifications", headers=b_headers)
    assert b_list.status_code == 200
    assert all(item["title"] != "Private to A" for item in b_list.json()["items"])

    a_list = api_client.get("/api/v1/portal/notifications", headers=a_headers)
    assert any(item["id"] == str(notification.id) for item in a_list.json()["items"])
    assert uuid.UUID(b_portal_id) != uuid.UUID(a_portal_id)


async def test_invite_matrix_creates_portal_notification(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"invite-feed-{uuid.uuid4().hex[:8]}@example.com"
    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "send_invite": True},
    )
    assert provision.status_code == 201, provision.text
    invite_token = provision.json().get("invite_token")
    assert invite_token

    accept = api_client.post(
        "/api/v1/portal/auth/accept-invite",
        json={"token": invite_token, "password": "chosenpass1"},
    )
    assert accept.status_code == 200, accept.text
    portal_headers = {"Authorization": f"Bearer {accept.json()['access_token']}"}

    listed = api_client.get("/api/v1/portal/notifications", headers=portal_headers)
    assert listed.status_code == 200, listed.text
    titles = [item["title"] for item in listed.json()["items"]]
    assert any("invited" in title.lower() for title in titles)
    for item in listed.json()["items"]:
        assert "organization_id" not in item
        assert "recipient_portal_user_id" not in item
        assert "source_module" not in item
        if item["action_url"]:
            assert item["action_url"].startswith("/portal")
