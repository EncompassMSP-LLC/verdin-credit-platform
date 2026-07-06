"""Bureau unsupervised re-filing feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.accounts.bureau_refiling_dependencies import require_bureau_refiling_enabled


def require_bureau_unsupervised_refiling_enabled() -> None:
    require_bureau_refiling_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_BUREAU_UNSUPERVISED_REFILING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bureau unsupervised re-filing is not enabled",
        )
