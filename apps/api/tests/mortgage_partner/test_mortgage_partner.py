"""Mortgage partner partnership + RBAC + pipeline + milestone + isolation tests."""

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
    assert "partner_pipeline" in body["capabilities"]
    assert "partner_milestones" in body["capabilities"]
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
    # pipeline defaults
    assert referral.json()["pipeline_stage"] == "referred"
    assert referral.json()["pipeline_stage_changed_at"] is not None
    # default milestones seeded
    milestones = referral.json()["milestones"]
    assert len(milestones) == 5
    assert milestones[0]["label"] == "Referral received"
    assert milestones[0]["complete"] is True
    assert milestones[1]["complete"] is False

    viewed = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=case_manager_headers,
    )
    assert viewed.status_code == 200
    assert viewed.json()["client_id"] == str(client_record.id)
    assert viewed.json()["client_display_name"] == "Referral Borrower"
    assert len(viewed.json()["milestones"]) == 5

    listed_referrals = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=case_manager_headers,
    )
    assert listed_referrals.status_code == 200, listed_referrals.text
    assert any(
        item["id"] == referral_id and item.get("client_display_name") == "Referral Borrower"
        for item in listed_referrals.json()
    )

    accepted = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=admin_headers,
        json={"status": "accepted"},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "accepted"
    assert accepted.json()["client_display_name"] == "Referral Borrower"

    forbidden_patch = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=case_manager_headers,
        json={"status": "declined"},
    )
    assert forbidden_patch.status_code == 403

    audits = api_client.get("/api/v1/mortgage-partner/access-audits", headers=admin_headers)
    assert audits.status_code == 200
    actions = {row["action"] for row in audits.json()}
    assert "partnership_create" in actions
    assert "referral_view" in actions
    assert "member_create" in actions
    assert "referral_update" in actions


def test_pipeline_stage_update(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Stage Test Lender",
        },
    )
    partnership_id = partnership.json()["id"]

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(client_record.id)},
    )
    assert referral.status_code == 201, referral.text
    referral_id = referral.json()["id"]
    assert referral.json()["pipeline_stage"] == "referred"
    original_changed_at = referral.json()["pipeline_stage_changed_at"]

    # advance stage
    patched = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=admin_headers,
        json={"pipeline_stage": "intake"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["pipeline_stage"] == "intake"
    assert patched.json()["pipeline_stage_changed_at"] != original_changed_at

    # patch with no fields → 422
    empty_patch = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=admin_headers,
        json={},
    )
    assert empty_patch.status_code == 422


def test_dashboard_summary(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Dashboard Summary Lender",
        },
    )
    partnership_id = partnership.json()["id"]

    for stage in ["referred", "near_ready", "mortgage_ready"]:
        api_client.post(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
            headers=admin_headers,
            json={"client_id": str(client_record.id), "pipeline_stage": stage},
        )

    summary = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/dashboard-summary",
        headers=admin_headers,
    )
    assert summary.status_code == 200, summary.text
    body = summary.json()
    assert body["total_referrals"] == 3
    assert body["counts_by_stage"]["referred"] == 1
    assert body["near_ready_count"] == 1
    assert body["mortgage_ready_count"] == 1
    assert body["funded_count"] == 0


def test_pipeline_endpoint(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Pipeline Lender",
        },
    )
    partnership_id = partnership.json()["id"]

    api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "pipeline_stage": "in_repair",
            "source_label": "LO desk",
        },
    )

    pipeline = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
        headers=admin_headers,
    )
    assert pipeline.status_code == 200, pipeline.text
    cards = pipeline.json()
    assert len(cards) == 1
    card = cards[0]
    assert card["pipeline_stage"] == "in_repair"
    assert card["client_display_name"] == "Referral Borrower"
    assert card["source_label"] == "LO desk"
    assert "days_in_stage" in card
    assert "stage_changed_at" in card


def test_milestone_get_and_replace(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Milestone Lender",
        },
    )
    partnership_id = partnership.json()["id"]

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(client_record.id)},
    )
    referral_id = referral.json()["id"]

    # GET milestones — 5 defaults
    get_ms = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
        headers=case_manager_headers,
    )
    assert get_ms.status_code == 200
    assert len(get_ms.json()) == 5

    # PUT replace milestones
    put_ms = api_client.put(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
        headers=admin_headers,
        json={
            "milestones": [
                {"label": "Custom step 1", "sort_order": 0, "complete": True},
                {"label": "Custom step 2", "sort_order": 1, "complete": False},
            ]
        },
    )
    assert put_ms.status_code == 200, put_ms.text
    new_ms = put_ms.json()
    assert len(new_ms) == 2
    assert new_ms[0]["label"] == "Custom step 1"
    assert new_ms[0]["complete"] is True
    assert new_ms[0]["completed_at"] is not None
    assert new_ms[1]["complete"] is False
    assert new_ms[1]["completed_at"] is None

    # verify list reflects replacement
    get_after = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
        headers=case_manager_headers,
    )
    assert len(get_after.json()) == 2

    # case_manager cannot replace milestones (write-only)
    forbidden = api_client.put(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
        headers=case_manager_headers,
        json={"milestones": []},
    )
    assert forbidden.status_code == 403


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


def test_tenant_isolation_pipeline_and_dashboard(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Other-org admin cannot access pipeline or dashboard of foreign partnership."""
    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Isolated Pipeline",
        },
    )
    partnership_id = create.json()["id"]
    api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={"client_id": str(client_record.id)},
    )

    other_pipeline = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
        headers=other_admin_headers,
    )
    assert other_pipeline.status_code == 404

    other_summary = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/dashboard-summary",
        headers=other_admin_headers,
    )
    assert other_summary.status_code == 404


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
