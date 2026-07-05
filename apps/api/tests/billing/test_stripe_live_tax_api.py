"""Admin-gated Stripe live Tax API integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.billing.test_stripe_tax_calculation import _prepare_generated_invoice_pdf_run


def _prepare_calculated_tax_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch,
) -> str:
    pdf_run_id = _prepare_generated_invoice_pdf_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Tax calculated before live API invocation"},
    )
    assert submit.status_code == 200, submit.text
    tax_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/billing/tax-calculation/runs/{tax_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "calculated"
    return tax_run_id


def test_stripe_live_tax_api_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/live-tax-api/status", headers=admin_headers)
    assert response.status_code == 404


def test_stripe_live_tax_api_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/live-tax-api/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["tax_calculation_ready"] is True
    assert payload["blockers"] == []


def test_submit_stripe_live_tax_api_requires_calculated_tax_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
    monkeypatch,
) -> None:
    pdf_run_id = _prepare_generated_invoice_pdf_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Pending approval — cannot invoke live Tax API yet"},
    )
    assert submit.status_code == 200, submit.text
    tax_run_id = submit.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Attempt live Tax API before calculation approved"},
    )
    assert response.status_code == 409
    assert "not calculated" in response.json()["detail"]


def test_submit_and_approve_stripe_live_tax_api_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
    monkeypatch,
) -> None:
    tax_run_id = _prepare_calculated_tax_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Invoke Stripe Tax API after operator review"},
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["stripe_tax_calculation_run_id"] == tax_run_id

    approve = api_client.post(
        f"/api/v1/billing/live-tax-api/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "invoked"
    assert approved["invoked_at"] is not None


def test_submit_stripe_live_tax_api_unknown_tax_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{uuid.uuid4()}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Missing tax calculation run"},
    )
    assert response.status_code == 404


def test_submit_stripe_live_tax_api_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    stripe_live_tax_api_env: None,
    monkeypatch,
) -> None:
    tax_run_id = _prepare_calculated_tax_run(api_client, admin_headers, monkeypatch)
    response = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=readonly_headers,
        json={"invocation_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_stripe_live_tax_api_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_live_tax_api_env: None,
    monkeypatch,
) -> None:
    tax_run_id = _prepare_calculated_tax_run(api_client, admin_headers, monkeypatch)
    submit = api_client.post(
        f"/api/v1/billing/live-tax-api/tax-calculation-runs/{tax_run_id}/invoke",
        headers=admin_headers,
        json={"invocation_summary": "Listing test live Tax API run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get("/api/v1/billing/live-tax-api/runs", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
