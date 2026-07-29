"""LRP-502 — CRM automation audit events + staff-mediated fire."""

from fastapi.testclient import TestClient


def test_automation_audit_on_create_update_and_dry_run_fire(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    case_manager_headers: dict[str, str],
) -> None:
    created = api_client.post(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
        json={
            "name": "Audit probe rule",
            "description": "LRP-502 coverage",
            "enabled": True,
            "trigger": "manual",
            "action": "Create ops follow-up task",
            "channel": "task",
        },
    )
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]

    events = api_client.get(
        "/api/v1/mortgage-partner/automation-events",
        headers=admin_headers,
        params={"rule_id": rule_id},
    )
    assert events.status_code == 200, events.text
    kinds = {row["event_kind"] for row in events.json()}
    assert "rule_created" in kinds

    patched = api_client.patch(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}",
        headers=admin_headers,
        json={"enabled": False},
    )
    assert patched.status_code == 200, patched.text

    events_after = api_client.get(
        "/api/v1/mortgage-partner/automation-events",
        headers=admin_headers,
        params={"rule_id": rule_id, "event_kind": "rule_disabled"},
    )
    assert events_after.status_code == 200, events_after.text
    assert len(events_after.json()) >= 1

    dry = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=admin_headers,
        json={},
    )
    assert dry.status_code == 201, dry.text
    body = dry.json()
    assert body["event_kind"] == "rule_dry_run"
    assert body["status"] == "dry_run"
    assert body["payload"]["auto_filing"] is False

    rules = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
    )
    assert rules.status_code == 200
    rule = next(row for row in rules.json() if row["id"] == rule_id)
    assert rule["fire_count"] == 0

    live_skip_disabled = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=admin_headers,
        json={"dry_run": False},
    )
    assert live_skip_disabled.status_code == 201, live_skip_disabled.text
    assert live_skip_disabled.json()["event_kind"] == "rule_skipped"
    assert live_skip_disabled.json()["status"] == "skipped"

    reenabled = api_client.patch(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}",
        headers=admin_headers,
        json={"enabled": True},
    )
    assert reenabled.status_code == 200, reenabled.text

    live = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=admin_headers,
        json={"dry_run": False},
    )
    assert live.status_code == 201, live.text
    assert live.json()["event_kind"] == "rule_fired"
    assert live.json()["status"] == "completed"

    rules_after = api_client.get(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
    )
    rule_after = next(row for row in rules_after.json() if row["id"] == rule_id)
    assert rule_after["fire_count"] == 1
    assert rule_after["last_fired_at"] is not None

    detail = api_client.get(
        f"/api/v1/mortgage-partner/automation-events/{live.json()['id']}",
        headers=admin_headers,
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["id"] == live.json()["id"]

    forbidden = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=case_manager_headers,
        json={"dry_run": True},
    )
    assert forbidden.status_code == 403

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "crm_automation_audit_events" in status.json()["capabilities"]


def test_automation_live_fire_skips_non_allowlisted_channel(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    created = api_client.post(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
        json={
            "name": "Email channel rule",
            "enabled": True,
            "trigger": "manual",
            "action": "Email LO advisory alert",
            "channel": "email",
        },
    )
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]

    live = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=admin_headers,
        json={"dry_run": False},
    )
    assert live.status_code == 201, live.text
    assert live.json()["event_kind"] == "rule_skipped"
    assert live.json()["payload"]["outcome"] == "channel_not_live_allowed"


def test_automation_audit_events_cross_tenant_denial(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
) -> None:
    created = api_client.post(
        "/api/v1/mortgage-partner/automation-rules",
        headers=admin_headers,
        json={
            "name": "Isolation audit rule",
            "enabled": True,
            "trigger": "manual",
            "action": "Create task",
            "channel": "task",
        },
    )
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]

    dry = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=admin_headers,
        json={"dry_run": True},
    )
    assert dry.status_code == 201, dry.text
    event_id = dry.json()["id"]

    foreign_list = api_client.get(
        "/api/v1/mortgage-partner/automation-events",
        headers=other_admin_headers,
        params={"rule_id": rule_id},
    )
    assert foreign_list.status_code == 200, foreign_list.text
    assert foreign_list.json() == []

    foreign_detail = api_client.get(
        f"/api/v1/mortgage-partner/automation-events/{event_id}",
        headers=other_admin_headers,
    )
    assert foreign_detail.status_code == 404

    foreign_fire = api_client.post(
        f"/api/v1/mortgage-partner/automation-rules/{rule_id}/fire",
        headers=other_admin_headers,
        json={"dry_run": True},
    )
    assert foreign_fire.status_code == 404
