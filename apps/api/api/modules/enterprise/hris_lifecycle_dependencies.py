"""HRIS lifecycle sync feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.dependencies import require_hris_bidirectional_sync_enabled


def require_hris_lifecycle_sync_enabled() -> None:
    require_hris_bidirectional_sync_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_HRIS_LIFECYCLE_SYNC):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HRIS lifecycle sync is not enabled",
        )
