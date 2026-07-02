"""Organization admin dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_org_admin_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization admin is not enabled",
        )
