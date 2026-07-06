"""Admin-gated Stripe charge retry integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.billing.test_stripe_live_tax_api import _prepare_calculated_tax_run


def _prepare_invoked_live_tax_api_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch,
) -> str:
    tax_run_id = _prepare_calculated_tax_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Invoke live Tax API before charge retry"},
    )
    assert submit.status_code == 200, submit.text
    live_tax_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/billing/live-tax-api/runs/{live_tax_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "invoked"
    return live_tax_run_id


def test_stripe_charge_retry_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/charge-retry/status", headers=admin_headers)
    assert response.status_code == 404


def test_stripe_charge_retry_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/charge-retry/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["live_tax_api_ready"] is True
    assert payload["blockers"] == []


def test_submit_stripe_charge_retry_requires_invoked_live_tax_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
    monkeypatch,
) -> None:
    tax_run_id = _prepare_calculated_tax_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Pending approval — cannot retry charge yet"},
    )
    assert submit.status_code == 200, submit.text
    live_tax_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=admin_headers,
        json={"retry_summary": "Attempt charge retry before live Tax API invoked"},
    )
    assert response.status_code == 409
    assert "not invoked" in response.json()["detail"]


def test_submit_and_approve_stripe_charge_retry_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
    monkeypatch,
) -> None:
    live_tax_run_id = _prepare_invoked_live_tax_api_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=admin_headers,
        json={"retry_summary": "Charge retry after live Tax API invocation"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["stripe_live_tax_api_run_id"] == live_tax_run_id

    approve = api_client.post(
        f"/api/v1/billing/charge-retry/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "retried"
    assert approved["retried_at"] is not None


def test_submit_stripe_charge_retry_unknown_live_tax_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{uuid.uuid4()}/retry",
        headers=admin_headers,
        json={"retry_summary": "Missing live Tax API run"},
    )
    assert response.status_code == 404


def test_submit_stripe_charge_retry_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    stripe_charge_retry_env: None,
    monkeypatch,
) -> None:
    live_tax_run_id = _prepare_invoked_live_tax_api_run(api_client, admin_headers, monkeypatch)
    response = api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=readonly_headers,
        json={"retry_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_stripe_charge_retry_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_charge_retry_env: None,
    monkeypatch,
) -> None:
    live_tax_run_id = _prepare_invoked_live_tax_api_run(api_client, admin_headers, monkeypatch)
    api_client.post(
        f"/api/v1/billing/charge-retry/live-tax-api-runs/{live_tax_run_id}/retry",
        headers=admin_headers,
        json={"retry_summary": "Listing test charge retry run"},
    )

    listing = api_client.get("/api/v1/billing/charge-retry/runs", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
