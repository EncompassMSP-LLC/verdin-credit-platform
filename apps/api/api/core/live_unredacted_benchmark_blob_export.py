"""Admin-gated live unredacted benchmark blob export readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.unredacted_cross_org_benchmark_export import (
    get_unredacted_cross_org_benchmark_export_status,
)


@dataclass(frozen=True)
class LiveUnredactedBenchmarkBlobExportStatus:
    enabled: bool
    ready: bool
    unredacted_export_ready: bool
    blockers: tuple[str, ...]


def get_live_unredacted_benchmark_blob_export_status() -> LiveUnredactedBenchmarkBlobExportStatus:
    blob_enabled = is_feature_enabled(FeatureFlag.ENABLE_LIVE_UNREDACTED_BENCHMARK_BLOB_EXPORT)
    parent_status = get_unredacted_cross_org_benchmark_export_status()

    blockers: list[str] = []
    if not blob_enabled:
        blockers.append("ENABLE_LIVE_UNREDACTED_BENCHMARK_BLOB_EXPORT is false")
    if blob_enabled and not parent_status.ready:
        blockers.extend(parent_status.blockers)

    enabled = blob_enabled and parent_status.enabled
    return LiveUnredactedBenchmarkBlobExportStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        unredacted_export_ready=parent_status.ready,
        blockers=tuple(blockers),
    )
