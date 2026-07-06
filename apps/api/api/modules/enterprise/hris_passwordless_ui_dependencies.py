"""HRIS passwordless UI feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.saml_passwordless_enrollment_dependencies import (
    require_saml_passwordless_enrollment_enabled,
)


def require_hris_passwordless_ui_enabled() -> None:
    require_saml_passwordless_enrollment_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_HRIS_PASSWORDLESS_UI):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HRIS passwordless UI is not enabled",
        )
