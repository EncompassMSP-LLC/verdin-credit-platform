"""Billing usage metering integration tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.stripe_billing import get_stripe_billing_settings


@pytest.fixture
def usage_metering_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_BILLING_USAGE_METERING", "true")
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


def test_usage_summary_empty(
    api_client: TestClient,
    admin_headers: dict[str, str],
    usage_metering_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/usage/summary", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["metering_enabled"] is True
    assert payload["stripe_customer_configured"] is False
    assert payload["total_events"] == 0
    assert payload["metrics"] == []


def test_record_usage_event_and_summary(
    api_client: TestClient,
    admin_headers: dict[str, str],
    usage_metering_env: None,
) -> None:
    record = api_client.post(
        "/api/v1/billing/usage/events",
        headers=admin_headers,
        json={"metric_name": "api_requests", "quantity": 3, "source": "manual"},
    )
    assert record.status_code == 201, record.text
    assert record.json()["metric_name"] == "api_requests"
    assert record.json()["quantity"] == 3

    summary = api_client.get("/api/v1/billing/usage/summary", headers=admin_headers)
    assert summary.status_code == 200, summary.text
    payload = summary.json()
    assert payload["total_events"] == 1
    assert payload["metrics"] == [{"metric_name": "api_requests", "total_quantity": 3}]
    assert payload["first_recorded_at"] is not None
    assert payload["last_recorded_at"] is not None


def test_usage_metering_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/usage/summary", headers=admin_headers)
    assert response.status_code == 404


def test_record_usage_event_forbidden_for_read_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    readonly_headers: dict[str, str],
    usage_metering_env: None,
) -> None:
    response = api_client.post(
        "/api/v1/billing/usage/events",
        headers=readonly_headers,
        json={"metric_name": "api_requests", "quantity": 1},
    )
    assert response.status_code == 403
