"""Operator-gated bureau re-filing scaffold integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_autonomous_bureau_filing import _prepare_invoked_bureau_live_api_run


def _prepare_filed_autonomous_bureau_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    account_id, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Autonomous filing before bureau re-filing"},
    )
    assert submit.status_code == 200, submit.text
    filing_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/runs/{filing_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "filed"
    return account_id, filing_run_id


def test_bureau_refiling_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    autonomous_bureau_filing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/bureau-refiling/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_bureau_refiling_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/bureau-refiling/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["autonomous_filing_ready"] is True
    assert payload["blockers"] == []


def test_submit_bureau_refiling_requires_filed_autonomous_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    _, live_api_run_id = _prepare_invoked_bureau_live_api_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/autonomous-bureau-filing/live-api-runs/{live_api_run_id}/file",
        headers=manager_headers,
        json={"filing_summary": "Pending approval — cannot refile yet"},
    )
    assert submit.status_code == 200, submit.text
    filing_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Attempt re-filing before autonomous filing approved"},
    )
    assert response.status_code == 409
    assert "not filed" in response.json()["detail"]


def test_submit_and_approve_bureau_refiling_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    account_id, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Bureau re-filing after autonomous filing approval"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["autonomous_bureau_filing_run_id"] == filing_run_id
    assert run["account_id"] == account_id

    approve = api_client.post(
        f"/api/v1/compliance/bureau-refiling/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "refiled"
    assert approved["timeline_event_id"] is not None

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "bureau_refiling" for event in events)


def test_submit_bureau_refiling_unknown_filing_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{uuid.uuid4()}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Missing autonomous filing run"},
    )
    assert response.status_code == 404


def test_approve_bureau_refiling_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Needs admin approval for re-filing"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/bureau-refiling/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_list_bureau_refiling_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "List test bureau re-filing run"},
    )

    response = api_client.get("/api/v1/compliance/bureau-refiling/runs", headers=manager_headers)
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
