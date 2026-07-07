"""OAuth marketplace publishing feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.org_admin.dependencies import require_public_oauth_developer_portal_enabled


def require_oauth_marketplace_publishing_enabled() -> None:
    require_public_oauth_developer_portal_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_OAUTH_MARKETPLACE_PUBLISHING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth marketplace publishing is not enabled",
        )
