"""SCIM provisioning readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.enterprise import get_enterprise_identity_gate_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class ScimProvisioningStatus:
    enabled: bool
    ready: bool
    bearer_token_configured: bool
    blockers: tuple[str, ...]


def get_scim_provisioning_settings() -> ScimProvisioningStatus:
    import os

    enterprise_enabled = is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE)
    scim_enabled = is_feature_enabled(FeatureFlag.ENABLE_SCIM_PROVISIONING)
    bearer_token_configured = bool(os.getenv("SCIM_PROVISIONING_BEARER_TOKEN", "").strip())

    blockers: list[str] = []
    if not enterprise_enabled:
        blockers.append("ENABLE_ENTERPRISE is false")
    if not scim_enabled:
        blockers.append("ENABLE_SCIM_PROVISIONING is false")

    identity = get_enterprise_identity_gate_status()
    if enterprise_enabled and not identity.sso_ready:
        blockers.append("Enterprise OIDC SSO is not configured")

    enabled = enterprise_enabled and scim_enabled
    ready = enabled and not blockers

    return ScimProvisioningStatus(
        enabled=enabled,
        ready=ready,
        bearer_token_configured=bearer_token_configured,
        blockers=tuple(blockers),
    )
