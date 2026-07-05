"""SMS deliverability dashboard feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.notifications.sms_campaign_dependencies import (
    require_sms_marketing_campaigns_enabled,
)


def require_sms_deliverability_dashboard_enabled() -> None:
    require_sms_marketing_campaigns_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_SMS_MARKETING_DELIVERY):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS marketing delivery is not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_SMS_DELIVERABILITY_DASHBOARD):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS deliverability dashboard is not enabled",
        )
