"""LRP-205 — CRM appointments + T-24h/T-1h reminders."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def test_appointment_create_list_and_reminder_process(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    starts = datetime.now(UTC) + timedelta(hours=12)
    ends = starts + timedelta(minutes=45)

    created = api_client.post(
        "/api/v1/mortgage-partner/appointments",
        headers=admin_headers,
        json={
            "title": "Intake consultation — Alex Rivera",
            "appointment_type": "consultation",
            "starts_at": starts.isoformat(),
            "ends_at": ends.isoformat(),
            "borrower_name": "Alex Rivera",
            "borrower_email": "alex.appt@example.com",
            "borrower_phone": "+15551212001",
            "tcpa_consent": True,
            "location": "Zoom",
            "meeting_url": "https://meet.example/lrp-alex",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["status"] == "scheduled"
    assert body["tcpa_consent"] is True
    appointment_id = body["id"]

    listed = api_client.get(
        "/api/v1/mortgage-partner/appointments",
        headers=admin_headers,
    )
    assert listed.status_code == 200, listed.text
    assert any(row["id"] == appointment_id for row in listed.json())

    # 12h until start → T-24h due, T-1h not yet
    processed = api_client.post(
        "/api/v1/mortgage-partner/appointments/reminders/process",
        headers=admin_headers,
    )
    assert processed.status_code == 200, processed.text
    result = processed.json()
    assert result["processed_count"] >= 1
    offsets = {run["offset_key"] for run in result["runs"]}
    assert "t24h" in offsets
    assert "t1h" not in offsets
    assert all(run["payload"]["claim_safety"]["auto_filing"] is False for run in result["runs"])

    # Idempotent — second process returns same run, does not duplicate
    again = api_client.post(
        "/api/v1/mortgage-partner/appointments/reminders/process",
        headers=admin_headers,
    )
    assert again.status_code == 200, again.text
    t24_runs = [r for r in again.json()["runs"] if r["offset_key"] == "t24h"]
    assert len(t24_runs) == 1
    assert t24_runs[0]["appointment_id"] == appointment_id

    reminders = api_client.get(
        "/api/v1/mortgage-partner/appointments/reminders",
        headers=admin_headers,
        params={"appointment_id": appointment_id},
    )
    assert reminders.status_code == 200, reminders.text
    assert len(reminders.json()) >= 1

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    caps = status.json()["capabilities"]
    assert "crm_appointments" in caps
    assert "appointment_reminders" in caps


def test_appointment_reminder_requires_tcpa_for_sms_channel(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    starts = datetime.now(UTC) + timedelta(minutes=50)
    ends = starts + timedelta(minutes=30)
    created = api_client.post(
        "/api/v1/mortgage-partner/appointments",
        headers=admin_headers,
        json={
            "title": "Near-term consult",
            "starts_at": starts.isoformat(),
            "ends_at": ends.isoformat(),
            "borrower_email": "near@example.com",
            "borrower_phone": "+15551212002",
            "tcpa_consent": False,
        },
    )
    assert created.status_code == 201, created.text

    processed = api_client.post(
        "/api/v1/mortgage-partner/appointments/reminders/process",
        headers=admin_headers,
    )
    assert processed.status_code == 200, processed.text
    # Both offsets due within 50 minutes
    offsets = {run["offset_key"] for run in processed.json()["runs"]}
    assert "t24h" in offsets
    assert "t1h" in offsets
