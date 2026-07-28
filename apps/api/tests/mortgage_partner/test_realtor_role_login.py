"""Realtor partner role + invite/login tests (LRP-301)."""

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization
from api.modules.mortgage_partner.models import PartnerRole
from api.modules.mortgage_partner.permissions import PARTNER_ROLE_PERMISSIONS


def _create_realtor_partnership(
    api_client: TestClient,
    admin_headers: dict[str, str],
    realtor_org: Organization,
) -> str:
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(realtor_org.id),
            "display_name": "Summit Realty Partners",
            "partner_type": "realtor",
            "status": "active",
        },
    )
    assert create.status_code == 201, create.text
    return create.json()["id"]


def test_realtor_role_in_matrix(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    roles = api_client.get("/api/v1/mortgage-partner/roles", headers=admin_headers)
    assert roles.status_code == 200
    role_names = {item["role"] for item in roles.json()["roles"]}
    assert "realtor" in role_names
    assert role_names == {role.value for role in PARTNER_ROLE_PERMISSIONS}
    realtor_perms = next(item for item in roles.json()["roles"] if item["role"] == "realtor")
    assert "readiness.export" not in realtor_perms["permissions"]
    assert "referrals.create" in realtor_perms["permissions"]

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "realtor_partner_role" in status.json()["capabilities"]
    assert "realtor_portal_auth" in status.json()["capabilities"]


def test_realtor_invite_accept_me_and_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    partnership_id = _create_realtor_partnership(api_client, admin_headers, partner_org)

    email = f"realtor-{uuid.uuid4().hex[:8]}@test.example"
    invite = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=admin_headers,
        json={
            "email": email,
            "first_name": "Riley",
            "last_name": "Realtor",
        },
    )
    assert invite.status_code == 201, invite.text
    token = invite.json()["invite_token"]
    assert token
    assert invite.json()["accepted_at"] is None

    preview = api_client.get(
        "/api/v1/mortgage-partner/realtor/invites/preview",
        params={"token": token},
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["email"] == email
    assert preview.json()["already_accepted"] is False

    foreign = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=other_admin_headers,
        json={
            "email": f"x-{uuid.uuid4().hex[:6]}@test.example",
            "first_name": "X",
            "last_name": "Y",
        },
    )
    assert foreign.status_code == 404

    accepted = api_client.post(
        "/api/v1/mortgage-partner/realtor/invites/accept",
        json={"token": token, "password": "securepass1"},
    )
    assert accepted.status_code == 200, accepted.text
    body = accepted.json()
    assert body["access_token"]
    assert body["realtor"]["partner_role"] == PartnerRole.REALTOR.value
    assert body["realtor"]["partnership_id"] == partnership_id
    assert body["realtor"]["email"] == email
    realtor_headers = {"Authorization": f"Bearer {body['access_token']}"}

    me = api_client.get("/api/v1/mortgage-partner/realtor/me", headers=realtor_headers)
    assert me.status_code == 200, me.text
    assert me.json()["partnership_id"] == partnership_id
    assert me.json()["membership_active"] is True

    forbidden = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=realtor_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Should Fail",
            "partner_type": "realtor",
        },
    )
    assert forbidden.status_code == 403

    member_id = me.json()["membership_id"]
    disabled = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-members/{member_id}/disable",
        headers=admin_headers,
        params={"disable_user": "false"},
    )
    assert disabled.status_code == 200, disabled.text
    assert disabled.json()["membership_active"] is False

    blocked = api_client.get("/api/v1/mortgage-partner/realtor/me", headers=realtor_headers)
    assert blocked.status_code == 403
    assert "disabled" in blocked.json()["detail"].lower()


def test_realtor_password_reset_and_disabled_account(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    partnership_id = _create_realtor_partnership(api_client, admin_headers, partner_org)
    email = f"reset-{uuid.uuid4().hex[:8]}@test.example"
    invite = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=admin_headers,
        json={"email": email, "first_name": "Pat", "last_name": "Partner"},
    )
    assert invite.status_code == 201, invite.text
    accepted = api_client.post(
        "/api/v1/mortgage-partner/realtor/invites/accept",
        json={"token": invite.json()["invite_token"], "password": "oldpassword1"},
    )
    assert accepted.status_code == 200, accepted.text
    member_id = accepted.json()["realtor"]["membership_id"]

    reset_req = api_client.post(
        "/api/v1/mortgage-partner/realtor/password-reset/request",
        json={"email": email},
    )
    assert reset_req.status_code == 200, reset_req.text
    reset_token = reset_req.json().get("reset_token")
    assert reset_token, "expected reset_token in test/dev env"

    confirmed = api_client.post(
        "/api/v1/mortgage-partner/realtor/password-reset/confirm",
        json={"token": reset_token, "password": "newpassword1"},
    )
    assert confirmed.status_code == 200, confirmed.text
    new_headers = {"Authorization": f"Bearer {confirmed.json()['access_token']}"}
    me = api_client.get("/api/v1/mortgage-partner/realtor/me", headers=new_headers)
    assert me.status_code == 200

    login = api_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "newpassword1"},
    )
    assert login.status_code == 200, login.text

    disabled = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-members/{member_id}/disable",
        headers=admin_headers,
        params={"disable_user": "true"},
    )
    assert disabled.status_code == 200, disabled.text

    login_blocked = api_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "newpassword1"},
    )
    assert login_blocked.status_code == 403
    assert "inactive" in login_blocked.json()["detail"].lower()


def test_lender_partnership_rejects_realtor_invite(
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
            "display_name": "Harbor Home Mortgage",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert create.status_code == 201, create.text
    partnership_id = create.json()["id"]
    invite = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=admin_headers,
        json={
            "email": f"bad-{uuid.uuid4().hex[:6]}@test.example",
            "first_name": "No",
            "last_name": "Go",
        },
    )
    assert invite.status_code == 400
    assert "realtor" in invite.json()["detail"].lower()
