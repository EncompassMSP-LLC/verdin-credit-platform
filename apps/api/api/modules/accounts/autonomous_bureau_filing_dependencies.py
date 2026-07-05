"""Autonomous bureau filing feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.bureau_live_api_dependencies import require_bureau_live_api_enabled


def require_autonomous_bureau_filing_enabled() -> None:
    require_bureau_live_api_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AUTONOMOUS_BUREAU_FILING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autonomous bureau filing is not enabled",
        )
