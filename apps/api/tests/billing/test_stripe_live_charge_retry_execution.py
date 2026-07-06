"""Admin-gated Stripe live charge retry execution integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.billing.test_stripe_charge_retry import _prepare_invoked_live_tax_api_run


def _prepare_retried_charge_retry_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch,
) -> str:
    live_tax_run_id = _prepare_invoked_live_tax_api_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=admin_headers,
        json={"retry_summary": "Charge retry before live execution scaffold"},
    )
    assert submit.status_code == 200, submit.text
    charge_retry_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/billing/charge-retry/runs/{charge_retry_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "retried"
    return charge_retry_run_id


def test_stripe_live_charge_retry_execution_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/billing/live-charge-retry/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_stripe_live_charge_retry_execution_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/billing/live-charge-retry/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["charge_retry_ready"] is True
    assert payload["blockers"] == []


def test_submit_stripe_live_charge_retry_execution_requires_retried_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
    monkeypatch,
) -> None:
    live_tax_run_id = _prepare_invoked_live_tax_api_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=admin_headers,
        json={"retry_summary": "Pending approval — cannot execute live charge retry yet"},
    )
    assert submit.status_code == 200, submit.text
    charge_retry_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/billing/live-charge-retry/charge-retry-runs/{charge_retry_run_id}/execute",
        headers=admin_headers,
        json={"execution_summary": "Attempt live execution before charge retry approved"},
    )
    assert response.status_code == 409
    assert "not retried" in response.json()["detail"]


def test_submit_and_approve_stripe_live_charge_retry_execution_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
    monkeypatch,
) -> None:
    charge_retry_run_id = _prepare_retried_charge_retry_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/live-charge-retry/charge-retry-runs/{charge_retry_run_id}/execute",
        headers=admin_headers,
        json={"execution_summary": "Live charge retry execution after retried scaffold"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["stripe_charge_retry_run_id"] == charge_retry_run_id

    approve = api_client.post(
        f"/api/v1/billing/live-charge-retry/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "executed"
    assert approved["executed_at"] is not None


def test_submit_stripe_live_charge_retry_execution_unknown_charge_retry_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/billing/live-charge-retry/charge-retry-runs/{uuid.uuid4()}/execute",
        headers=admin_headers,
        json={"execution_summary": "Missing charge retry run"},
    )
    assert response.status_code == 404


def test_submit_stripe_live_charge_retry_execution_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
    monkeypatch,
) -> None:
    charge_retry_run_id = _prepare_retried_charge_retry_run(api_client, admin_headers, monkeypatch)
    response = api_client.post(
        f"/api/v1/billing/live-charge-retry/charge-retry-runs/{charge_retry_run_id}/execute",
        headers=readonly_headers,
        json={"execution_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_stripe_live_charge_retry_execution_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_charge_retry_execution_env: None,
    monkeypatch,
) -> None:
    charge_retry_run_id = _prepare_retried_charge_retry_run(api_client, admin_headers, monkeypatch)
    api_client.post(
        f"/api/v1/billing/live-charge-retry/charge-retry-runs/{charge_retry_run_id}/execute",
        headers=admin_headers,
        json={"execution_summary": "Listing test live charge retry execution run"},
    )

    listing = api_client.get("/api/v1/billing/live-charge-retry/runs", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
