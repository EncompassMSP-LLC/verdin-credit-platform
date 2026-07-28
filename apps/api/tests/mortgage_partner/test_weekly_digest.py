"""LRP-207 — weekly partner status digest subscriptions + processing."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization
from api.modules.clients.models import Client
from api.modules.mortgage_partner.weekly_digest_service import borrower_initials, iso_week_key


def test_borrower_initials_and_week_key() -> None:
    assert borrower_initials("Alex Rivera") == "A.R."
    assert borrower_initials("Madonna") == "M."
    assert iso_week_key(datetime(2026, 7, 27, tzinfo=UTC)).startswith("2026-W")


def test_weekly_digest_subscribe_process_idempotent(
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
            "display_name": "Digest Lender Co",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert partnership.status_code == 201, partnership.text
    partnership_id = partnership.json()["id"]

    referral = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=admin_headers,
        json={
            "client_id": str(client_record.id),
            "status": "accepted",
            "pipeline_stage": "intake",
            "source_label": "digest-test",
        },
    )
    assert referral.status_code == 201, referral.text

    rejected = api_client.post(
        "/api/v1/mortgage-partner/weekly-digests/subscriptions",
        headers=admin_headers,
        json={
            "partnership_id": partnership_id,
            "recipient_name": "No Opt",
            "recipient_email": "noopt@example.com",
            "marketing_opt_in": False,
        },
    )
    assert rejected.status_code == 400, rejected.text

    created = api_client.post(
        "/api/v1/mortgage-partner/weekly-digests/subscriptions",
        headers=admin_headers,
        json={
            "partnership_id": partnership_id,
            "recipient_name": "Jordan LO",
            "recipient_email": "jordan.lo@example.com",
            "send_weekday": 1,
            "marketing_opt_in": True,
        },
    )
    assert created.status_code == 201, created.text
    subscription_id = created.json()["id"]
    assert created.json()["enabled"] is True

    week_key = iso_week_key(datetime.now(UTC))
    processed = api_client.post(
        "/api/v1/mortgage-partner/weekly-digests/process",
        headers=admin_headers,
        params={"week_key": week_key, "force": True},
    )
    assert processed.status_code == 200, processed.text
    result = processed.json()
    assert result["week_key"] == week_key
    assert result["processed_count"] >= 1
    run = next(r for r in result["runs"] if r["subscription_id"] == subscription_id)
    assert run["payload"]["claim_safety"]["pii_minimized"] is True
    assert run["payload"]["claim_safety"]["auto_filing"] is False
    assert "pipeline_snapshot" in run["payload"]
    assert run["body_text"] is not None
    assert "underwriting decision" in (run["body_text"] or "").lower()
    # Body must not dump full borrower names from fixture display names
    assert "changeme" not in (run["body_text"] or "").lower()

    again = api_client.post(
        "/api/v1/mortgage-partner/weekly-digests/process",
        headers=admin_headers,
        params={"week_key": week_key, "force": True},
    )
    assert again.status_code == 200, again.text
    runs = [
        r
        for r in again.json()["runs"]
        if r["subscription_id"] == subscription_id and r["week_key"] == week_key
    ]
    assert len(runs) == 1

    archived = api_client.get(
        "/api/v1/mortgage-partner/weekly-digests/runs",
        headers=admin_headers,
        params={"partnership_id": partnership_id},
    )
    assert archived.status_code == 200, archived.text
    assert any(row["id"] == run["id"] for row in archived.json())

    opted_out = api_client.patch(
        f"/api/v1/mortgage-partner/weekly-digests/subscriptions/{subscription_id}",
        headers=admin_headers,
        json={"marketing_opt_in": False},
    )
    assert opted_out.status_code == 200, opted_out.text
    assert opted_out.json()["enabled"] is False

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "weekly_partner_digest" in status.json()["capabilities"]


def test_weekly_digest_tenant_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    partnership = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=admin_headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Isolation Digest Partner",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert partnership.status_code == 201, partnership.text
    partnership_id = partnership.json()["id"]

    created = api_client.post(
        "/api/v1/mortgage-partner/weekly-digests/subscriptions",
        headers=admin_headers,
        json={
            "partnership_id": partnership_id,
            "recipient_name": "Org A LO",
            "recipient_email": "orga.lo@example.com",
            "marketing_opt_in": True,
        },
    )
    assert created.status_code == 201, created.text
    subscription_id = created.json()["id"]

    other_list = api_client.get(
        "/api/v1/mortgage-partner/weekly-digests/subscriptions",
        headers=other_admin_headers,
    )
    assert other_list.status_code == 200, other_list.text
    assert all(row["id"] != subscription_id for row in other_list.json())

    other_patch = api_client.patch(
        f"/api/v1/mortgage-partner/weekly-digests/subscriptions/{subscription_id}",
        headers=other_admin_headers,
        json={"enabled": False},
    )
    assert other_patch.status_code == 404, other_patch.text
