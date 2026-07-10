"""Operator-gated unsupervised autonomous filing loop scaffold integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_bureau_refiling import _prepare_filed_autonomous_bureau_filing_run


def _prepare_executed_fully_autonomous_bureau_api_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    account_id, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )
    submit = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={"api_filing_summary": "Parent fully autonomous API filing for unsupervised loop"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    approve = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "executed"
    return account_id, run_id


def test_unsupervised_autonomous_filing_loops_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/unsupervised-autonomous-filing-loops/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_unsupervised_autonomous_filing_loops_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/unsupervised-autonomous-filing-loops/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["fully_autonomous_bureau_api_filing_ready"] is True
    assert payload["blockers"] == []


def test_submit_unsupervised_loop_requires_executed_api_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )
    submit_parent = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={"api_filing_summary": "Pending — cannot start unsupervised loop yet"},
    )
    assert submit_parent.status_code == 200, submit_parent.text
    pending_run_id = submit_parent.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/{pending_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Attempt unsupervised loop before API filing executed"},
    )
    assert response.status_code == 409
    assert "not executed" in response.json()["detail"]


def test_submit_and_approve_unsupervised_autonomous_filing_loop_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    account_id, api_filing_run_id = _prepare_executed_fully_autonomous_bureau_api_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/{api_filing_run_id}/start",
        headers=manager_headers,
        json={
            "loop_summary": "Unsupervised autonomous filing loop after executed API filing",
            "loop_reference_id": "loop-ref-001",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["fully_autonomous_bureau_api_filing_run_id"] == api_filing_run_id
    assert run["account_id"] == account_id
    assert run["loop_reference_id"] == "loop-ref-001"

    approve = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None
    assert approved["timeline_event_id"] is not None

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "unsupervised_autonomous_filing_loop" for event in events)


def test_approve_unsupervised_loop_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    _, api_filing_run_id = _prepare_executed_fully_autonomous_bureau_api_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/{api_filing_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "Needs admin approval for unsupervised loop"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_start_unsupervised_loop_unknown_api_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/{uuid.uuid4()}/start",
        headers=manager_headers,
        json={"loop_summary": "Missing fully autonomous bureau API filing run"},
    )
    assert response.status_code == 404


def test_list_unsupervised_autonomous_filing_loop_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    unsupervised_autonomous_filing_loops_env: None,
) -> None:
    account_id, api_filing_run_id = _prepare_executed_fully_autonomous_bureau_api_filing_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/{api_filing_run_id}/start",
        headers=manager_headers,
        json={"loop_summary": "List test unsupervised autonomous filing loop run"},
    )

    response = api_client.get(
        f"/api/v1/compliance/unsupervised-autonomous-filing-loops/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
