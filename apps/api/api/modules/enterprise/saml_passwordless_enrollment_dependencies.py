"""SAML passwordless enrollment feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.saml_automated_rotation_dependencies import (
    require_saml_automated_rotation_enabled,
)


def require_saml_passwordless_enrollment_enabled() -> None:
    require_saml_automated_rotation_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_SAML_PASSWORDLESS_ENROLLMENT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAML passwordless enrollment is not enabled",
        )
