"""Admin-gated public OAuth marketplace listing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.oauth_marketplace_publishing import get_oauth_marketplace_publishing_status


@dataclass(frozen=True)
class PublicOAuthMarketplaceListingStatus:
    enabled: bool
    ready: bool
    oauth_marketplace_publishing_ready: bool
    blockers: tuple[str, ...]


def get_public_oauth_marketplace_listing_status() -> PublicOAuthMarketplaceListingStatus:
    listings_enabled = is_feature_enabled(FeatureFlag.ENABLE_PUBLIC_OAUTH_MARKETPLACE_LISTINGS)
    publishing_status = get_oauth_marketplace_publishing_status()

    blockers: list[str] = []
    if not listings_enabled:
        blockers.append("ENABLE_PUBLIC_OAUTH_MARKETPLACE_LISTINGS is false")
    if listings_enabled and not publishing_status.ready:
        blockers.extend(publishing_status.blockers)

    enabled = listings_enabled and publishing_status.enabled
    return PublicOAuthMarketplaceListingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        oauth_marketplace_publishing_ready=publishing_status.ready,
        blockers=tuple(blockers),
    )
