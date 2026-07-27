"""LRP-203 — persisted CRM automation rules."""

from fastapi.testclient import TestClient


def test_automation_rules_seed_defaults_and_toggle(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
) -> None:
    listed = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
    )
    assert listed.status_code == 200, listed.text
    rows = listed.json()
    assert len(rows) >= 5
    assert any(row["trigger"] == "referral_created" for row in rows)
    assert all("fire_count" in row for row in rows)

    # Idempotent seed — second list does not duplicate
    listed_again = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
    )
    assert listed_again.status_code == 200
    assert len(listed_again.json()) == len(rows)

    target = next(row for row in rows if row["trigger"] == "score_band_change")
    assert target["enabled"] is False

    patched = api_client.patch(
        f"/api/v1/mortgage-partner/automation-rules/{target['id']}",
        headers=admin_headers,
        json={"enabled": True},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["enabled"] is True

    created = api_client.post(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
        json={
            "name": "Manual ops ping",
            "description": "Staff-triggered reminder",
            "enabled": True,
            "trigger": "manual",
            "action": "Create ops follow-up task",
            "channel": "task",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["trigger"] == "manual"

    forbidden = api_client.post(
        "/api/v1/mortgage-partner/automation-rules",
        headers=case_manager_headers,
        json={
            "name": "Blocked",
            "trigger": "manual",
            "action": "Nope",
            "channel": "task",
        },
    )
    assert forbidden.status_code == 403

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "crm_automation_rules" in status.json()["capabilities"]
