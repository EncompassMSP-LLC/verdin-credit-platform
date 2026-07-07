"""Admin-gated fully autonomous bureau API filing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.autonomous_bureau_filing import get_autonomous_bureau_filing_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class FullyAutonomousBureauApiFilingStatus:
    enabled: bool
    ready: bool
    autonomous_bureau_filing_ready: bool
    blockers: tuple[str, ...]


def get_fully_autonomous_bureau_api_filing_status() -> FullyAutonomousBureauApiFilingStatus:
    api_filing_enabled = is_feature_enabled(FeatureFlag.ENABLE_FULLY_AUTONOMOUS_BUREAU_API_FILING)
    filing_status = get_autonomous_bureau_filing_status()

    blockers: list[str] = []
    if not api_filing_enabled:
        blockers.append("ENABLE_FULLY_AUTONOMOUS_BUREAU_API_FILING is false")
    if api_filing_enabled and not filing_status.ready:
        blockers.extend(filing_status.blockers)

    enabled = api_filing_enabled and filing_status.enabled
    return FullyAutonomousBureauApiFilingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        autonomous_bureau_filing_ready=filing_status.ready,
        blockers=tuple(blockers),
    )
