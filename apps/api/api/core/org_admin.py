"""Organization admin status helpers."""

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.org_admin.schemas import OrgAdminStatusResponse

_ORG_ADMIN_CAPABILITIES = [
    "organization_summary",
    "api_key_lifecycle",
    "api_key_auth_middleware",
    "scoped_key_permissions",
    "key_revocation_audit",
    "billing_status",
]

_DEFERRED_CAPABILITIES = [
    "scim_provisioning",
    "cross_org_admin_roles",
    "api_key_usage_analytics",
    "api_key_rate_limiting",
    "billing_usage_metering",
    "api_key_rotation",
    "developer_portal",
]


def get_org_admin_status() -> OrgAdminStatusResponse:
    capabilities = list(_ORG_ADMIN_CAPABILITIES)
    deferred = list(_DEFERRED_CAPABILITIES)
    if is_feature_enabled(FeatureFlag.ENABLE_API_KEY_RATE_LIMIT):
        capabilities.append("api_key_rate_limiting")
        deferred.remove("api_key_rate_limiting")
    if is_feature_enabled(FeatureFlag.ENABLE_BILLING_USAGE_METERING):
        capabilities.append("billing_usage_metering")
        deferred.remove("billing_usage_metering")
    if is_feature_enabled(FeatureFlag.ENABLE_SCIM_PROVISIONING):
        capabilities.append("scim_provisioning")
        deferred.remove("scim_provisioning")
    if is_feature_enabled(FeatureFlag.ENABLE_API_DEVELOPER_PORTAL):
        capabilities.append("api_key_rotation")
        deferred.remove("api_key_rotation")
        capabilities.append("developer_portal")
        deferred.remove("developer_portal")

    return OrgAdminStatusResponse(
        org_admin_enabled=True,
        api_keys_enabled=True,
        capabilities=capabilities,
        deferred_capabilities=deferred,
    )
