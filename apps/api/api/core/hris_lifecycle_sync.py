"""Admin-gated HRIS lifecycle sync readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.hris_bidirectional_sync import get_hris_bidirectional_sync_status


@dataclass(frozen=True)
class HrisLifecycleSyncStatus:
    enabled: bool
    ready: bool
    hris_sync_ready: bool
    blockers: tuple[str, ...]


def get_hris_lifecycle_sync_status() -> HrisLifecycleSyncStatus:
    lifecycle_enabled = is_feature_enabled(FeatureFlag.ENABLE_HRIS_LIFECYCLE_SYNC)
    sync_status = get_hris_bidirectional_sync_status()

    blockers: list[str] = []
    if not lifecycle_enabled:
        blockers.append("ENABLE_HRIS_LIFECYCLE_SYNC is false")
    if lifecycle_enabled and not sync_status.ready:
        blockers.extend(sync_status.blockers)

    enabled = lifecycle_enabled and sync_status.enabled
    return HrisLifecycleSyncStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        hris_sync_ready=sync_status.ready,
        blockers=tuple(blockers),
    )
