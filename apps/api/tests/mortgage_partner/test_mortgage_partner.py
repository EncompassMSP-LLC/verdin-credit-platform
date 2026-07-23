"""Mortgage partner partnership + RBAC + isolation tests."""

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization, User
from api.modules.clients.models import Client
from api.modules.mortgage_partner.permissions import PARTNER_ROLE_PERMISSIONS


def test_status_404_when_flag_disabled(
    api_client: TestClient,
    mortgage_partner_disabled: None,
    admin_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert response.status_code == 404


def test_status_and_role_matrix(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    body = status.json()
    assert body["mortgage_partner_enabled"] is True
    assert "partnerships" in body["capabilities"]
    assert "cross_tenant_marketplace" in body["deferred_capabilities"]

    roles = api_client.get("/api/v1/mortgage-partner/roles", headers=admin_headers)
    assert roles.status_code == 200
    role_names = {item["role"] for item in roles.json()["roles"]}
    assert role_names == {role.value for role in PARTNER_ROLE_PERMISSIONS}


def test_create_partnership_member_referral_and_audit(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
    partner_org: Organization,
    partner_lo_user: User,
    client_record: Client,
) -> None:
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
    partnership_id = create.json()["id"]

    listed = api_client.get("/api/v1/mortgage-partner/partnerships", headers=case_manager_headers)
    assert listed.status_code == 200
    assert any(item["id"] == partnership_id for item in listed.json())

    member = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/members",
        headers=admin_headers,
        json={
            "user_id": str(partner_lo_user.id),
            "partner_role": "loan_officer",
        },
    )
    assert member.status_code == 201, member.text
    assert member.json()["partner_role"] == "loan_officer"

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "source_label": "LO warm handoff",
            "status": "new",
        },
    )
    assert referral.status_code == 201, referral.text
    referral_id = referral.json()["id"]

    viewed = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=case_manager_headers,
    )
    assert viewed.status_code == 200
    assert viewed.json()["client_id"] == str(client_record.id)
    assert viewed.json()["client_display_name"] == "Referral Borrower"

    listed_referrals = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=case_manager_headers,
    )
    assert listed_referrals.status_code == 200, listed_referrals.text
    assert any(
        item["id"] == referral_id and item.get("client_display_name") == "Referral Borrower"
        for item in listed_referrals.json()
    )

    audits = api_client.get("/api/v1/mortgage-partner/access-audits", headers=admin_headers)
    assert audits.status_code == 200
    actions = {row["action"] for row in audits.json()}
    assert "partnership_create" in actions
    assert "referral_view" in actions
    assert "member_create" in actions


def test_case_manager_cannot_create_partnership(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    case_manager_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    response = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=case_manager_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Blocked",
        },
    )
    assert response.status_code == 403


def test_tenant_isolation_hides_other_org_partnership(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Isolated Partnership",
        },
    )
    assert create.status_code == 201
    partnership_id = create.json()["id"]

    other_list = api_client.get(
        "/api/v1/mortgage-partner/partnerships", headers=other_admin_headers
    )
    assert other_list.status_code == 200
    assert other_list.json() == []

    other_get = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}",
        headers=other_admin_headers,
    )
    assert other_get.status_code == 404


def test_cannot_refer_foreign_client(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Referral Guard",
        },
    )
    partnership_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404
