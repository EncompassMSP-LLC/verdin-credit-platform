"""Admin-gated Stripe live Tax API readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_tax_calculation import get_stripe_tax_calculation_status


@dataclass(frozen=True)
class StripeLiveTaxApiStatus:
    enabled: bool
    ready: bool
    tax_calculation_ready: bool
    blockers: tuple[str, ...]


def get_stripe_live_tax_api_status() -> StripeLiveTaxApiStatus:
    live_tax_enabled = is_feature_enabled(FeatureFlag.ENABLE_STRIPE_LIVE_TAX_API)
    tax_status = get_stripe_tax_calculation_status()

    blockers: list[str] = []
    if not live_tax_enabled:
        blockers.append("ENABLE_STRIPE_LIVE_TAX_API is false")
    if live_tax_enabled and not tax_status.ready:
        blockers.extend(tax_status.blockers)

    enabled = live_tax_enabled and tax_status.enabled
    return StripeLiveTaxApiStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        tax_calculation_ready=tax_status.ready,
        blockers=tuple(blockers),
    )
