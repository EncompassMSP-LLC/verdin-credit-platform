"""Compliance-gated dispute filing prep endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags


def sample_case_id(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Dispute Filing Prep Case", "client_name": "Prep Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_account(api_client: TestClient, headers: dict[str, str], case_id: str) -> str:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json={
            "case_id": case_id,
            "creditor_name": "Example Bank",
            "bureau": "equifax",
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "late_60",
            "account_number_masked": "****1234",
            "balance": "1500.00",
            "past_due_amount": "300.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def dispute_filing_prep_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_AI", "true")
    monkeypatch.setenv("ENABLE_AGENT_OBSERVABILITY", "true")
    monkeypatch.setenv("ENABLE_AGENT_EXECUTION", "true")
    monkeypatch.setenv("ENABLE_DISPUTE_FILING_PREP", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_dispute_filing_prep_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(
        "/api/v1/compliance/dispute-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_dispute_filing_prep_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    dispute_filing_prep_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/dispute-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["agent_execution_ready"] is True
    assert payload["blockers"] == []


def test_submit_and_approve_dispute_filing_prep_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    dispute_filing_prep_env: None,
) -> None:
    case_id = sample_case_id(api_client, manager_headers)
    account_id = create_account(api_client, manager_headers, case_id)

    submit = api_client.post(
        f"/api/v1/compliance/dispute-filing/accounts/{account_id}/prep",
        headers=manager_headers,
        json={"prep_summary": "Prepare Equifax tradeline dispute filing packet"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    assert submit.json()["run"]["status"] == "pending_approval"
    assert submit.json()["run"]["bureau_target"] == "equifax"

    approve = api_client.post(
        f"/api/v1/compliance/dispute-filing/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "prepared"
    assert approve.json()["run"]["approved_by_user_id"] is not None


def test_submit_dispute_filing_prep_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    dispute_filing_prep_env: None,
) -> None:
    case_id = sample_case_id(api_client, manager_headers)
    account_id = create_account(api_client, manager_headers, case_id)

    response = api_client.post(
        f"/api/v1/compliance/dispute-filing/accounts/{account_id}/prep",
        headers=readonly_headers,
        json={"prep_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_dispute_filing_prep_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    dispute_filing_prep_env: None,
) -> None:
    case_id = sample_case_id(api_client, manager_headers)
    account_id = create_account(api_client, manager_headers, case_id)
    submit = api_client.post(
        f"/api/v1/compliance/dispute-filing/accounts/{account_id}/prep",
        headers=manager_headers,
        json={"prep_summary": "Listing test prep run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get(
        f"/api/v1/compliance/dispute-filing/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["account_id"] == account_id
