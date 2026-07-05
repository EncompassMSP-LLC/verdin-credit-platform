"""Admin-gated dispute bureau submission endpoint tests."""

from fastapi.testclient import TestClient

from tests.compliance.conftest import create_account, sample_case_id


def _prepare_filing_prep_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    case_id = sample_case_id(api_client, manager_headers)
    account_id = create_account(api_client, manager_headers, case_id)
    prep = api_client.post(
        f"/api/v1/compliance/dispute-filing/accounts/{account_id}/prep",
        headers=manager_headers,
        json={"prep_summary": "Prepared filing packet for bureau submission"},
    )
    assert prep.status_code == 200, prep.text
    prep_run_id = prep.json()["run"]["id"]
    approve = api_client.post(
        f"/api/v1/compliance/dispute-filing/runs/{prep_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    return account_id, prep_run_id


def test_dispute_bureau_submission_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    dispute_filing_prep_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/dispute-bureau-submission/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_dispute_bureau_submission_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    dispute_bureau_submission_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/dispute-bureau-submission/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["filing_prep_ready"] is True
    assert payload["blockers"] == []


def test_submit_and_approve_dispute_bureau_submission_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    dispute_bureau_submission_env: None,
) -> None:
    account_id, prep_run_id = _prepare_filing_prep_run(api_client, manager_headers, admin_headers)

    submit = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/prep-runs/{prep_run_id}/submit",
        headers=manager_headers,
        json={"submission_summary": "Submit prepared dispute to Equifax bureau scaffold"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    assert submit.json()["run"]["status"] == "pending_approval"
    assert submit.json()["run"]["filing_prep_run_id"] == prep_run_id
    assert submit.json()["run"]["account_id"] == account_id

    approve = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "submitted"
    assert approve.json()["run"]["submitted_at"] is not None


def test_submit_dispute_bureau_submission_forbidden_for_read_only(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    dispute_bureau_submission_env: None,
) -> None:
    _, prep_run_id = _prepare_filing_prep_run(api_client, manager_headers, admin_headers)
    response = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/prep-runs/{prep_run_id}/submit",
        headers=readonly_headers,
        json={"submission_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_dispute_bureau_submission_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    dispute_bureau_submission_env: None,
) -> None:
    account_id, prep_run_id = _prepare_filing_prep_run(api_client, manager_headers, admin_headers)
    submit = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/prep-runs/{prep_run_id}/submit",
        headers=manager_headers,
        json={"submission_summary": "Listing test submission run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get(
        f"/api/v1/compliance/dispute-bureau-submission/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["account_id"] == account_id
