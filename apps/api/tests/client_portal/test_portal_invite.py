"""Portal invite email on staff provisioning (LRP-301B)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
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
        json=sample_client_payload(display_name=f"Invite Client {uuid.uuid4().hex[:6]}"),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_provision_sends_invite_without_password_email(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"invite-{uuid.uuid4().hex[:8]}@example.com"

    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "send_invite": True},
    )
    assert provision.status_code == 201, provision.text
    body = provision.json()
    assert body["email"] == email
    assert body["invitation_pending"] is True
    assert "password" not in body
    assert "No password" in body["detail"]
    invite_token = body.get("invite_token")
    assert invite_token, "expected invite_token in test/dev env"

    blocked = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert blocked.status_code == 401

    accept = api_client.post(
        "/api/v1/portal/auth/accept-invite",
        json={"token": invite_token, "password": "chosenpass1"},
    )
    assert accept.status_code == 200, accept.text
    assert accept.json()["access_token"]

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "chosenpass1"},
    )
    assert login.status_code == 200, login.text

    reuse = api_client.post(
        "/api/v1/portal/auth/accept-invite",
        json={"token": invite_token, "password": "anotherpass1"},
    )
    assert reuse.status_code == 400


def test_resend_invite_rate_limit_and_activated_conflict(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"resend-{uuid.uuid4().hex[:8]}@example.com"

    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email},
    )
    assert provision.status_code == 201, provision.text

    too_soon = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user/resend-invite",
        headers=manager_headers,
    )
    assert too_soon.status_code == 429

    token = provision.json()["invite_token"]
    accept = api_client.post(
        "/api/v1/portal/auth/accept-invite",
        json={"token": token, "password": "chosenpass1"},
    )
    assert accept.status_code == 200, accept.text

    after_active = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user/resend-invite",
        headers=manager_headers,
    )
    assert after_active.status_code == 409


def test_resend_invite_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"ro-{uuid.uuid4().hex[:8]}@example.com"
    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email},
    )
    assert provision.status_code == 201, provision.text

    blocked = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user/resend-invite",
        headers=readonly_headers,
    )
    assert blocked.status_code == 403
