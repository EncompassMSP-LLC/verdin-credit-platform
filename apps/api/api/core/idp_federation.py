"""Multi-IdP federation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.enterprise import get_enterprise_identity_gate_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.scim_provisioning import get_scim_provisioning_settings


@dataclass(frozen=True)
class IdpFederationStatus:
    enabled: bool
    ready: bool
    scim_provisioning_enabled: bool
    blockers: tuple[str, ...]


def get_idp_federation_status() -> IdpFederationStatus:
    enterprise_enabled = is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE)
    federation_enabled = is_feature_enabled(FeatureFlag.ENABLE_IDP_FEDERATION)
    scim_settings = get_scim_provisioning_settings()

    blockers: list[str] = []
    if not enterprise_enabled:
        blockers.append("ENABLE_ENTERPRISE is false")
    if not federation_enabled:
        blockers.append("ENABLE_IDP_FEDERATION is false")

    identity = get_enterprise_identity_gate_status()
    if enterprise_enabled and not identity.sso_ready:
        blockers.append("Enterprise OIDC SSO is not configured")

    enabled = enterprise_enabled and federation_enabled
    ready = enabled and not blockers

    return IdpFederationStatus(
        enabled=enabled,
        ready=ready,
        scim_provisioning_enabled=scim_settings.enabled,
        blockers=tuple(blockers),
    )
