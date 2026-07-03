"""Billing integration tests."""

import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.stripe_billing import (
    StripeCustomerResult,
    StripeSubscriptionResult,
    get_stripe_billing_settings,
)


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


def _stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed = f"{timestamp}.{payload.decode()}".encode()
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_billing_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
) -> None:
    response = api_client.get("/api/v1/billing/status", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["provider"] == "stripe"
    assert payload["default_price_id"] == "price_test_default"


def test_billing_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "false")
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()

    response = api_client.get("/api/v1/billing/status", headers=admin_headers)
    assert response.status_code == 404


def test_setup_and_subscribe_flow(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_customer",
        AsyncMock(return_value=StripeCustomerResult(customer_id="cus_test_1")),
    )
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_subscription",
        AsyncMock(
            return_value=StripeSubscriptionResult(
                subscription_id="sub_test_1",
                status="active",
                price_id="price_test_default",
                current_period_end=int(time.time()) + 3600,
            ),
        ),
    )

    setup = api_client.post("/api/v1/billing/setup", headers=admin_headers)
    assert setup.status_code == 201, setup.text
    assert setup.json()["stripe_customer_id"] == "cus_test_1"
    assert setup.json()["created"] is True

    setup_again = api_client.post("/api/v1/billing/setup", headers=admin_headers)
    assert setup_again.status_code == 201
    assert setup_again.json()["created"] is False

    subscribe = api_client.post("/api/v1/billing/subscribe", headers=admin_headers, json={})
    assert subscribe.status_code == 200, subscribe.text
    sub_payload = subscribe.json()
    assert sub_payload["stripe_subscription_id"] == "sub_test_1"
    assert sub_payload["subscription_status"] == "active"

    org_summary = api_client.get("/api/v1/org-admin/organization", headers=admin_headers)
    assert org_summary.status_code == 200
    billing = org_summary.json()["billing"]
    assert billing is not None
    assert billing["stripe_customer_id"] == "cus_test_1"
    assert billing["subscription_status"] == "active"


def test_stripe_webhook_updates_subscription(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.modules.billing.service.create_stripe_customer",
        AsyncMock(return_value=StripeCustomerResult(customer_id="cus_test_webhook")),
    )
    setup = api_client.post("/api/v1/billing/setup", headers=admin_headers)
    assert setup.status_code == 201

    event = {
        "id": "evt_test_1",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_webhook_1",
                "customer": "cus_test_webhook",
                "status": "past_due",
                "current_period_end": int(time.time()) + 7200,
                "items": {"data": [{"price": {"id": "price_webhook"}}]},
            },
        },
    }
    payload = json.dumps(event).encode()
    signature = _stripe_signature(payload, "whsec_test_secret")

    response = api_client.post(
        "/api/v1/billing/webhooks/stripe",
        content=payload,
        headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "processed"

    org_summary = api_client.get("/api/v1/org-admin/organization", headers=admin_headers)
    billing = org_summary.json()["billing"]
    assert billing["subscription_status"] == "past_due"
    assert billing["stripe_subscription_id"] == "sub_webhook_1"


def test_subscribe_requires_setup(
    api_client: TestClient,
    admin_headers: dict[str, str],
    billing_env: None,
) -> None:
    response = api_client.post("/api/v1/billing/subscribe", headers=admin_headers, json={})
    assert response.status_code == 404


def test_billing_setup_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    billing_env: None,
) -> None:
    response = api_client.post("/api/v1/billing/setup", headers=manager_headers)
    assert response.status_code == 403
