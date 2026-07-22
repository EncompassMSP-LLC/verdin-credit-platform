"""Mortgage partner feature-flag dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_mortgage_partner_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_MORTGAGE_PARTNER):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mortgage Partner Edition is not enabled",
        )
