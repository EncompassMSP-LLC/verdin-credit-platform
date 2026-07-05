"""Admin-gated Stripe tax calculation integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.billing.test_stripe_invoice_pdf import (
    _run_completed_invoice_pdf_collection,
    _setup_billing_with_active_subscription,
)


def _prepare_generated_invoice_pdf_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch,
) -> str:
    _setup_billing_with_active_subscription(api_client, admin_headers, monkeypatch)
    collection_run_id = _run_completed_invoice_pdf_collection(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{collection_run_id}/generate",
        headers=admin_headers,
        json={"generation_summary": "PDF ready for tax calculation scaffold"},
    )
    assert submit.status_code == 200, submit.text
    pdf_run_id = submit.json()["run"]["id"]

    approve = api_client.post(
        f"/api/v1/billing/invoice-pdf/runs/{pdf_run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "generated"
    return pdf_run_id


def test_stripe_tax_calculation_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/tax-calculation/status", headers=admin_headers)
    assert response.status_code == 404


def test_stripe_tax_calculation_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/tax-calculation/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["invoice_pdf_ready"] is True
    assert payload["blockers"] == []


def test_submit_stripe_tax_calculation_requires_generated_pdf_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
    monkeypatch,
) -> None:
    _setup_billing_with_active_subscription(api_client, admin_headers, monkeypatch)
    collection_run_id = _run_completed_invoice_pdf_collection(api_client, admin_headers)

    submit_pdf = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{collection_run_id}/generate",
        headers=admin_headers,
        json={"generation_summary": "Pending approval — cannot calculate tax yet"},
    )
    assert submit_pdf.status_code == 200, submit_pdf.text
    pdf_run_id = submit_pdf.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Tax calc before PDF approved"},
    )
    assert response.status_code == 409
    assert "not generated" in response.json()["detail"]


def test_submit_and_approve_stripe_tax_calculation_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
    monkeypatch,
) -> None:
    pdf_run_id = _prepare_generated_invoice_pdf_run(api_client, admin_headers, monkeypatch)

    submit = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Calculate Stripe tax after operator review"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    assert submit.json()["run"]["status"] == "pending_approval"
    assert submit.json()["run"]["invoice_pdf_run_id"] == pdf_run_id

    approve = api_client.post(
        f"/api/v1/billing/tax-calculation/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "calculated"
    assert approve.json()["run"]["calculated_at"] is not None


def test_submit_stripe_tax_calculation_unknown_pdf_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{uuid.uuid4()}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Missing PDF run"},
    )
    assert response.status_code == 404


def test_submit_stripe_tax_calculation_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    stripe_tax_calculation_env: None,
    monkeypatch,
) -> None:
    pdf_run_id = _prepare_generated_invoice_pdf_run(api_client, admin_headers, monkeypatch)
    response = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=readonly_headers,
        json={"calculation_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_stripe_tax_calculation_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_tax_calculation_env: None,
    monkeypatch,
) -> None:
    pdf_run_id = _prepare_generated_invoice_pdf_run(api_client, admin_headers, monkeypatch)
    submit = api_client.post(
        f"/api/v1/billing/tax-calculation/pdf-runs/{pdf_run_id}/calculate",
        headers=admin_headers,
        json={"calculation_summary": "Listing test tax calculation run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get("/api/v1/billing/tax-calculation/runs", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
