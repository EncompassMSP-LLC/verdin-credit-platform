"""LRP smoke E2E — Mortgage Partner Edition happy path in CI (LRP-503).

Covers staff-mediated lending-readiness surfaces against a running API:

  Auth → mortgage-partner status → partnership → client/case/account
  → credit analysis → referral → pipeline/dashboard → readiness report
  → automation rules dry-run audit

Does not exercise unsupervised filing, live bureau pulls, or demo auth.
"""

from __future__ import annotations

import uuid

import httpx
from sqlalchemy.orm import Session, sessionmaker

from api.modules.auth.models import Organization
from tests.e2e.fixtures.organization import OrganizationRecord
from tests.e2e.fixtures.users import UserRecord
from tests.e2e.helpers import auth
from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.assertions import expect_ok


def _seed_partner_org(db_session_factory: sessionmaker[Session]) -> OrganizationRecord:
    suffix = uuid.uuid4().hex[:8]
    with db_session_factory() as session:
        org = Organization(
            id=uuid.uuid4(),
            name=f"E2E Lender Partner {suffix}",
            slug=f"e2e-lender-{suffix}",
            is_active=True,
        )
        session.add(org)
        session.commit()
        return OrganizationRecord(id=org.id, name=org.name, slug=org.slug)


def test_lrp_smoke_mortgage_partner_path(
    http: httpx.Client,
    owner: UserRecord,
    organization: OrganizationRecord,
    db_session_factory: sessionmaker[Session],
    artifacts: ArtifactCollector,
) -> None:
    tokens = auth.login(http, owner.email, owner.password)
    headers = tokens.headers

    status = expect_ok(
        http.get("/api/v1/mortgage-partner/status", headers=headers),
        label="lrp_status",
        artifacts=artifacts,
    )
    assert status["mortgage_partner_enabled"] is True
    caps = status["capabilities"]
    for required in (
        "partner_pipeline",
        "partner_readiness_report",
        "crm_automation_rules",
        "crm_automation_audit_events",
        "partner_isolation_denial_suite",
    ):
        assert required in caps, f"missing capability {required}"

    partner = _seed_partner_org(db_session_factory)
    partnership = expect_ok(
        http.post(
            "/api/v1/mortgage-partner/partnerships",
            headers=headers,
            json={
                "partner_organization_id": str(partner.id),
                "display_name": f"E2E Partnership {partner.slug}",
                "partner_type": "lender",
                "status": "active",
            },
        ),
        label="lrp_partnership",
        artifacts=artifacts,
        expected_status=201,
    )
    partnership_id = partnership["id"]

    client = expect_ok(
        http.post(
            "/api/v1/clients",
            headers=headers,
            json={
                "display_name": f"E2E Borrower {uuid.uuid4().hex[:6]}",
                "email": f"borrower-{uuid.uuid4().hex[:8]}@verdin-e2e.com",
                "mailing_address_line1": "100 Smoke Test Ave",
                "mailing_city": "Austin",
                "mailing_state": "TX",
                "mailing_postal_code": "78701",
                "status": "active",
            },
        ),
        label="lrp_client",
        artifacts=artifacts,
        expected_status=201,
    )
    client_id = client["id"]

    case = expect_ok(
        http.post(
            "/api/v1/cases",
            headers=headers,
            json={
                "title": f"LRP Smoke Case {uuid.uuid4().hex[:6]}",
                "client_id": client_id,
            },
        ),
        label="lrp_case",
        artifacts=artifacts,
        expected_status=201,
    )
    case_id = case["id"]

    expect_ok(
        http.post(
            "/api/v1/accounts",
            headers=headers,
            json={
                "case_id": case_id,
                "creditor_name": "E2E Example Bank",
                "bureau": "equifax",
                "account_type": "credit_card",
                "account_status": "open",
                "payment_status": "late_60",
                "account_number_masked": "****4242",
                "balance": "1200.00",
                "past_due_amount": "250.00",
            },
        ),
        label="lrp_account",
        artifacts=artifacts,
        expected_status=201,
    )

    expect_ok(
        http.post(
            f"/api/v1/cases/{case_id}/credit-analysis/runs",
            headers=headers,
        ),
        label="lrp_credit_analysis",
        artifacts=artifacts,
        expected_status=201,
    )

    referral = expect_ok(
        http.post(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
            headers=headers,
            json={
                "client_id": client_id,
                "case_id": case_id,
                "source_label": "LRP-503 smoke handoff",
                "status": "new",
            },
        ),
        label="lrp_referral",
        artifacts=artifacts,
        expected_status=201,
    )
    referral_id = referral["id"]
    assert referral["pipeline_stage"] == "referred"
    assert len(referral["milestones"]) == 5

    staged = expect_ok(
        http.patch(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}",
            headers=headers,
            json={"pipeline_stage": "intake", "status": "accepted"},
        ),
        label="lrp_referral_stage",
        artifacts=artifacts,
    )
    assert staged["pipeline_stage"] == "intake"
    assert staged["status"] == "accepted"

    dashboard = expect_ok(
        http.get(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}/dashboard-summary",
            headers=headers,
        ),
        label="lrp_dashboard",
        artifacts=artifacts,
    )
    assert dashboard["total_referrals"] >= 1
    assert dashboard["counts_by_stage"].get("intake", 0) >= 1

    pipeline = expect_ok(
        http.get(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}/pipeline",
            headers=headers,
        ),
        label="lrp_pipeline",
        artifacts=artifacts,
    )
    assert any(
        card["referral_id"] == referral_id and card["pipeline_stage"] == "intake"
        for card in pipeline
    )

    report = expect_ok(
        http.get(
            f"/api/v1/mortgage-partner/partnerships/{partnership_id}"
            f"/referrals/{referral_id}/readiness-report",
            headers=headers,
        ),
        label="lrp_readiness_report",
        artifacts=artifacts,
    )
    assert report["band"]
    assert report["disclaimer"]
    disclaimer = report["disclaimer"].lower()
    assert "not a guarantee" in disclaimer or "guarantee" not in disclaimer
    assert "approved" not in disclaimer

    rules = expect_ok(
        http.get("/api/v1/mortgage-partner/automation-rules", headers=headers),
        label="lrp_automation_rules",
        artifacts=artifacts,
    )
    assert isinstance(rules, list) and len(rules) >= 1
    task_rule = next((row for row in rules if row["channel"] == "task"), rules[0])

    dry_run = expect_ok(
        http.post(
            f"/api/v1/mortgage-partner/automation-rules/{task_rule['id']}/fire",
            headers=headers,
            json={"dry_run": True},
        ),
        label="lrp_automation_dry_run",
        artifacts=artifacts,
        expected_status=201,
    )
    assert dry_run["event_kind"] == "rule_dry_run"
    assert dry_run["status"] == "dry_run"
    assert dry_run["payload"].get("auto_filing") is False

    events = expect_ok(
        http.get(
            "/api/v1/mortgage-partner/automation-events",
            headers=headers,
            params={"rule_id": task_rule["id"], "limit": 10},
        ),
        label="lrp_automation_events",
        artifacts=artifacts,
    )
    assert any(row["id"] == dry_run["id"] for row in events)

    artifacts.record(
        "lrp_smoke_complete",
        {
            "organization_id": str(organization.id),
            "partnership_id": partnership_id,
            "referral_id": referral_id,
            "case_id": case_id,
        },
    )
