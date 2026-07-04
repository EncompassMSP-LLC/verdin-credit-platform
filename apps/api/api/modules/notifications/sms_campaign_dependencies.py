"""SMS marketing campaign feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_sms_marketing_campaigns_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_SMS_DELIVERY):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS delivery is not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_SMS_MARKETING_CAMPAIGNS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS marketing campaigns are not enabled",
        )
