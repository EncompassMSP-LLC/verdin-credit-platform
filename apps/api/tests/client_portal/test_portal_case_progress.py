"""Client portal case progress integration tests."""

import uuid

from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags


def _create_client(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    display_name: str,
    email: str | None = None,
) -> str:
    payload: dict[str, str] = {"display_name": display_name}
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
    client_name: str,
    client_email: str | None = None,
) -> dict:
    payload: dict[str, str] = {"title": title, "client_name": client_name}
    if client_email:
        payload["client_email"] = client_email
    response = api_client.post("/api/v1/cases", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_portal_cases_hidden_when_disabled(api_client: TestClient) -> None:
    get_feature_flags.cache_clear()
    response = api_client.get("/api/v1/portal/cases")
    assert response.status_code == 404


def test_portal_user_lists_and_views_matching_cases(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-case-{uuid.uuid4().hex[:8]}@example.com"
    display_name = f"Portal Case Client {uuid.uuid4().hex[:6]}"
    client_id = _create_client(
        api_client,
        manager_headers,
        display_name=display_name,
        email=email,
    )
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    visible_case = _create_case(
        api_client,
        manager_headers,
        title="Visible Portal Case",
        client_name=display_name,
        client_email=email,
    )
    _create_case(
        api_client,
        manager_headers,
        title="Hidden Portal Case",
        client_name="Someone Else",
        client_email=f"other-{uuid.uuid4().hex[:8]}@example.com",
    )

    portal_headers = _portal_login(api_client, email)
    list_response = api_client.get("/api/v1/portal/cases", headers=portal_headers)
    assert list_response.status_code == 200, list_response.text
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == visible_case["id"]
    assert items[0]["title"] == "Visible Portal Case"

    detail_response = api_client.get(
        f"/api/v1/portal/cases/{visible_case['id']}",
        headers=portal_headers,
    )
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["status"] == visible_case["status"]
    assert detail["stage"] == visible_case["stage"]
    assert detail["account_count"] == 0
    assert isinstance(detail["dispute_accounts"], dict)


def test_portal_user_cannot_view_unmatched_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-blocked-{uuid.uuid4().hex[:8]}@example.com"
    client_id = _create_client(api_client, manager_headers, display_name="Blocked Client")
    _provision_portal_user(api_client, manager_headers, client_id, email=email)

    other_case = _create_case(
        api_client,
        manager_headers,
        title="Private Case",
        client_name="Other Client",
        client_email=f"private-{uuid.uuid4().hex[:8]}@example.com",
    )

    portal_headers = _portal_login(api_client, email)
    response = api_client.get(
        f"/api/v1/portal/cases/{other_case['id']}",
        headers=portal_headers,
    )
    assert response.status_code == 404
