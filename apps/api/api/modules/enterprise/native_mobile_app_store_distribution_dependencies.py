"""Native mobile app store distribution feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.native_mobile_passkey_client_dependencies import (
    require_native_mobile_passkey_client_enabled,
)


def require_native_mobile_app_store_distribution_enabled() -> None:
    require_native_mobile_passkey_client_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_NATIVE_MOBILE_APP_STORE_DISTRIBUTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Native mobile app store distribution is not enabled",
        )
