"""Operator-gated bureau re-filing readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.autonomous_bureau_filing import get_autonomous_bureau_filing_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class BureauRefilingStatus:
    enabled: bool
    ready: bool
    autonomous_filing_ready: bool
    blockers: tuple[str, ...]


def get_bureau_refiling_status() -> BureauRefilingStatus:
    refiling_enabled = is_feature_enabled(FeatureFlag.ENABLE_BUREAU_REFILING)
    filing_status = get_autonomous_bureau_filing_status()

    blockers: list[str] = []
    if not refiling_enabled:
        blockers.append("ENABLE_BUREAU_REFILING is false")
    if refiling_enabled and not filing_status.ready:
        blockers.extend(filing_status.blockers)

    enabled = refiling_enabled and filing_status.enabled
    return BureauRefilingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        autonomous_filing_ready=filing_status.ready,
        blockers=tuple(blockers),
    )
