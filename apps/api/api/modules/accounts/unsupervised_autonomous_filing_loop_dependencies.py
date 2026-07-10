"""Unsupervised autonomous filing loop feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.fully_autonomous_bureau_api_filing_dependencies import (
    require_fully_autonomous_bureau_api_filing_enabled,
)


def require_unsupervised_autonomous_filing_loops_enabled() -> None:
    require_fully_autonomous_bureau_api_filing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_UNSUPERVISED_AUTONOMOUS_FILING_LOOPS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unsupervised autonomous filing loops are not enabled",
        )
