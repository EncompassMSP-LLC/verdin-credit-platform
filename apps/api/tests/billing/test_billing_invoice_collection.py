"""Billing invoice collection scaffold integration tests."""

from fastapi.testclient import TestClient

from api.modules.billing.collection_models import BillingInvoiceCollectionRunKind


def test_collection_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    invoicing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/collection/status", headers=admin_headers)
    assert response.status_code == 404


def test_collection_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    collection_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/collection/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["invoicing_ready"] is True
    assert payload["blockers"] == []


def test_run_collection_without_billing_customer(
    api_client: TestClient,
    admin_headers: dict[str, str],
    collection_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/billing/collection/run",
        headers=admin_headers,
        json={"run_kind": BillingInvoiceCollectionRunKind.INVOICE_PDF.value},
    )
    assert response.status_code == 404
    assert "Billing customer" in response.json()["detail"]


def test_run_collection_requires_write_role(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    collection_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/billing/collection/run",
        headers=readonly_headers,
        json={"run_kind": BillingInvoiceCollectionRunKind.INVOICE_PDF.value},
    )
    assert response.status_code == 403


def test_list_collection_runs_empty(
    api_client: TestClient,
    admin_headers: dict[str, str],
    collection_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/collection/runs", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["items"] == []
    assert payload["total"] == 0
