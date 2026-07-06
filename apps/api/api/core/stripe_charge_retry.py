"""Admin-gated Stripe charge retry readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_live_tax_api import get_stripe_live_tax_api_status


@dataclass(frozen=True)
class StripeChargeRetryStatus:
    enabled: bool
    ready: bool
    live_tax_api_ready: bool
    blockers: tuple[str, ...]


def get_stripe_charge_retry_status() -> StripeChargeRetryStatus:
    retry_enabled = is_feature_enabled(FeatureFlag.ENABLE_STRIPE_CHARGE_RETRY)
    live_tax_status = get_stripe_live_tax_api_status()

    blockers: list[str] = []
    if not retry_enabled:
        blockers.append("ENABLE_STRIPE_CHARGE_RETRY is false")
    if retry_enabled and not live_tax_status.ready:
        blockers.extend(live_tax_status.blockers)

    enabled = retry_enabled and live_tax_status.enabled
    return StripeChargeRetryStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        live_tax_api_ready=live_tax_status.ready,
        blockers=tuple(blockers),
    )
