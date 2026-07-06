"""Admin-gated Stripe live charge retry execution readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_charge_retry import get_stripe_charge_retry_status


@dataclass(frozen=True)
class StripeLiveChargeRetryExecutionStatus:
    enabled: bool
    ready: bool
    charge_retry_ready: bool
    blockers: tuple[str, ...]


def get_stripe_live_charge_retry_execution_status() -> StripeLiveChargeRetryExecutionStatus:
    execution_enabled = is_feature_enabled(FeatureFlag.ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION)
    retry_status = get_stripe_charge_retry_status()

    blockers: list[str] = []
    if not execution_enabled:
        blockers.append("ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION is false")
    if execution_enabled and not retry_status.ready:
        blockers.extend(retry_status.blockers)

    enabled = execution_enabled and retry_status.enabled
    return StripeLiveChargeRetryExecutionStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        charge_retry_ready=retry_status.ready,
        blockers=tuple(blockers),
    )
