"""Admin-gated autonomous bureau filing scaffold integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_bureau_live_api import _prepare_submitted_bureau_submission_run


def _prepare_invoked_bureau_live_api_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    account_id, submission_run_id = _prepare_submitted_bureau_submission_run(
        api_client, manager_headers, admin_headers
    )

    invoke = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Invoke bureau live API before autonomous filing"},
    )
    assert invoke.status_code == 200, invoke.text
    live_api_run_id = invoke.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/bureau-live-api/runs/{live_api_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "invoked"
    return account_id, live_api_run_id


def test_autonomous_bureau_filing_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_live_api_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/autonomous-bureau-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_autonomous_bureau_filing_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/autonomous-bureau-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["bureau_live_api_ready"] is True
    assert payload["blockers"] == []


def test_submit_autonomous_bureau_filing_requires_invoked_live_api_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    account_id, submission_run_id = _prepare_submitted_bureau_submission_run(
        api_client, manager_headers, admin_headers
    )

    invoke = api_client.post(
        f"/api/v1/compliance/bureau-live-api/submission-runs/{submission_run_id}/invoke",
        headers=manager_headers,
        json={"invocation_summary": "Pending approval — cannot file autonomously yet"},
    )
    assert invoke.status_code == 200, invoke.text
    live_api_run_id = invoke.json()["run"]["id"]
    assert account_id

    response = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Attempt autonomous filing before live API invoked"},
    )
    assert response.status_code == 409
    assert "not invoked" in response.json()["detail"]


def test_submit_and_approve_autonomous_bureau_filing_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    account_id, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Autonomous bureau filing after live API invocation"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["bureau_live_api_run_id"] == live_api_run_id
    assert run["account_id"] == account_id

    approve = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "filed"
    assert approved["filed_at"] is not None
    assert approved["timeline_event_id"] is not None

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "autonomous_bureau_filing" for event in events)


def test_approve_autonomous_bureau_filing_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    _, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Needs admin approval for autonomous filing"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_file_autonomous_bureau_filing_unknown_live_api_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{uuid.uuid4()}/file",
        headers=manager_headers,
        json={"filing_summary": "Missing bureau live API run"},
    )
    assert response.status_code == 404


def test_list_autonomous_bureau_filing_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    account_id, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "List test autonomous bureau filing run"},
    )

    response = api_client.get(
        f"/api/v1/compliance/autonomous-bureau-filing/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
