"""Billing feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_billing_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_BILLING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing is not enabled",
        )
