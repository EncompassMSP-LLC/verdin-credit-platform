"""Operator-gated bureau unsupervised re-filing scaffold integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.compliance.test_bureau_refiling import _prepare_filed_autonomous_bureau_filing_run


def _prepare_refiled_bureau_refiling_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Bureau re-filing before unsupervised scaffold"},
    )
    assert submit.status_code == 200, submit.text
    refiling_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/bureau-refiling/runs/{refiling_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "refiled"
    account_id = approve.json()["run"]["account_id"]
    return account_id, refiling_run_id


def test_bureau_unsupervised_refiling_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_refiling_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/bureau-unsupervised-refiling/status",
        headers=manager_headers,
    )
    assert response.status_code == 404


def test_bureau_unsupervised_refiling_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/compliance/bureau-unsupervised-refiling/status",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["bureau_refiling_ready"] is True
    assert payload["blockers"] == []


def test_submit_bureau_unsupervised_refiling_requires_refiled_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    _, filing_run_id = _prepare_filed_autonomous_bureau_filing_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile",
        headers=manager_headers,
        json={"refiling_summary": "Pending approval — cannot start unsupervised re-filing yet"},
    )
    assert submit.status_code == 200, submit.text
    refiling_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/refiling-runs/{refiling_run_id}/start",
        headers=manager_headers,
        json={
            "refiling_summary": "Attempt unsupervised re-filing before bureau re-filing approved"
        },
    )
    assert response.status_code == 409
    assert "not refiled" in response.json()["detail"]


def test_submit_and_approve_bureau_unsupervised_refiling_with_timeline(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    account_id, refiling_run_id = _prepare_refiled_bureau_refiling_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/refiling-runs/{refiling_run_id}/start",
        headers=manager_headers,
        json={"refiling_summary": "Unsupervised bureau re-filing after operator re-filing"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["bureau_refiling_run_id"] == refiling_run_id
    assert run["account_id"] == account_id

    approve = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "unsupervised_refiled"
    assert approved["timeline_event_id"] is not None

    case_id = approved["case_id"]
    timeline = api_client.get(
        f"/api/v1/timeline?case_id={case_id}",
        headers=manager_headers,
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json()["items"]
    assert any(event["event_type"] == "bureau_unsupervised_refiling" for event in events)


def test_submit_bureau_unsupervised_refiling_unknown_refiling_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/refiling-runs/{uuid.uuid4()}/start",
        headers=manager_headers,
        json={"refiling_summary": "Missing bureau re-filing run"},
    )
    assert response.status_code == 404


def test_approve_bureau_unsupervised_refiling_forbidden_for_case_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    _, refiling_run_id = _prepare_refiled_bureau_refiling_run(
        api_client, manager_headers, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/refiling-runs/{refiling_run_id}/start",
        headers=manager_headers,
        json={"refiling_summary": "Needs admin approval for unsupervised re-filing"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/runs/{run_id}/approve",
        headers=manager_headers,
    )
    assert approve.status_code == 403


def test_list_bureau_unsupervised_refiling_runs(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    bureau_unsupervised_refiling_env: None,
) -> None:
    _, refiling_run_id = _prepare_refiled_bureau_refiling_run(
        api_client, manager_headers, admin_headers
    )
    api_client.post(
        f"/api/v1/compliance/bureau-unsupervised-refiling/refiling-runs/{refiling_run_id}/start",
        headers=manager_headers,
        json={"refiling_summary": "List test bureau unsupervised re-filing run"},
    )

    response = api_client.get(
        "/api/v1/compliance/bureau-unsupervised-refiling/runs",
        headers=manager_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] >= 1
