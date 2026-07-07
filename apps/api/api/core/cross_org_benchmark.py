"""Cross-org benchmark analytics readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class CrossOrgBenchmarkStatus:
    enabled: bool
    ready: bool
    blockers: tuple[str, ...]


def get_cross_org_benchmark_status() -> CrossOrgBenchmarkStatus:
    enabled = is_feature_enabled(FeatureFlag.ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS)
    blockers: list[str] = []
    if not enabled:
        blockers.append("ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS is false")
    return CrossOrgBenchmarkStatus(
        enabled=enabled, ready=enabled and not blockers, blockers=tuple(blockers)
    )
