"""Billing invoice collection scaffold integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.stripe_billing import get_stripe_billing_settings
from api.modules.billing.collection_models import BillingInvoiceCollectionRunKind


@pytest.fixture
def collection_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICING", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICE_COLLECTION", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


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
