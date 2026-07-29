"""LRP-501 — consolidated partner cross-tenant denial suite.

Verifies org-scoped mortgage-partner surfaces hide foreign tenants (404) or
deny unauthenticated-membership access (403). Does not introduce a new audit
run table (LRP-502) or partner JWT realm.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.modules.auth.models import Organization
from api.modules.clients.models import Client


def _create_partnership(
    api_client: TestClient,
    headers: dict[str, str],
    partner_org: Organization,
    *,
    display_name: str = "Isolation Partnership",
    partner_type: str = "lender",
) -> str:
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": display_name,
            "partner_type": partner_type,
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
    email = f"iso-realtor-{uuid.uuid4().hex[:8]}@test.example"
    invite = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/realtor-invites",
        headers=admin_headers,
        json={"email": email, "first_name": "Iso", "last_name": "Realtor"},
    )
    assert invite.status_code == 201, invite.text
    accepted = api_client.post(
        "/api/v1/mortgage-partner/realtor/invites/accept",
        json={"token": invite.json()["invite_token"], "password": "securepass1"},
    )
    assert accepted.status_code == 200, accepted.text
    return {"Authorization": f"Bearer {accepted.json()['access_token']}"}


def test_status_advertises_partner_isolation_denial_suite(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200, status.text
    body = status.json()
    assert "partner_isolation_denial_suite" in body["capabilities"]
    assert "cross_tenant_marketplace" in body["deferred_capabilities"]
    assert "partner_jwt_realm" in body["deferred_capabilities"]


def test_appointments_cross_tenant_denial(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
) -> None:
    starts = datetime.now(UTC) + timedelta(hours=12)
    ends = starts + timedelta(minutes=30)
    created = api_client.post(
        "/api/v1/mortgage-partner/appointments",
        headers=admin_headers,
        json={
            "title": "Isolated consultation",
            "appointment_type": "consultation",
            "starts_at": starts.isoformat(),
            "ends_at": ends.isoformat(),
            "borrower_name": "Jordan Sample",
            "borrower_email": "jordan.iso@example.com",
            "tcpa_consent": True,
        },
    )
    assert created.status_code == 201, created.text
    appointment_id = created.json()["id"]

    foreign_list = api_client.get(
        "/api/v1/mortgage-partner/appointments",
        headers=other_admin_headers,
    )
    assert foreign_list.status_code == 200, foreign_list.text
    assert all(row["id"] != appointment_id for row in foreign_list.json())

    foreign_patch = api_client.patch(
        f"/api/v1/mortgage-partner/appointments/{appointment_id}",
        headers=other_admin_headers,
        json={"status": "cancelled"},
    )
    assert foreign_patch.status_code == 404

    # Seed a reminder run in-org, then confirm foreign org cannot see it
    api_client.post(
        "/api/v1/mortgage-partner/appointments/reminders/process",
        headers=admin_headers,
    )
    foreign_reminders = api_client.get(
        "/api/v1/mortgage-partner/appointments/reminders",
        headers=other_admin_headers,
        params={"appointment_id": appointment_id},
    )
    assert foreign_reminders.status_code == 200, foreign_reminders.text
    assert foreign_reminders.json() == []


def test_automation_rules_cross_tenant_denial(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
) -> None:
    listed = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
    )
    assert listed.status_code == 200, listed.text
    rows = listed.json()
    assert rows
    rule_id = rows[0]["id"]

    foreign_list = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=other_admin_headers,
    )
    assert foreign_list.status_code == 200, foreign_list.text
    foreign_ids = {row["id"] for row in foreign_list.json()}
    assert rule_id not in foreign_ids

    foreign_patch = api_client.patch(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}",
        headers=other_admin_headers,
        json={"enabled": True},
    )
    assert foreign_patch.status_code == 404


def test_referral_intake_orchestrator_cross_tenant_denial(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    cro_org: Organization,
    partner_org: Organization,
    monkeypatch,
) -> None:
    monkeypatch.setenv("REFERRAL_INTAKE_ENABLED", "true")
    monkeypatch.setenv("REFERRAL_INTAKE_ORGANIZATION_SLUG", cro_org.slug)
    get_settings.cache_clear()

    partnership_id = _create_partnership(
        api_client,
        admin_headers,
        partner_org,
        display_name="Intake Isolation Lender",
    )
    submitted = api_client.post(
        "/api/v1/mortgage-partner/referral-intake",
        json={
            "partner_org_name": "Isolation Mortgage",
            "lo_name": "Pat Loan",
            "lo_email": "pat@iso.example",
            "borrower_name": "Casey Borrower",
            "borrower_email": "casey.iso@example.com",
            "consent_attested": True,
            "partnership_id": partnership_id,
        },
    )
    assert submitted.status_code == 201, submitted.text
    intake_id = submitted.json()["intake_id"]

    own = api_client.get(
        f"/api/v1/mortgage-partner/referral-intake/{intake_id}/orchestrator",
        headers=admin_headers,
    )
    assert own.status_code == 200, own.text

    foreign = api_client.get(
        f"/api/v1/mortgage-partner/referral-intake/{intake_id}/orchestrator",
        headers=other_admin_headers,
    )
    assert foreign.status_code == 404


def test_access_audits_cross_tenant_denial(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    partnership_id = _create_partnership(
        api_client,
        admin_headers,
        partner_org,
        display_name="Audit Isolation",
    )
    audits = api_client.get(
        "/api/v1/mortgage-partner/access-audits",
        headers=admin_headers,
    )
    assert audits.status_code == 200, audits.text
    own_ids = {row["id"] for row in audits.json()}
    assert own_ids

    foreign = api_client.get(
        "/api/v1/mortgage-partner/access-audits",
        headers=other_admin_headers,
    )
    assert foreign.status_code == 200, foreign.text
    foreign_ids = {row["id"] for row in foreign.json()}
    assert own_ids.isdisjoint(foreign_ids)

    # Foreign partnership id must not leak via partnership GET either
    other_get = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}",
        headers=other_admin_headers,
    )
    assert other_get.status_code == 404


def test_foreign_partnership_surface_denials(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership_id = _create_partnership(
        api_client,
        admin_headers,
        partner_org,
        display_name="Surface Isolation",
    )
    api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(client_record.id)},
    )

    paths = [
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/members",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/dashboard-summary",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/readiness-report",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/readiness-report/export",
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/contacts",
    ]
    for path in paths:
        response = api_client.get(path, headers=other_admin_headers)
        assert response.status_code == 404, f"{path} -> {response.status_code} {response.text}"


def test_realtor_partnership_scoped_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    second_partner_org: Organization,
    client_record: Client,
) -> None:
    """Realtor on partnership A must not see partnership B referrals."""
    partnership_a = _create_partnership(
        api_client,
        admin_headers,
        partner_org,
        display_name="Realtor A Partnership",
        partner_type="realtor",
    )
    partnership_b = _create_partnership(
        api_client,
        admin_headers,
        second_partner_org,
        display_name="Realtor B Partnership",
        partner_type="realtor",
    )
    realtor_a = _activate_realtor(api_client, admin_headers, partnership_a)
    realtor_b = _activate_realtor(api_client, admin_headers, partnership_b)

    referral_b = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_b}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "source_label": "B only",
            "pipeline_stage": "intake",
        },
    )
    assert referral_b.status_code == 201, referral_b.text

    dash_a = api_client.get(
        "/api/v1/mortgage-partner/realtor/dashboard",
        headers=realtor_a,
    )
    assert dash_a.status_code == 200, dash_a.text
    assert dash_a.json()["partnership_id"] == partnership_a
    assert dash_a.json()["total_referrals"] == 0

    listed_a = api_client.get(
        "/api/v1/mortgage-partner/realtor/referrals",
        headers=realtor_a,
    )
    assert listed_a.status_code == 200
    assert listed_a.json() == []

    pipeline_a = api_client.get(
        "/api/v1/mortgage-partner/realtor/pipeline",
        headers=realtor_a,
    )
    assert pipeline_a.status_code == 200
    assert pipeline_a.json()["partnership_id"] == partnership_a
    assert pipeline_a.json()["cards"] == []

    dash_b = api_client.get(
        "/api/v1/mortgage-partner/realtor/dashboard",
        headers=realtor_b,
    )
    assert dash_b.status_code == 200, dash_b.text
    assert dash_b.json()["partnership_id"] == partnership_b
    assert dash_b.json()["total_referrals"] == 1
