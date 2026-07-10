"""Public OAuth marketplace listing feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.org_admin.oauth_marketplace_publishing_dependencies import (
    require_oauth_marketplace_publishing_enabled,
)


def require_public_oauth_marketplace_listings_enabled() -> None:
    require_oauth_marketplace_publishing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_PUBLIC_OAUTH_MARKETPLACE_LISTINGS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public OAuth marketplace listings are not enabled",
        )
