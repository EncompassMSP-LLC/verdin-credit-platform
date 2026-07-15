"""API tests for auditable dispute response records (Phase 10 intake)."""

import uuid

from fastapi.testclient import TestClient

from tests.accounts.conftest import sample_account_payload


def _create_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
) -> str:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(case_id),
    )
    assert create.status_code == 201
    return create.json()["id"]


def _send_dispute_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    account_id: str,
) -> str:
    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    return letter_id


def test_record_dispute_response_persists_and_syncs_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={
            "outcome": "deleted",
            "response_method": "mail",
            "response_date": "2026-07-10",
            "notes": "Bureau deleted the tradeline after reinvestigation.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["outcome"] == "deleted"
    assert body["response_method"] == "mail"
    assert body["response_date"] == "2026-07-10"
    assert body["account_id"] == account_id
    assert body["recorded_at"] is not None

    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert account.json()["dispute_status"] == "deleted"
    assert account.json()["response_received"] is True

    listing = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
    )
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert listing.json()[0]["id"] == body["id"]


def test_record_dispute_response_no_response_does_not_mark_received(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "no_response", "response_method": "mail"},
    )

    assert response.status_code == 201
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert account.json()["response_received"] is False
    assert account.json()["dispute_status"] != "deleted"


def test_record_dispute_response_links_sent_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)
    letter_id = _send_dispute_letter(api_client, manager_headers, account_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={
            "outcome": "verified",
            "response_method": "portal",
            "dispute_letter_id": letter_id,
        },
    )

    assert response.status_code == 201
    assert response.json()["dispute_letter_id"] == letter_id


def test_record_dispute_response_unknown_letter_returns_404(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={
            "outcome": "verified",
            "dispute_letter_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


def test_record_dispute_response_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(api_client, manager_headers, sample_case_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=readonly_headers,
        json={"outcome": "verified"},
    )

    assert response.status_code == 403
