"""Client management endpoint tests."""

import uuid

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def test_create_client(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    response = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(
            display_name="Jordan Rivera",
            email="jordan@example.com",
            phone="555-0100",
            status="active",
        ),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["display_name"] == "Jordan Rivera"
    assert data["email"] == "jordan@example.com"
    assert data["status"] == "active"
    assert data["mailing_address_line1"] == "123 Main St"
    assert data["mailing_city"] == "Atlanta"


def test_create_client_requires_mailing_address(
    api_client: TestClient, manager_headers: dict[str, str]
) -> None:
    response = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json={"display_name": "Missing Address"},
    )
    assert response.status_code == 422


def test_create_client_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/clients",
        headers=readonly_headers,
        json=sample_client_payload(display_name="Blocked Client"),
    )
    assert response.status_code == 403


def test_list_clients(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    unique = f"ListClient-{uuid.uuid4().hex[:6]}"
    api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name=unique),
    )
    response = api_client.get("/api/v1/clients", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["display_name"] == unique for item in data["items"])


def test_get_and_update_client(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    create = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Before Update"),
    )
    client_id = create.json()["id"]

    get_response = api_client.get(f"/api/v1/clients/{client_id}", headers=manager_headers)
    assert get_response.status_code == 200
    assert get_response.json()["display_name"] == "Before Update"

    update = api_client.patch(
        f"/api/v1/clients/{client_id}",
        headers=manager_headers,
        json={"display_name": "After Update", "status": "inactive"},
    )
    assert update.status_code == 200
    assert update.json()["display_name"] == "After Update"
    assert update.json()["status"] == "inactive"


def test_create_and_list_contacts(api_client: TestClient, manager_headers: dict[str, str]) -> None:
    client = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Contact Parent"),
    ).json()
    client_id = client["id"]

    contact = api_client.post(
        f"/api/v1/clients/{client_id}/contacts",
        headers=manager_headers,
        json={
            "full_name": "Primary Contact",
            "email": "primary@example.com",
            "relationship_type": "primary",
            "is_primary": True,
        },
    )
    assert contact.status_code == 201
    assert contact.json()["is_primary"] is True

    listed = api_client.get(
        f"/api/v1/clients/{client_id}/contacts",
        headers=manager_headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["full_name"] == "Primary Contact"


def test_primary_contact_is_exclusive(
    api_client: TestClient, manager_headers: dict[str, str]
) -> None:
    client_id = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Primary Switch"),
    ).json()["id"]

    first = api_client.post(
        f"/api/v1/clients/{client_id}/contacts",
        headers=manager_headers,
        json={"full_name": "First Primary", "is_primary": True},
    ).json()

    second = api_client.post(
        f"/api/v1/clients/{client_id}/contacts",
        headers=manager_headers,
        json={"full_name": "Second Primary", "is_primary": True},
    ).json()
    assert second["is_primary"] is True

    first_after = api_client.get(
        f"/api/v1/clients/{client_id}/contacts/{first['id']}",
        headers=manager_headers,
    )
    assert first_after.status_code == 200
    assert first_after.json()["is_primary"] is False


def test_delete_client_requires_admin(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    client_id = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Delete Me"),
    ).json()["id"]

    forbidden = api_client.delete(f"/api/v1/clients/{client_id}", headers=manager_headers)
    assert forbidden.status_code == 403

    deleted = api_client.delete(f"/api/v1/clients/{client_id}", headers=admin_headers)
    assert deleted.status_code == 204

    missing = api_client.get(f"/api/v1/clients/{client_id}", headers=manager_headers)
    assert missing.status_code == 404


def test_delete_client_cascades_cases_and_accounts(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    client_id = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Cascade Delete Client"),
    ).json()["id"]

    case_id = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Cascade Case",
            "client_id": client_id,
            "client_name": "Cascade Delete Client",
        },
    ).json()["id"]

    account_id = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json={
            "case_id": case_id,
            "creditor_name": "Cascade Creditor",
            "bureau": "equifax",
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "current",
            "account_number_masked": "****9999",
        },
    ).json()["id"]

    contact_id = api_client.post(
        f"/api/v1/clients/{client_id}/contacts",
        headers=manager_headers,
        json={
            "full_name": "Primary Contact",
            "relationship_type": "primary",
            "is_primary": True,
        },
    ).json()["id"]

    deleted = api_client.delete(f"/api/v1/clients/{client_id}", headers=admin_headers)
    assert deleted.status_code == 204

    assert (
        api_client.get(f"/api/v1/clients/{client_id}", headers=manager_headers).status_code == 404
    )
    assert api_client.get(f"/api/v1/cases/{case_id}", headers=manager_headers).status_code == 404
    assert (
        api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).status_code == 404
    )
    assert (
        api_client.get(
            f"/api/v1/clients/{client_id}/contacts/{contact_id}",
            headers=manager_headers,
        ).status_code
        == 404
    )

    accounts_list = api_client.get("/api/v1/accounts", headers=manager_headers)
    assert accounts_list.status_code == 200
    assert all(item["id"] != account_id for item in accounts_list.json()["items"])

    cases_list = api_client.get("/api/v1/cases", headers=manager_headers)
    assert cases_list.status_code == 200
    assert all(item["id"] != case_id for item in cases_list.json()["items"])
