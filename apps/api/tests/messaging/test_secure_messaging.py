"""Secure messaging integration tests."""

import uuid

from fastapi.testclient import TestClient

from api.core.messaging import get_messaging_center_status
from tests.helpers.client_payload import sample_client_payload


def _create_client(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    display_name: str,
    email: str | None = None,
) -> str:
    payload = sample_client_payload(display_name=display_name)
    if email:
        payload["email"] = email
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_portal_user(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
    *,
    email: str,
) -> dict:
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _portal_login(api_client: TestClient, email: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_case(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    client_id: str,
) -> dict:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": title, "client_id": client_id},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_messaging_center_status_payload() -> None:
    status = get_messaging_center_status()
    assert status.secure_messaging_enabled is True
    assert status.thread_per_case is True
    assert "portal_client_messages" in status.capabilities
    assert "portal_web_push" in status.capabilities


def test_get_messaging_status(api_client: TestClient, readonly_headers: dict[str, str]) -> None:
    response = api_client.get("/api/v1/messaging/status", headers=readonly_headers)
    assert response.status_code == 200
    assert response.json()["thread_per_case"] is True


def test_portal_and_staff_messaging_on_linked_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-msg-{uuid.uuid4().hex[:8]}@example.com"
    client_id = _create_client(
        api_client, manager_headers, display_name="Messaging Client", email=email
    )
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    linked_case = _create_case(
        api_client,
        manager_headers,
        title="Messaging Case",
        client_id=client_id,
    )

    portal_headers = _portal_login(api_client, email)
    empty = api_client.get(
        f"/api/v1/portal/cases/{linked_case['id']}/messages",
        headers=portal_headers,
    )
    assert empty.status_code == 200, empty.text
    assert empty.json()["messages"] == []
    assert empty.json()["thread_id"] is None

    send_response = api_client.post(
        f"/api/v1/portal/cases/{linked_case['id']}/messages",
        headers=portal_headers,
        json={"body": "Hello from the portal"},
    )
    assert send_response.status_code == 201, send_response.text
    portal_message = send_response.json()
    assert portal_message["sender_role"] == "portal_client"
    assert portal_message["body"] == "Hello from the portal"

    staff_thread = api_client.get(
        f"/api/v1/cases/{linked_case['id']}/message-thread",
        headers=manager_headers,
    )
    assert staff_thread.status_code == 200, staff_thread.text
    thread = staff_thread.json()
    assert thread["thread_id"] is not None
    assert len(thread["messages"]) == 1

    staff_reply = api_client.post(
        f"/api/v1/cases/{linked_case['id']}/message-thread/messages",
        headers=manager_headers,
        json={"body": "Staff reply here"},
    )
    assert staff_reply.status_code == 201, staff_reply.text
    assert staff_reply.json()["sender_role"] == "staff"

    portal_list = api_client.get(
        f"/api/v1/portal/cases/{linked_case['id']}/messages",
        headers=portal_headers,
    )
    assert portal_list.status_code == 200
    assert len(portal_list.json()["messages"]) == 2


def test_portal_cannot_message_unlinked_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-msg-blocked-{uuid.uuid4().hex[:8]}@example.com"
    client_id = _create_client(api_client, manager_headers, display_name="Blocked Messaging Client")
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    other_case = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Private Messaging Case",
            "client_name": "Other Client",
            "client_email": f"private-{uuid.uuid4().hex[:8]}@example.com",
        },
    ).json()

    portal_headers = _portal_login(api_client, email)
    response = api_client.post(
        f"/api/v1/portal/cases/{other_case['id']}/messages",
        headers=portal_headers,
        json={"body": "Should not send"},
    )
    assert response.status_code == 404
