"""Reporting operations read model tests."""

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import User
from tests.helpers.client_payload import sample_client_payload


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json=sample_client_payload(display_name=f"Reporting Client {uuid.uuid4().hex[:6]}"),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_notification(
    api_client: TestClient,
    admin_headers: dict[str, str],
    recipient_user_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/notifications",
        headers=admin_headers,
        json={
            "recipient_user_id": recipient_user_id,
            "title": "Reporting notification",
            "category": "system",
        },
    )
    assert response.status_code == 201, response.text


def test_operations_reporting_requires_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/reporting/operations")
    assert response.status_code == 401


def test_operations_reporting_returns_read_model(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    case_manager_user: User,
) -> None:
    _create_client(api_client, manager_headers)
    _create_notification(api_client, admin_headers, str(case_manager_user.id))

    response = api_client.get("/api/v1/reporting/operations", headers=manager_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "generated_at" in body
    operations = body["operations"]
    assert operations["clients"]["total"] >= 1
    assert operations["clients"]["active"] >= 1
    assert isinstance(operations["dispute_accounts"], dict)
    assert isinstance(operations["dispute_letters"], dict)
    assert operations["notifications"]["created_today"] >= 1
    assert operations["notifications"]["unread_total"] >= 1
    assert operations["portal_users"] >= 0


def test_dashboard_includes_operations_section(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    _create_client(api_client, manager_headers)

    response = api_client.get("/api/v1/dashboard", headers=manager_headers)
    assert response.status_code == 200, response.text
    operations = response.json()["operations"]
    assert operations["clients"]["total"] >= 1
    assert "dispute_accounts" in operations
    assert "notifications" in operations
