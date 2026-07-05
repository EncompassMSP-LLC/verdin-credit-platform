"""Bureau live API integration feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.dispute_bureau_submission_dependencies import (
    require_dispute_bureau_submission_enabled,
)


def require_bureau_live_api_enabled() -> None:
    require_dispute_bureau_submission_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_BUREAU_LIVE_API):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bureau live API integration is not enabled",
        )
