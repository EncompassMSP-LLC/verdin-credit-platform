"""Native mobile passkey client feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.mobile_passkey_readiness_dependencies import (
    require_mobile_passkey_readiness_enabled,
)


def require_native_mobile_passkey_client_enabled() -> None:
    require_mobile_passkey_readiness_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_NATIVE_MOBILE_PASSKEY_CLIENT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Native mobile passkey client is not enabled",
        )
