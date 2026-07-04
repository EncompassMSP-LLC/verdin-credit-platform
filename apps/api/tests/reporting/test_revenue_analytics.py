"""Revenue analytics reporting tests."""

import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.revenue_analytics import build_revenue_analytics, compute_revenue_readiness_score
from api.core.stripe_billing import (
    StripeCustomerResult,
    StripeSubscriptionResult,
    get_stripe_billing_settings,
)
from api.modules.billing.models import OrganizationBillingAccount, SubscriptionStatus


@pytest.fixture
def billing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


def test_compute_revenue_readiness_score() -> None:
    assert (
        compute_revenue_readiness_score(
            stripe_customer_configured=False,
            subscription_active=False,
            active_clients=0,
            portal_users=0,
        )
        == 0
    )
    assert (
        compute_revenue_readiness_score(
            stripe_customer_configured=True,
            subscription_active=True,
            active_clients=5,
            portal_users=2,
        )
        == 100
    )


def test_build_revenue_analytics_without_account() -> None:
    payload = build_revenue_analytics(
        billing_enabled=True,
        billing_ready=True,
        account=None,
        active_clients=0,
        portal_enabled_clients=0,
        portal_users=0,
    )
    assert payload["subscription_status"] == "none"
    assert payload["readiness_score"] == 0


def test_build_revenue_analytics_with_active_subscription() -> None:
    account = OrganizationBillingAccount(
        organization_id=__import__("uuid").uuid4(),
        stripe_customer_id="cus_test",
        stripe_subscription_id="sub_test",
        subscription_status=SubscriptionStatus.ACTIVE,
        price_id="price_test",
        current_period_end=datetime.now(UTC) + timedelta(days=10),
    )
    payload = build_revenue_analytics(
        billing_enabled=True,
        billing_ready=True,
        account=account,
        active_clients=3,
        portal_enabled_clients=2,
        portal_users=4,
    )
    assert payload["subscription_active"] is True
    assert payload["renewal_within_30_days"] is True
    assert payload["readiness_score"] == 100


def test_revenue_analytics_hidden_when_billing_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_enabled: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "false")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()

    response = api_client.get("/api/v1/reporting/revenue", headers=manager_headers)
    assert response.status_code == 404


def test_get_revenue_analytics_reporting(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    billing_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_customer",
        AsyncMock(return_value=StripeCustomerResult(customer_id="cus_rev_test")),
    )
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_subscription",
        AsyncMock(
            return_value=StripeSubscriptionResult(
                subscription_id="sub_rev_test",
                status="active",
                price_id="price_test_default",
                current_period_end=int(time.time()) + 20 * 24 * 3600,
            )
        ),
    )

    setup = api_client.post("/api/v1/billing/setup", headers=admin_headers)
    assert setup.status_code == 201, setup.text
    subscribe = api_client.post(
        "/api/v1/billing/subscribe",
        headers=admin_headers,
        json={},
    )
    assert subscribe.status_code == 200, subscribe.text

    response = api_client.get("/api/v1/reporting/revenue", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "generated_at" in payload
    analytics = payload["revenue_analytics"]
    assert analytics["billing_enabled"] is True
    assert analytics["stripe_customer_configured"] is True
    assert analytics["subscription_active"] is True
    assert analytics["readiness_score"] >= 70


def test_enterprise_reporting_includes_revenue_when_billing_enabled(
    billing_env: None,
) -> None:
    from api.core.enterprise_reporting import get_enterprise_reporting_status

    status = get_enterprise_reporting_status()
    assert "revenue_metrics" in status.capabilities
    assert "revenue_metrics" not in status.deferred_capabilities
