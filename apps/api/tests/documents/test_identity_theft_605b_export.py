"""API tests for FCRA §605B block packet export."""

from __future__ import annotations

import io
import uuid
import zipfile

from fastapi.testclient import TestClient

from tests.helpers.client_payload import sample_client_payload


def _create_client(api_client: TestClient, headers: dict[str, str], *, email: str) -> str:
    payload = sample_client_payload(
        display_name=f"605B Client {uuid.uuid4().hex[:6]}",
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
            "title": f"605B packet case {uuid.uuid4().hex[:6]}",
            "client_id": client_id,
            "client_name": client_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_605b_packet_requires_confirmed_identity_theft(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"605b-empty-{uuid.uuid4().hex[:8]}@test.example"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name="605B Empty",
    )
    response = api_client.get(
        f"/api/v1/cases/{case_id}/identity-theft/605b-packet.zip",
        headers=manager_headers,
    )
    assert response.status_code == 409, response.text


def test_605b_packet_export_after_confirmation(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    email = f"605b-ok-{uuid.uuid4().hex[:8]}@test.example"
    display_name = f"605B Ready {uuid.uuid4().hex[:6]}"
    client_id = _create_client(api_client, manager_headers, email=email)
    case_id = _create_case(
        api_client,
        manager_headers,
        client_id=client_id,
        client_name=display_name,
    )

    confirm = api_client.post(
        f"/api/v1/cases/{case_id}/identity-theft/account-reviews",
        headers=manager_headers,
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

    response = api_client.get(
        f"/api/v1/cases/{case_id}/identity-theft/605b-packet.zip",
        headers=manager_headers,
        params={"letter_format": "text"},
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/zip")
    assert "fcra-605b-block-packet-" in response.headers.get("content-disposition", "")

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = archive.namelist()
        assert "README.md" in names
        letter_paths = [name for name in names if name.startswith("letters/")]
        assert letter_paths
        letter = archive.read(letter_paths[0]).decode("utf-8")
        assert "Fake Bank" in letter
        assert "1681c-2" in letter or "605B" in letter
        readme = archive.read("README.md").decode("utf-8")
        assert "does **not** submit" in readme or "staff-mediated" in readme.lower()
