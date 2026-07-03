"""Stripe billing adapter unit tests."""

import hashlib
import hmac
import json
import time

import pytest

from api.core.feature_flags import FeatureFlag
from api.core.stripe_billing import (
    BillingNotReadyError,
    StripeBillingSettings,
    get_billing_status,
    require_billing_ready,
    verify_stripe_webhook_signature,
)


def test_verify_stripe_webhook_signature_valid() -> None:
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_1"}).encode()
    timestamp = int(time.time())
    signed = f"{timestamp}.{payload.decode()}".encode()
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    header = f"t={timestamp},v1={digest}"
    assert verify_stripe_webhook_signature(payload, header, secret=secret) is True


def test_require_billing_ready_raises_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "false")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_stripe_billing_settings.cache_clear()
    with pytest.raises(BillingNotReadyError):
        require_billing_ready()


def test_get_billing_status_blockers() -> None:
    settings = StripeBillingSettings(stripe_secret_key=None, stripe_webhook_secret=None)

    def fake_feature_enabled(flag: FeatureFlag) -> bool:
        return flag == FeatureFlag.ENABLE_BILLING

    from api.core import stripe_billing

    original = stripe_billing.is_feature_enabled
    stripe_billing.is_feature_enabled = fake_feature_enabled  # type: ignore[method-assign]
    try:
        status = get_billing_status(settings)
    finally:
        stripe_billing.is_feature_enabled = original

    assert status.ready is False
    assert any("STRIPE_SECRET_KEY" in blocker for blocker in status.blockers)
