"""Operator-gated bureau live API integration endpoint tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_dispute_bureau_submission import _prepare_filing_prep_run


def _prepare_submitted_bureau_submission_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    account_id, prep_run_id = _prepare_filing_prep_run(api_client, manager_headers, admin_headers)

    submit = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/prep-runs/{prep_run_id}/submit",
        headers=manager_headers,
        json={"submission_summary": "Submitted dispute for bureau live API scaffold"},
    )
    assert submit.status_code == 200, submit.text
    submission_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/runs/{submission_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "submitted"
    return account_id, submission_run_id


def test_bureau_live_api_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    dispute_bureau_submission_env: None,
) -> None:
    response = api_client.get("/api/v1/compliance/bureau-live-api/status", headers=manager_headers)
    assert response.status_code == 404


def test_bureau_live_api_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    response = api_client.get("/api/v1/compliance/bureau-live-api/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["bureau_submission_ready"] is True
    assert payload["blockers"] == []


def test_submit_bureau_live_api_requires_submitted_submission_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    account_id, prep_run_id = _prepare_filing_prep_run(api_client, manager_headers, admin_headers)
    submit = api_client.post(
        f"/api/v1/compliance/dispute-bureau-submission/prep-runs/{prep_run_id}/submit",
        headers=manager_headers,
        json={"submission_summary": "Pending approval — cannot invoke live API yet"},
    )
    assert submit.status_code == 200, submit.text
    submission_run_id = submit.json()["run"]["id"]
    assert account_id  # used by prep flow

    response = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Attempt live bureau API before submission approved"},
    )
    assert response.status_code == 409
    assert "not submitted" in response.json()["detail"]


def test_submit_and_approve_bureau_live_api_run_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    account_id, submission_run_id = _prepare_submitted_bureau_submission_run(
        api_client, manager_headers, admin_headers
    )

    invoke = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Invoke Equifax live API scaffold after submission"},
    )
    assert invoke.status_code == 200, invoke.text
    run = invoke.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["bureau_submission_run_id"] == submission_run_id
    assert run["account_id"] == account_id

    approve = api_client.post(
        f"/api/v1/compliance/bureau-live-api/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "invoked"
    assert approved["invoked_at"] is not None
    assert approved["timeline_event_id"] is not None
    assert approved["invocation_reference_id"] is not None
    assert approved["invocation_channel"] == "operator_approved"

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "bureau_live_api_invocation" for event in events)


def test_approve_bureau_live_api_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    _, submission_run_id = _prepare_submitted_bureau_submission_run(
        api_client, manager_headers, admin_headers
    )

    invoke = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Needs admin approval for live API invocation"},
    )
    assert invoke.status_code == 200, invoke.text
    run_id = invoke.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/bureau-live-api/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_invoke_bureau_live_api_unknown_submission_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{uuid.uuid4()}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Missing bureau submission run"},
    )
    assert response.status_code == 404


def test_list_bureau_live_api_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    account_id, submission_run_id = _prepare_submitted_bureau_submission_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "List test bureau live API run"},
    )

    response = api_client.get(
        f"/api/v1/compliance/bureau-live-api/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
