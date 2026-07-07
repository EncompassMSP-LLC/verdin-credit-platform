"""Public OAuth developer portal readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.api_developer_portal import get_api_developer_portal_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class PublicOAuthDeveloperPortalStatus:
    enabled: bool
    ready: bool
    api_developer_portal_ready: bool
    blockers: tuple[str, ...]


def get_public_oauth_developer_portal_status() -> PublicOAuthDeveloperPortalStatus:
    public_enabled = is_feature_enabled(FeatureFlag.ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL)
    portal_status = get_api_developer_portal_status()

    blockers: list[str] = []
    if not public_enabled:
        blockers.append("ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL is false")
    if public_enabled and not portal_status.ready:
        blockers.extend(portal_status.blockers)

    enabled = public_enabled and portal_status.enabled
    return PublicOAuthDeveloperPortalStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        api_developer_portal_ready=portal_status.ready,
        blockers=tuple(blockers),
    )
