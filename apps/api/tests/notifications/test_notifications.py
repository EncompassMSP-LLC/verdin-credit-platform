"""In-app notification endpoint tests."""

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import User


def _create_notification(
    api_client: TestClient,
    admin_headers: dict[str, str],
    recipient_user_id: str,
    *,
    title: str = "Test notification",
    category: str = "system",
) -> dict:
    response = api_client.post(
        "/api/v1/notifications",
        headers=admin_headers,
        json={
            "recipient_user_id": recipient_user_id,
            "title": title,
            "body": "Notification body",
            "category": category,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_notification_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    response = api_client.post(
        "/api/v1/notifications",
        headers=manager_headers,
        json={
            "recipient_user_id": str(case_manager_user.id),
            "title": "Blocked",
        },
    )
    assert response.status_code == 403


def test_list_notifications_for_recipient(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    _create_notification(
        api_client,
        admin_headers,
        str(case_manager_user.id),
        title="Assigned review",
        category="task",
    )

    response = api_client.get("/api/v1/notifications", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["title"] == "Assigned review" for item in data["items"])


def test_unread_count_and_mark_read(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    created = _create_notification(
        api_client,
        admin_headers,
        str(case_manager_user.id),
        title="Unread item",
    )

    unread = api_client.get("/api/v1/notifications/unread-count", headers=manager_headers)
    assert unread.status_code == 200
    assert unread.json()["unread_count"] >= 1

    read = api_client.post(
        f"/api/v1/notifications/{created['id']}/read",
        headers=manager_headers,
    )
    assert read.status_code == 200
    assert read.json()["read_at"] is not None

    unread_after = api_client.get("/api/v1/notifications/unread-count", headers=manager_headers)
    assert unread_after.json()["unread_count"] == unread.json()["unread_count"] - 1


def test_mark_all_read(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    _create_notification(api_client, admin_headers, str(case_manager_user.id), title="One")
    _create_notification(api_client, admin_headers, str(case_manager_user.id), title="Two")

    cleared = api_client.post("/api/v1/notifications/mark-all-read", headers=manager_headers)
    assert cleared.status_code == 200
    assert cleared.json()["unread_count"] == 0

    unread_only = api_client.get(
        "/api/v1/notifications",
        headers=manager_headers,
        params={"unread_only": True},
    )
    assert unread_only.json()["total"] == 0


def test_cannot_read_other_users_notification(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    created = _create_notification(
        api_client,
        admin_headers,
        str(case_manager_user.id),
        title="Private",
    )

    response = api_client.post(
        f"/api/v1/notifications/{created['id']}/read",
        headers=readonly_headers,
    )
    assert response.status_code == 404

    missing_recipient = api_client.post(
        "/api/v1/notifications",
        headers=admin_headers,
        json={
            "recipient_user_id": str(uuid.uuid4()),
            "title": "Missing user",
        },
    )
    assert missing_recipient.status_code == 404
