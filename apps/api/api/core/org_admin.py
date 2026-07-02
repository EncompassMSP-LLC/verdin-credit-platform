"""Organization admin status helpers."""

from api.modules.org_admin.schemas import OrgAdminStatusResponse

_ORG_ADMIN_CAPABILITIES = [
    "organization_summary",
    "api_key_lifecycle",
    "api_key_auth_middleware",
    "scoped_key_permissions",
    "key_revocation_audit",
]

_DEFERRED_CAPABILITIES = [
    "scim_provisioning",
    "billing_administration",
    "cross_org_admin_roles",
    "api_key_usage_analytics",
    "api_key_rate_limiting",
]


def get_org_admin_status() -> OrgAdminStatusResponse:
    return OrgAdminStatusResponse(
        org_admin_enabled=True,
        api_keys_enabled=True,
        capabilities=list(_ORG_ADMIN_CAPABILITIES),
        deferred_capabilities=list(_DEFERRED_CAPABILITIES),
    )
