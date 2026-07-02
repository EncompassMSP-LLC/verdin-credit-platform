"""Enterprise identity gate API helpers."""

from api.core.enterprise_identity import (
    EnterpriseFeatureDisabledError,
    EnterpriseIdentityNotReadyError,
    EnterpriseIdentitySettings,
    EnterpriseIdentityStatus,
    evaluate_enterprise_identity_status,
    get_enterprise_identity_settings,
    require_enterprise_identity_ready,
)
from api.core.feature_flags import FeatureFlag, is_feature_enabled


def is_enterprise_feature_enabled() -> bool:
    return is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE)


def get_enterprise_identity_gate_status(
    settings: EnterpriseIdentitySettings | None = None,
) -> EnterpriseIdentityStatus:
    return evaluate_enterprise_identity_status(settings)


def require_enterprise_gateway(
    *,
    require_sso: bool = False,
    require_mfa: bool = False,
) -> EnterpriseIdentityStatus:
    return require_enterprise_identity_ready(
        get_enterprise_identity_settings(),
        require_sso=require_sso,
        require_mfa=require_mfa,
    )


__all__ = [
    "EnterpriseFeatureDisabledError",
    "EnterpriseIdentityNotReadyError",
    "EnterpriseIdentitySettings",
    "EnterpriseIdentityStatus",
    "get_enterprise_identity_gate_status",
    "is_enterprise_feature_enabled",
    "require_enterprise_gateway",
]
