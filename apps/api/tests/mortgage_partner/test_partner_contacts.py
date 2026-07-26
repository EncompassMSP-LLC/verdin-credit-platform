"""LRP-101 — partner CRM contacts CRUD + enrichment + tenant isolation."""

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization
from api.modules.clients.models import Client


def _create_partnership(
    api_client: TestClient,
    admin_headers: dict[str, str],
    partner_org: Organization,
) -> str:
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Harbor Home Mortgage",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert create.status_code == 201, create.text
    return create.json()["id"]


def test_partner_contacts_crud_and_primary_enrichment(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "partner_contacts" in status.json()["capabilities"]

    created = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=admin_headers,
        json={
            "first_name": "Dana",
            "last_name": "Lopez",
            "email": "dana@harbor.example",
            "phone": "555-0100",
            "job_title": "Senior LO",
            "contact_role": "loan_officer",
            "is_primary": True,
        },
    )
    assert created.status_code == 201, created.text
    contact_id = created.json()["id"]
    assert created.json()["is_primary"] is True
    assert created.json()["email"] == "dana@harbor.example"

    secondary = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=admin_headers,
        json={
            "first_name": "Pat",
            "last_name": "Ng",
            "email": "pat@harbor.example",
            "contact_role": "operations",
            "is_primary": True,
        },
    )
    assert secondary.status_code == 201, secondary.text
    secondary_id = secondary.json()["id"]

    listed = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=case_manager_headers,
    )
    assert listed.status_code == 200, listed.text
    by_id = {row["id"]: row for row in listed.json()}
    assert by_id[secondary_id]["is_primary"] is True
    assert by_id[contact_id]["is_primary"] is False

    partnerships = api_client.get(
        "/api/v1/mortgage-partner/partnerships", headers=case_manager_headers
    )
    assert partnerships.status_code == 200
    row = next(item for item in partnerships.json() if item["id"] == partnership_id)
    assert row["primary_contact_name"] == "Pat Ng"
    assert row["primary_contact_email"] == "pat@harbor.example"
    assert row["active_referral_count"] == 0

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(client_record.id), "status": "new"},
    )
    assert referral.status_code == 201, referral.text

    partnerships2 = api_client.get(
        "/api/v1/mortgage-partner/partnerships", headers=case_manager_headers
    )
    row2 = next(item for item in partnerships2.json() if item["id"] == partnership_id)
    assert row2["active_referral_count"] == 1

    patched = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts/{contact_id}",
        headers=admin_headers,
        json={"is_primary": True, "job_title": "Team Lead"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["is_primary"] is True
    assert patched.json()["job_title"] == "Team Lead"

    listed2 = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=case_manager_headers,
    )
    by_id2 = {row["id"]: row for row in listed2.json()}
    assert by_id2[contact_id]["is_primary"] is True
    assert by_id2[secondary_id]["is_primary"] is False

    forbidden = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=case_manager_headers,
        json={"first_name": "No", "last_name": "Write"},
    )
    assert forbidden.status_code == 403

    audits = api_client.get("/api/v1/mortgage-partner/access-audits", headers=admin_headers)
    assert audits.status_code == 200
    actions = {row["action"] for row in audits.json()}
    assert "contact_create" in actions
    assert "contact_list" in actions
    assert "contact_update" in actions


def test_partner_contacts_tenant_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    other_admin_headers: dict[str, str],
) -> None:
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    created = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=admin_headers,
        json={"first_name": "Secret", "last_name": "Contact", "is_primary": True},
    )
    assert created.status_code == 201, created.text
    contact_id = created.json()["id"]

    listed = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
        headers=other_admin_headers,
    )
    assert listed.status_code == 404

    patched = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts/{contact_id}",
        headers=other_admin_headers,
        json={"first_name": "Hacked"},
    )
    assert patched.status_code == 404
