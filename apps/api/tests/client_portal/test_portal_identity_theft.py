"""Portal identity-theft confirmation endpoint tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def _create_client(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    email: str,
    display_name: str | None = None,
) -> str:
    payload = sample_client_payload(
        display_name=display_name or f"Portal Identity Client {uuid.uuid4().hex[:6]}",
        email=email,
    )
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_portal_user(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
    *,
    email: str,
) -> None:
    response = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201, response.text


def _portal_login(api_client: TestClient, email: str) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
            "title": f"Identity theft portal case {uuid.uuid4().hex[:6]}",
            "client_id": client_id,
            "client_name": client_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_portal_identity_theft_center_and_confirmation(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"portal-idtheft-{uuid.uuid4().hex[:8]}@test.example"
    display_name = f"Portal ID Theft {uuid.uuid4().hex[:6]}"
    client_id = _create_client(
        api_client,
        manager_headers,
        email=email,
        display_name=display_name,
    )
    _provision_portal_user(api_client, manager_headers, client_id, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name=display_name,
    )
    portal_headers = _portal_login(api_client, email)

    center = api_client.get(
        f"/api/v1/portal/cases/{case_id}/identity-theft-center",
        headers=portal_headers,
    )
    assert center.status_code == 200, center.text
    body = center.json()
    assert body["case_id"] == case_id
    assert "attestation_text" in body
    assert "identity_theft" in body["confirmation_options"]

    blocked = api_client.post(
        f"/api/v1/portal/cases/{case_id}/identity-theft/account-reviews",
        headers=portal_headers,
        json={
            "confirmation": "identity_theft",
            "attestation_accepted": False,
            "creditor_name": "Fraud Bank",
            "account_number_masked": "****9999",
            "tradeline_index": 0,
            "detection_source": "CONSUMER_CONFIRMATION",
            "confidence": 1.0,
        },
    )
    assert blocked.status_code == 422, blocked.text

    confirmed = api_client.post(
        f"/api/v1/portal/cases/{case_id}/identity-theft/account-reviews",
        headers=portal_headers,
        json={
            "confirmation": "identity_theft",
            "attestation_accepted": True,
            "creditor_name": "Fraud Bank",
            "account_number_masked": "****9999",
            "tradeline_index": 0,
            "detection_source": "CONSUMER_CONFIRMATION",
            "confidence": 1.0,
        },
    )
    assert confirmed.status_code == 201, confirmed.text
    review = confirmed.json()
    assert review["consumer_confirmation"] == "identity_theft"
    assert review["issue_type"] == "CONFIRMED_IDENTITY_THEFT_CLAIM"
    assert review["legal_path"] == "FCRA_605B"
    assert review["ordinary_dispute_locked"] is True
    assert review["attestation_accepted"] is True

    center_after = api_client.get(
        f"/api/v1/portal/cases/{case_id}/identity-theft-center",
        headers=portal_headers,
    )
    assert center_after.status_code == 200, center_after.text
    after = center_after.json()
    assert after["incident"] is not None
    assert len(after["account_reviews"]) >= 1


def test_portal_identity_theft_hidden_for_other_client_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email_a = f"portal-a-{uuid.uuid4().hex[:8]}@test.example"
    email_b = f"portal-b-{uuid.uuid4().hex[:8]}@test.example"
    name_a = f"Portal Client A {uuid.uuid4().hex[:6]}"
    name_b = f"Portal Client B {uuid.uuid4().hex[:6]}"
    client_a = _create_client(api_client, manager_headers, email=email_a, display_name=name_a)
    client_b = _create_client(api_client, manager_headers, email=email_b, display_name=name_b)
    _provision_portal_user(api_client, manager_headers, client_a, email=email_a)
    _provision_portal_user(api_client, manager_headers, client_b, email=email_b)
    case_b = _create_case(
        api_client,
        manager_headers,
        client_id=client_b,
        client_name=name_b,
    )
    portal_a = _portal_login(api_client, email_a)

    response = api_client.get(
        f"/api/v1/portal/cases/{case_b}/identity-theft-center",
        headers=portal_a,
    )
    assert response.status_code == 404
