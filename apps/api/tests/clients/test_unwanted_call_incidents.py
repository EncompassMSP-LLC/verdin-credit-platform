"""Unwanted-call complaint incident API tests (LRP-209A)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "display_name": "Ada Borrower",
            "email": f"ada-{datetime.now(UTC).timestamp()}@example.com",
            "mailing_address_line1": "1 Main St",
            "mailing_city": "Austin",
            "mailing_state": "TX",
            "mailing_postal_code": "78701",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_unwanted_call_incident_crud_and_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    case = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": "Unwanted Call Case",
            "client_name": "Ada Borrower",
            "client_id": client_id,
        },
    )
    assert case.status_code == 201, case.text
    case_id = case.json()["id"]

    # Seed prefs so eligibility has DNC context
    prefs = api_client.put(
        f"/api/v1/clients/{client_id}/communication-preferences",
        headers=manager_headers,
        json={
            "dnc_assistance_requested": True,
            "dnc_consent_attested": True,
            "dnc_phone_ownership_confirmed": True,
            "dnc_disclosure_acknowledged": True,
            "dnc_phone_number": "+15551234567",
            "workplace_calls_prohibited": True,
        },
    )
    assert prefs.status_code == 200, prefs.text
    opened = api_client.post(
        f"/api/v1/clients/{client_id}/communication-preferences/do-not-call/open-registry",
        headers=manager_headers,
    )
    assert opened.status_code == 200, opened.text
    completed = api_client.post(
        f"/api/v1/clients/{client_id}/communication-preferences/do-not-call/mark-completed",
        headers=manager_headers,
    )
    assert completed.status_code == 200, completed.text

    called_at = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    create = api_client.post(
        f"/api/v1/clients/{client_id}/unwanted-call-incidents",
        headers=manager_headers,
        json={
            "called_at": called_at,
            "case_id": case_id,
            "caller_number": "+15557654321",
            "party_type": "telemarketer",
            "channel": "phone",
            "creditor_or_collector_name": "Spam Co",
            "complaint_target": "ftc",
            "notes": "Repeated sales call after DNC",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["client_id"] == client_id
    assert body["case_id"] == case_id
    assert body["status"] == "draft_ready"
    assert body["external_submission_status"] == "draft_prepared"
    assert "call_after_dnc_completed" in body["eligibility_guidance"]["codes"]
    assert "never auto-submits" in body["disclaimer"].lower()
    assert "DRAFT" in (body["draft_text"] or "")
    incident_id = body["id"]

    listed = api_client.get(
        f"/api/v1/clients/{client_id}/unwanted-call-incidents",
        headers=manager_headers,
    )
    assert listed.status_code == 200
    assert len(listed.json()["items"]) >= 1
    assert "never auto-submits" in listed.json()["disclaimer"].lower()

    timeline = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"case_id": case_id, "event_type": "UNWANTED_CALL_INCIDENT_RECORDED"},
    )
    assert timeline.status_code == 200
    assert timeline.json()["total"] >= 1

    patched = api_client.patch(
        f"/api/v1/clients/{client_id}/unwanted-call-incidents/{incident_id}",
        headers=manager_headers,
        json={"status": "follow_up_due", "follow_up_notes": "Call client Friday"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["status"] == "follow_up_due"

    updated_events = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={"case_id": case_id, "event_type": "UNWANTED_CALL_INCIDENT_UPDATED"},
    )
    assert updated_events.status_code == 200
    assert updated_events.json()["total"] >= 1

    deleted = api_client.delete(
        f"/api/v1/clients/{client_id}/unwanted-call-incidents/{incident_id}",
        headers=manager_headers,
    )
    assert deleted.status_code == 204

    after = api_client.get(
        f"/api/v1/clients/{client_id}/unwanted-call-incidents",
        headers=manager_headers,
    )
    assert after.status_code == 200
    assert after.json()["items"] == []
