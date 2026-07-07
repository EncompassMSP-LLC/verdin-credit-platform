"""Multi-IdP bulk provisioning feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.enterprise.hris_passwordless_ui_dependencies import (
    require_hris_passwordless_ui_enabled,
)


def require_bulk_idp_provisioning_enabled() -> None:
    require_hris_passwordless_ui_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_MULTI_IDP_BULK_PROVISIONING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Multi-IdP bulk provisioning is not enabled",
        )
