"""Compliance feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_compliance_enforcement_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_COMPLIANCE_ENFORCEMENT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance enforcement is not enabled",
        )
