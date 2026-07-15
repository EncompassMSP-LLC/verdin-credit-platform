"""API tests for FCRA §605B submission-readiness audit runs (operator-gated)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def _create_client(api_client: TestClient, headers: dict[str, str], *, email: str) -> str:
    payload = sample_client_payload(
        display_name=f"605B Readiness {uuid.uuid4().hex[:6]}",
        email=email,
    )
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_case(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    client_name: str,
) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "title": f"605B readiness case {uuid.uuid4().hex[:6]}",
            "client_id": client_id,
            "client_name": client_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _confirm_identity_theft(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
) -> None:
    confirm = api_client.post(
        f"/api/v1/cases/{case_id}/identity-theft/account-reviews",
        headers=headers,
        json={
            "confirmation": "identity_theft",
            "attestation_accepted": True,
            "bureau": "experian",
            "tradeline_index": 0,
            "match_key": f"fakebank|{uuid.uuid4().hex[:6]}",
            "creditor_name": "Fake Bank",
            "account_number_masked": "****9999",
            "detection_source": "TRADELINE_HEURISTIC",
            "confidence": 0.9,
        },
    )
    assert confirm.status_code == 201, confirm.text


def test_readiness_run_not_ready_before_confirmation(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"605b-readiness-empty-{uuid.uuid4().hex[:8]}@test.example"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name="Readiness Empty",
    )

    response = api_client.post(
        f"/api/v1/cases/{case_id}/identity-theft/605b-readiness-runs",
        headers=manager_headers,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["is_ready"] is False
    assert body["confirmed_count"] == 0
    assert any("confirmed" in reason.lower() for reason in body["blocking_reasons"])


def test_readiness_run_records_after_confirmation_and_latest(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"605b-readiness-ok-{uuid.uuid4().hex[:8]}@test.example"
    display_name = f"Readiness Ready {uuid.uuid4().hex[:6]}"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name=display_name,
    )
    _confirm_identity_theft(api_client, manager_headers, case_id=case_id)

    run = api_client.post(
        f"/api/v1/cases/{case_id}/identity-theft/605b-readiness-runs",
        headers=manager_headers,
    )
    assert run.status_code == 201, run.text
    run_body = run.json()
    assert run_body["confirmed_count"] == 1
    assert run_body["attestation_recorded"] is True
    assert "experian" in run_body["bureaus"]

    latest = api_client.get(
        f"/api/v1/cases/{case_id}/identity-theft/605b-readiness-runs/latest",
        headers=manager_headers,
    )
    assert latest.status_code == 200, latest.text
    assert latest.json()["id"] == run_body["id"]


def test_latest_readiness_run_404_when_none(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"605b-readiness-none-{uuid.uuid4().hex[:8]}@test.example"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name="Readiness None",
    )
    response = api_client.get(
        f"/api/v1/cases/{case_id}/identity-theft/605b-readiness-runs/latest",
        headers=manager_headers,
    )
    assert response.status_code == 404, response.text
