"""Organization admin dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_org_admin_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization admin is not enabled",
        )


def require_api_developer_portal_enabled() -> None:
    require_org_admin_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_API_DEVELOPER_PORTAL):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API developer portal is not enabled",
        )


def require_public_oauth_developer_portal_enabled() -> None:
    require_api_developer_portal_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public OAuth developer portal is not enabled",
        )
