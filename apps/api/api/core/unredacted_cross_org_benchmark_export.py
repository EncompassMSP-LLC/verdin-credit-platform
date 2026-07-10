"""Admin-gated unredacted cross-org benchmark export readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.cross_org_benchmark import get_cross_org_benchmark_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class UnredactedCrossOrgBenchmarkExportStatus:
    enabled: bool
    ready: bool
    cross_org_benchmark_ready: bool
    blockers: tuple[str, ...]


def get_unredacted_cross_org_benchmark_export_status() -> UnredactedCrossOrgBenchmarkExportStatus:
    export_enabled = is_feature_enabled(FeatureFlag.ENABLE_UNREDACTED_CROSS_ORG_BENCHMARK_EXPORT)
    benchmark_status = get_cross_org_benchmark_status()

    blockers: list[str] = []
    if not export_enabled:
        blockers.append("ENABLE_UNREDACTED_CROSS_ORG_BENCHMARK_EXPORT is false")
    if export_enabled and not benchmark_status.ready:
        blockers.extend(benchmark_status.blockers)

    enabled = export_enabled and benchmark_status.enabled
    return UnredactedCrossOrgBenchmarkExportStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        cross_org_benchmark_ready=benchmark_status.ready,
        blockers=tuple(blockers),
    )
