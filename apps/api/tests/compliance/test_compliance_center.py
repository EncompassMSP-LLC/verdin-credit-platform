"""Compliance center scaffold tests."""

import uuid

from fastapi.testclient import TestClient

from api.core.compliance import get_compliance_center_status
from api.modules.clients.models import Client


def test_compliance_center_status_payload() -> None:
    status = get_compliance_center_status()
    assert status.consent_records_enabled is True
    assert status.retention_policies_enabled is True
    assert status.consent_type_count == 5
    assert status.retention_scope_count == 4
    assert "consent_record_crud" in status.capabilities
    assert "retention_enforcement_jobs" in status.capabilities
    assert "legal_sign_off_workflows" in status.deferred_capabilities


def test_get_compliance_status(api_client: TestClient, readonly_headers: dict[str, str]) -> None:
    response = api_client.get("/api/v1/compliance/status", headers=readonly_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["consent_records_enabled"] is True
    assert data["retention_scope_count"] == 4


def test_create_and_list_consent_records(
    api_client: TestClient,
    manager_headers: dict[str, str],
    test_client: Client,
) -> None:
    create_response = api_client.post(
        "/api/v1/compliance/consents",
        headers=manager_headers,
        json={
            "client_id": str(test_client.id),
            "consent_type": "croa_services",
            "source": "staff",
            "notes": "Signed during intake",
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["status"] == "granted"
    assert created["client_id"] == str(test_client.id)
    assert created["consent_type"] == "croa_services"

    list_response = api_client.get(
        f"/api/v1/compliance/consents?client_id={test_client.id}",
        headers=manager_headers,
    )
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["total"] >= 1
    assert any(item["id"] == created["id"] for item in listed["items"])


def test_get_consent_record(
    api_client: TestClient,
    manager_headers: dict[str, str],
    test_client: Client,
) -> None:
    create_response = api_client.post(
        "/api/v1/compliance/consents",
        headers=manager_headers,
        json={
            "client_id": str(test_client.id),
            "consent_type": "fcra_dispute",
        },
    )
    consent_id = create_response.json()["id"]

    get_response = api_client.get(
        f"/api/v1/compliance/consents/{consent_id}",
        headers=manager_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == consent_id


def test_withdraw_consent_record(
    api_client: TestClient,
    manager_headers: dict[str, str],
    test_client: Client,
) -> None:
    create_response = api_client.post(
        "/api/v1/compliance/consents",
        headers=manager_headers,
        json={
            "client_id": str(test_client.id),
            "consent_type": "marketing",
        },
    )
    consent_id = create_response.json()["id"]

    withdraw_response = api_client.post(
        f"/api/v1/compliance/consents/{consent_id}/withdraw",
        headers=manager_headers,
    )
    assert withdraw_response.status_code == 200, withdraw_response.text
    withdrawn = withdraw_response.json()
    assert withdrawn["status"] == "withdrawn"
    assert withdrawn["withdrawn_at"] is not None

    repeat_response = api_client.post(
        f"/api/v1/compliance/consents/{consent_id}/withdraw",
        headers=manager_headers,
    )
    assert repeat_response.status_code == 400


def test_create_consent_requires_write_role(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    test_client: Client,
) -> None:
    response = api_client.post(
        "/api/v1/compliance/consents",
        headers=readonly_headers,
        json={
            "client_id": str(test_client.id),
            "consent_type": "croa_services",
        },
    )
    assert response.status_code == 403


def test_create_consent_unknown_client(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/compliance/consents",
        headers=manager_headers,
        json={
            "client_id": str(uuid.uuid4()),
            "consent_type": "croa_services",
        },
    )
    assert response.status_code == 404


def test_retention_policy_admin_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    denied = api_client.post(
        "/api/v1/compliance/retention-policies",
        headers=manager_headers,
        json={
            "name": "Document retention",
            "scope": "documents",
            "retention_days": 2555,
        },
    )
    assert denied.status_code == 403

    created = api_client.post(
        "/api/v1/compliance/retention-policies",
        headers=admin_headers,
        json={
            "name": "Document retention",
            "scope": "documents",
            "retention_days": 2555,
            "description": "Seven-year placeholder",
        },
    )
    assert created.status_code == 201, created.text
    policy = created.json()
    assert policy["scope"] == "documents"
    assert policy["retention_days"] == 2555

    updated = api_client.patch(
        f"/api/v1/compliance/retention-policies/{policy['id']}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    listed = api_client.get("/api/v1/compliance/retention-policies", headers=admin_headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    fetched = api_client.get(
        f"/api/v1/compliance/retention-policies/{policy['id']}",
        headers=admin_headers,
    )
    assert fetched.status_code == 200
