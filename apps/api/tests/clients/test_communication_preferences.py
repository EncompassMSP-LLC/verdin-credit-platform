"""LRP-209 client communication preferences + Do Not Call assistance tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json=sample_client_payload(display_name="Comm Prefs Client", phone="555-0199"),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_get_communication_preferences_defaults(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    response = api_client.get(
        f"/api/v1/clients/{client_id}/communication-preferences",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["client_id"] == client_id
    assert body["preferred_channel"] == "mail"
    assert body["dnc_status"] == "not_started"
    assert "creditors" in body["dnc_disclosure"].lower()
    assert "never silently" in body["disclaimer"].lower()
    assert "donotcall.gov" in body["official_dnc_registry_url"]
    assert "DRAFT" in body["communication_request_draft"]
    assert "stop creditor calls" not in body["dnc_disclosure"].lower()


def test_update_and_dnc_workflow(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)

    updated = api_client.put(
        f"/api/v1/clients/{client_id}/communication-preferences",
        headers=manager_headers,
        json={
            "preferred_channel": "email",
            "do_not_text": True,
            "workplace_calls_prohibited": True,
            "dnc_assistance_requested": True,
            "dnc_consent_attested": True,
            "dnc_phone_ownership_confirmed": True,
            "dnc_disclosure_acknowledged": True,
            "dnc_phone_number": "555-0199",
            "collector_opt_out_recorded": True,
        },
    )
    assert updated.status_code == 200, updated.text
    data = updated.json()
    assert data["preferred_channel"] == "email"
    assert data["do_not_text"] is True
    assert data["dnc_status"] == "consent_recorded"
    assert data["collector_opt_out_recorded"] is True
    assert data["collector_opt_out_recorded_at"] is not None

    blocked = api_client.post(
        f"/api/v1/clients/{client_id}/communication-preferences/do-not-call/open-registry",
        headers=manager_headers,
    )
    assert blocked.status_code == 200, blocked.text
    opened = blocked.json()
    assert opened["dnc_status"] == "awaiting_email_confirmation"
    assert opened["dnc_registry_opened_at"] is not None
    assert any(e["action"] == "dnc_registry_opened" for e in opened["preference_events"])

    premature_complete = api_client.post(
        f"/api/v1/clients/{client_id}/communication-preferences/do-not-call/mark-completed",
        headers=manager_headers,
    )
    assert premature_complete.status_code == 200, premature_complete.text
    done = premature_complete.json()
    assert done["dnc_status"] == "completed"
    assert done["dnc_completed_at"] is not None
    assert done["dnc_followup_due_at"] is not None


def test_open_dnc_requires_consent(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    response = api_client.post(
        f"/api/v1/clients/{client_id}/communication-preferences/do-not-call/open-registry",
        headers=manager_headers,
    )
    assert response.status_code == 422
