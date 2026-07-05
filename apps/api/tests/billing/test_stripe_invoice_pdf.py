"""Admin-gated Stripe invoice PDF generation integration tests."""

import time
import uuid
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from api.core.stripe_billing import StripeCustomerResult, StripeSubscriptionResult
from api.modules.billing.collection_models import BillingInvoiceCollectionRunKind


def _setup_billing_with_active_subscription(
    api_client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_customer",
        AsyncMock(return_value=StripeCustomerResult(customer_id="cus_pdf_test")),
    )
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_subscription",
        AsyncMock(
            return_value=StripeSubscriptionResult(
                subscription_id="sub_pdf_test",
                status="active",
                price_id="price_test_default",
                current_period_end=int(time.time()) + 3600,
            ),
        ),
    )
    setup = api_client.post("/api/v1/billing/setup", headers=admin_headers)
    assert setup.status_code == 201, setup.text
    subscribe = api_client.post("/api/v1/billing/subscribe", headers=admin_headers, json={})
    assert subscribe.status_code == 200, subscribe.text


def _run_completed_invoice_pdf_collection(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    collection = api_client.post(
        "/api/v1/billing/collection/run",
        headers=admin_headers,
        json={"run_kind": BillingInvoiceCollectionRunKind.INVOICE_PDF.value},
    )
    assert collection.status_code == 200, collection.text
    run = collection.json()["run"]
    assert run["status"] == "completed"
    assert run["invoices_pdf_generated"] == 1
    return run["id"]


def test_stripe_invoice_pdf_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    collection_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/invoice-pdf/status", headers=admin_headers)
    assert response.status_code == 404


def test_stripe_invoice_pdf_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/invoice-pdf/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["collection_ready"] is True
    assert payload["blockers"] == []


def test_submit_and_approve_stripe_invoice_pdf_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
    monkeypatch,
) -> None:
    _setup_billing_with_active_subscription(api_client, admin_headers, monkeypatch)
    collection_run_id = _run_completed_invoice_pdf_collection(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{collection_run_id}/generate",
        headers=admin_headers,
        json={"generation_summary": "Generate Stripe invoice PDF after operator review"},
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    assert submit.json()["run"]["status"] == "pending_approval"
    assert submit.json()["run"]["collection_run_id"] == collection_run_id

    approve = api_client.post(
        f"/api/v1/billing/invoice-pdf/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "generated"
    assert approve.json()["run"]["generated_at"] is not None


def test_submit_stripe_invoice_pdf_invalid_collection_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{uuid.uuid4()}/generate",
        headers=admin_headers,
        json={"generation_summary": "Should fail without collection run"},
    )
    assert response.status_code == 404


def test_submit_stripe_invoice_pdf_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
    monkeypatch,
) -> None:
    _setup_billing_with_active_subscription(api_client, admin_headers, monkeypatch)
    collection_run_id = _run_completed_invoice_pdf_collection(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{collection_run_id}/generate",
        headers=readonly_headers,
        json={"generation_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_stripe_invoice_pdf_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    stripe_invoice_pdf_env: None,
    monkeypatch,
) -> None:
    _setup_billing_with_active_subscription(api_client, admin_headers, monkeypatch)
    collection_run_id = _run_completed_invoice_pdf_collection(api_client, admin_headers)
    submit = api_client.post(
        f"/api/v1/billing/invoice-pdf/collection-runs/{collection_run_id}/generate",
        headers=admin_headers,
        json={"generation_summary": "Listing test PDF generation run"},
    )
    assert submit.status_code == 200, submit.text

    listing = api_client.get("/api/v1/billing/invoice-pdf/runs", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["collection_run_id"] == collection_run_id
