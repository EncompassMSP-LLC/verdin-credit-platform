"""LRP-103 — public partner referral web-form intake."""

from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.modules.auth.models import Organization


def test_referral_intake_creates_client_case_referral_and_task(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    cro_org: Organization,
    partner_org: Organization,
    monkeypatch,
) -> None:
    monkeypatch.setenv("REFERRAL_INTAKE_ENABLED", "true")
    monkeypatch.setenv("REFERRAL_INTAKE_ORGANIZATION_SLUG", cro_org.slug)
    get_settings.cache_clear()

    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Web Intake Lender",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert create.status_code == 201, create.text
    partnership_id = create.json()["id"]

    status = api_client.get("/api/v1/mortgage-partner/referral-intake/status")
    assert status.status_code == 200, status.text
    assert status.json()["referral_intake_enabled"] is True

    submitted = api_client.post(
        "/api/v1/mortgage-partner/referral-intake",
        json={
            "partner_org_name": "Harbor Home Mortgage",
            "lo_name": "Dana Lopez",
            "lo_email": "dana@harbor.example",
            "lo_phone": "555-0100",
            "borrower_name": "Alex Rivera",
            "borrower_email": "alex.rivera@example.com",
            "borrower_phone": "555-0199",
            "product_intent": "Purchase — conventional",
            "known_gaps": "Late payments last year",
            "notes": "Prefers evening calls",
            "consent_attested": True,
            "partnership_id": partnership_id,
        },
    )
    assert submitted.status_code == 201, submitted.text
    body = submitted.json()
    assert body["status"] == "accepted"
    assert body["partnership_id"] == partnership_id
    assert body["referral_id"]
    assert body["client_id"]
    assert body["case_id"]
    assert body["task_id"]
    assert body["orchestrator_run_id"]
    assert body["assigned_user_id"]  # admin fixture user is assignable

    orch = api_client.get(
        f"/api/v1/mortgage-partner/referral-intake/{body['intake_id']}/orchestrator",
        headers=admin_headers,
    )
    assert orch.status_code == 200, orch.text
    orch_body = orch.json()
    assert orch_body["id"] == body["orchestrator_run_id"]
    assert orch_body["status"] == "completed"
    step_keys = {step["key"] for step in orch_body["payload"]["steps"]}
    assert "assign_case_manager" in step_keys
    assert "thank_you_referrer" in step_keys
    assert "schedule_consultation_task" in step_keys
    assert orch_body["payload"]["claim_safety"]["auto_filing"] is False

    case = api_client.get(f"/api/v1/cases/{body['case_id']}", headers=admin_headers)
    assert case.status_code == 200, case.text
    assert case.json()["assigned_user_id"] == body["assigned_user_id"]

    referrals = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
    )
    assert referrals.status_code == 200
    assert any(row["id"] == body["referral_id"] for row in referrals.json())


def test_referral_intake_quarantines_ssn_in_notes(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    cro_org: Organization,
    partner_org: Organization,
    monkeypatch,
) -> None:
    monkeypatch.setenv("REFERRAL_INTAKE_ENABLED", "true")
    monkeypatch.setenv("REFERRAL_INTAKE_ORGANIZATION_SLUG", cro_org.slug)
    get_settings.cache_clear()

    create = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Quarantine Lender",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert create.status_code == 201, create.text

    submitted = api_client.post(
        "/api/v1/mortgage-partner/referral-intake",
        json={
            "partner_org_name": "Harbor Home Mortgage",
            "lo_name": "Dana Lopez",
            "lo_email": "dana@harbor.example",
            "borrower_name": "Alex Rivera",
            "borrower_email": "alex2@example.com",
            "notes": "SSN 123-45-6789 left in chat",
            "consent_attested": True,
            "partnership_id": create.json()["id"],
        },
    )
    assert submitted.status_code == 201, submitted.text
    body = submitted.json()
    assert body["status"] == "quarantined"
    assert body["referral_id"] is None
    assert body["quarantine_reason"]
    assert body.get("orchestrator_run_id") is None
    assert body.get("assigned_user_id") is None


def test_referral_intake_requires_consent(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    cro_org: Organization,
    monkeypatch,
) -> None:
    monkeypatch.setenv("REFERRAL_INTAKE_ENABLED", "true")
    monkeypatch.setenv("REFERRAL_INTAKE_ORGANIZATION_SLUG", cro_org.slug)
    get_settings.cache_clear()

    submitted = api_client.post(
        "/api/v1/mortgage-partner/referral-intake",
        json={
            "partner_org_name": "Harbor",
            "lo_name": "Dana",
            "lo_email": "dana@harbor.example",
            "borrower_name": "Alex",
            "borrower_email": "alex3@example.com",
            "consent_attested": False,
        },
    )
    assert submitted.status_code == 422
