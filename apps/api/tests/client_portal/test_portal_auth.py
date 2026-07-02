"""Client portal auth integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags


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
        json={"display_name": f"Portal Client {uuid.uuid4().hex[:6]}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_portal_user(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
    *,
    email: str,
    password: str = "password123",
) -> dict:
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_portal_endpoints_hidden_when_disabled(api_client: TestClient) -> None:
    get_feature_flags.cache_clear()
    response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": "portal@example.com", "password": "password123"},
    )
    assert response.status_code == 404


def test_provision_and_portal_login(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"portal-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    data = login.json()
    assert data["access_token"]
    assert data["refresh_token"]

    me = api_client.get(
        "/api/v1/portal/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email
    assert me.json()["client_id"] == client_id


def test_portal_token_rejected_on_staff_me(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"portal-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    token = login.json()["access_token"]

    staff_me = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert staff_me.status_code == 401


def test_staff_token_rejected_on_portal_me(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    response = api_client.get("/api/v1/portal/auth/me", headers=manager_headers)
    assert response.status_code == 401


def test_portal_refresh_flow(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"portal-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    refresh_token = login.json()["refresh_token"]

    refreshed = api_client.post(
        "/api/v1/portal/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["access_token"]
    assert refreshed.json()["refresh_token"] != refresh_token


def test_portal_refresh_rejected_on_staff_refresh(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    email = f"portal-{uuid.uuid4().hex[:8]}@example.com"
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    refresh_token = login.json()["refresh_token"]

    staff_refresh = api_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert staff_refresh.status_code == 401


def test_provision_portal_user_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=readonly_headers,
        json={"email": "blocked@example.com", "password": "password123"},
    )
    assert response.status_code == 403
