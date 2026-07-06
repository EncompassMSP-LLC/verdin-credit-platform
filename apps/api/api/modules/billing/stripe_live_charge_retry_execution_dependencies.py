"""Stripe live charge retry execution feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.billing.stripe_charge_retry_dependencies import require_stripe_charge_retry_enabled


def require_stripe_live_charge_retry_execution_enabled() -> None:
    require_stripe_charge_retry_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe live charge retry execution is not enabled",
        )
