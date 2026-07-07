"""Admin-gated OAuth marketplace publishing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.public_oauth_developer_portal import get_public_oauth_developer_portal_status


@dataclass(frozen=True)
class OAuthMarketplacePublishingStatus:
    enabled: bool
    ready: bool
    public_oauth_developer_portal_ready: bool
    blockers: tuple[str, ...]


def get_oauth_marketplace_publishing_status() -> OAuthMarketplacePublishingStatus:
    publishing_enabled = is_feature_enabled(FeatureFlag.ENABLE_OAUTH_MARKETPLACE_PUBLISHING)
    portal_status = get_public_oauth_developer_portal_status()

    blockers: list[str] = []
    if not publishing_enabled:
        blockers.append("ENABLE_OAUTH_MARKETPLACE_PUBLISHING is false")
    if publishing_enabled and not portal_status.ready:
        blockers.extend(portal_status.blockers)

    enabled = publishing_enabled and portal_status.enabled
    return OAuthMarketplacePublishingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        public_oauth_developer_portal_ready=portal_status.ready,
        blockers=tuple(blockers),
    )
