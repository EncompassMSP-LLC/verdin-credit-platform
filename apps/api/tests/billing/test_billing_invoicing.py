"""Billing invoicing and dunning scaffold integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.stripe_billing import get_stripe_billing_settings
from api.modules.billing.invoicing_models import BillingInvoicingRunKind


@pytest.fixture
def invoicing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICING", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


def test_invoicing_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/invoicing/status", headers=admin_headers)
    assert response.status_code == 404


def test_invoicing_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    invoicing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/invoicing/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["billing_ready"] is True
    assert payload["blockers"] == []


def test_run_invoicing_without_billing_customer(
    api_client: TestClient,
    admin_headers: dict[str, str],
    invoicing_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/billing/invoicing/run",
        headers=admin_headers,
        json={"run_kind": BillingInvoicingRunKind.INVOICE_CYCLE.value},
    )
    assert response.status_code == 404
    assert "Billing customer" in response.json()["detail"]


def test_run_invoicing_requires_write_role(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    invoicing_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/billing/invoicing/run",
        headers=readonly_headers,
        json={"run_kind": BillingInvoicingRunKind.INVOICE_CYCLE.value},
    )
    assert response.status_code == 403


def test_list_invoicing_runs_empty(
    api_client: TestClient,
    admin_headers: dict[str, str],
    invoicing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/invoicing/runs", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["items"] == []
    assert payload["total"] == 0
