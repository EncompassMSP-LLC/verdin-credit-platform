"""Stripe charge retry feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.billing.dependencies import require_stripe_live_tax_api_enabled


def require_stripe_charge_retry_enabled() -> None:
    require_stripe_live_tax_api_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_STRIPE_CHARGE_RETRY):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe charge retry is not enabled",
        )
