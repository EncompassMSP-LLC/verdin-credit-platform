"""Loan officer portal UAT happy-path API coverage (LRP-304).

Exercises the V1.0 LO journey without demo credentials:
status → partnership → referral → stage → milestones → dashboard → pipeline →
readiness report/export → notifications → tenant isolation.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization
from api.modules.clients.models import Client
from tests.accounts.conftest import sample_account_payload


def _create_case_with_published_run(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
) -> str:
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "title": f"LO UAT Case {uuid.uuid4().hex[:6]}",
            "client_id": client_id,
        },
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]
    account = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json=sample_account_payload(case_id),
    )
    assert account.status_code == 201, account.text
    run = api_client.post(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=headers,
    )
    assert run.status_code == 201, run.text
    return case_id


def test_lo_uat_happy_path_and_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    status = api_client.get("/api/v1/mortgage-partner/status", headers=case_manager_headers)
    assert status.status_code == 200, status.text
    assert status.json()["mortgage_partner_enabled"] is True
    caps = status.json()["capabilities"]
    assert "partner_pipeline" in caps
    assert "partner_readiness_report" in caps

    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": f"LO UAT Lender {uuid.uuid4().hex[:6]}",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert partnership.status_code == 201, partnership.text
    partnership_id = partnership.json()["id"]

    case_id = _create_case_with_published_run(api_client, admin_headers, str(client_record.id))

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "case_id": case_id,
            "source_label": "LO UAT warm handoff",
            "status": "new",
        },
    )
    assert referral.status_code == 201, referral.text
    referral_id = referral.json()["id"]
    assert referral.json()["pipeline_stage"] == "referred"
    assert len(referral.json()["milestones"]) == 5

    listed = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=case_manager_headers,
    )
    assert listed.status_code == 200, listed.text
    assert any(item["id"] == referral_id for item in listed.json())

    staged = api_client.patch(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
        headers=admin_headers,
        json={"pipeline_stage": "intake", "status": "accepted"},
    )
    assert staged.status_code == 200, staged.text
    assert staged.json()["pipeline_stage"] == "intake"
    assert staged.json()["status"] == "accepted"

    milestones = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
        headers=case_manager_headers,
    )
    assert milestones.status_code == 200, milestones.text
    assert len(milestones.json()) == 5
    assert milestones.json()[0]["complete"] is True

    dashboard = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/dashboard-summary",
        headers=case_manager_headers,
    )
    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["total_referrals"] >= 1
    assert dashboard.json()["counts_by_stage"].get("intake", 0) >= 1

    pipeline = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
        headers=case_manager_headers,
    )
    assert pipeline.status_code == 200, pipeline.text
    cards = pipeline.json()
    assert any(
        card["referral_id"] == referral_id and card["pipeline_stage"] == "intake" for card in cards
    )

    report = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=case_manager_headers,
    )
    assert report.status_code == 200, report.text
    report_body = report.json()
    assert report_body["band"]
    assert report_body["disclaimer"]
    disclaimer = report_body["disclaimer"].lower()
    assert "guarantee" not in disclaimer or "not a guarantee" in disclaimer
    assert "approved" not in disclaimer

    export = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report/export",
        headers=case_manager_headers,
        params={"format": "text"},
    )
    assert export.status_code == 200, export.text
    assert "disclaimer" in export.text.lower() or "advisory" in export.text.lower()

    notifications = api_client.get("/api/v1/notifications", headers=case_manager_headers)
    assert notifications.status_code == 200, notifications.text
    unread = api_client.get(
        "/api/v1/notifications/unread-count",
        headers=case_manager_headers,
    )
    assert unread.status_code == 200, unread.text
    assert "unread_count" in unread.json()

    # Isolation: foreign CRO org cannot see this partnership
    foreign = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
        headers=other_admin_headers,
    )
    assert foreign.status_code == 404
