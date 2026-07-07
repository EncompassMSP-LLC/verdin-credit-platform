"""Admin-gated fully autonomous bureau API filing scaffold integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_bureau_refiling import _prepare_filed_autonomous_bureau_filing_run


def test_fully_autonomous_bureau_api_filing_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/fully-autonomous-bureau-api-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_fully_autonomous_bureau_api_filing_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/fully-autonomous-bureau-api-filing/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["autonomous_bureau_filing_ready"] is True
    assert payload["blockers"] == []


def test_submit_fully_autonomous_bureau_api_filing_requires_filed_autonomous_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    from tests.compliance.test_autonomous_bureau_filing import _prepare_invoked_bureau_live_api_run

    _, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Pending approval — cannot execute fully autonomous API filing"},
    )
    assert submit.status_code == 200, submit.text
    filing_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={
            "api_filing_summary": "Attempt fully autonomous API filing before autonomous filing filed"
        },
    )
    assert response.status_code == 409
    assert "not filed" in response.json()["detail"]


def test_submit_and_approve_fully_autonomous_bureau_api_filing_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    account_id, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={
            "api_filing_summary": "Fully autonomous bureau API filing after autonomous filing",
            "execution_reference_id": "exec-ref-001",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["autonomous_bureau_filing_run_id"] == filing_run_id
    assert run["account_id"] == account_id
    assert run["execution_reference_id"] == "exec-ref-001"

    approve = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "executed"
    assert approved["executed_at"] is not None
    assert approved["timeline_event_id"] is not None

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "fully_autonomous_bureau_api_filing" for event in events)


def test_approve_fully_autonomous_bureau_api_filing_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={"api_filing_summary": "Needs admin approval for fully autonomous API filing"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_execute_fully_autonomous_bureau_api_filing_unknown_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{uuid.uuid4()}/execute",
        headers=manager_headers,
        json={"api_filing_summary": "Missing autonomous bureau filing run"},
    )
    assert response.status_code == 404


def test_list_fully_autonomous_bureau_api_filing_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    fully_autonomous_bureau_api_filing_env: None,
) -> None:
    account_id, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/filing-runs/{filing_run_id}/execute",
        headers=manager_headers,
        json={"api_filing_summary": "List test fully autonomous bureau API filing run"},
    )

    response = api_client.get(
        f"/api/v1/compliance/fully-autonomous-bureau-api-filing/runs?account_id={account_id}",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
