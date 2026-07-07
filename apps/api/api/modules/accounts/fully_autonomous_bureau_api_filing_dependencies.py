"""Fully autonomous bureau API filing feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.autonomous_bureau_filing_dependencies import (
    require_autonomous_bureau_filing_enabled,
)


def require_fully_autonomous_bureau_api_filing_enabled() -> None:
    require_autonomous_bureau_filing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_FULLY_AUTONOMOUS_BUREAU_API_FILING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fully autonomous bureau API filing is not enabled",
        )
