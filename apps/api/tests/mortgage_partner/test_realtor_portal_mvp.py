"""Realtor portal MVP — partnership-scoped coarse referral surfaces (LRP-302)."""

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization


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


def _activate_realtor(
    api_client: TestClient,
    admin_headers: dict[str, str],
    partnership_id: str,
) -> dict[str, str]:
    email = f"portal-{uuid.uuid4().hex[:8]}@test.example"
    invite = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=admin_headers,
        json={"email": email, "first_name": "Riley", "last_name": "Realtor"},
    )
    assert invite.status_code == 201, invite.text
    accepted = api_client.post(
        "/api/v1/mortgage-partner/realtor/invites/accept",
        json={"token": invite.json()["invite_token"], "password": "securepass1"},
    )
    assert accepted.status_code == 200, accepted.text
    return {"Authorization": f"Bearer {accepted.json()['access_token']}"}


def test_realtor_portal_dashboard_referrals_pipeline(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
    client_record,
) -> None:
    partnership_id = _create_realtor_partnership(api_client, admin_headers, partner_org)
    realtor_headers = _activate_realtor(api_client, admin_headers, partnership_id)

    # Staff creates referral on realtor partnership
    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "source_label": "Open house",
            "status": "new",
            "pipeline_stage": "intake",
        },
    )
    assert referral.status_code == 201, referral.text

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert "realtor_portal_mvp" in status.json()["capabilities"]

    dashboard = api_client.get(
        "/api/v1/mortgage-partner/realtor/dashboard", headers=realtor_headers
    )
    assert dashboard.status_code == 200, dashboard.text
    body = dashboard.json()
    assert body["partnership_id"] == partnership_id
    assert body["total_referrals"] == 1
    assert body["counts_by_stage"]["intake"] == 1
    assert body["recent"][0]["borrower_initials"] == "R.B."
    assert "client_id" not in body["recent"][0]
    assert "notes" not in body["recent"][0]
    assert "advisory" in body["advisory_disclaimer"].lower()

    listed = api_client.get("/api/v1/mortgage-partner/realtor/referrals", headers=realtor_headers)
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1
    assert listed.json()[0]["pipeline_stage"] == "intake"

    pipeline = api_client.get("/api/v1/mortgage-partner/realtor/pipeline", headers=realtor_headers)
    assert pipeline.status_code == 200, pipeline.text
    assert pipeline.json()["partnership_id"] == partnership_id
    assert len(pipeline.json()["cards"]) == 1

    # Other CRO staff cannot use realtor portal without membership
    foreign = api_client.get(
        "/api/v1/mortgage-partner/realtor/dashboard",
        headers=other_admin_headers,
    )
    assert foreign.status_code == 403
