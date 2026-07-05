"""Admin-gated autonomous bureau filing readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.bureau_live_api import get_bureau_live_api_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AutonomousBureauFilingStatus:
    enabled: bool
    ready: bool
    bureau_live_api_ready: bool
    blockers: tuple[str, ...]


def get_autonomous_bureau_filing_status() -> AutonomousBureauFilingStatus:
    filing_enabled = is_feature_enabled(FeatureFlag.ENABLE_AUTONOMOUS_BUREAU_FILING)
    live_api_status = get_bureau_live_api_status()

    blockers: list[str] = []
    if not filing_enabled:
        blockers.append("ENABLE_AUTONOMOUS_BUREAU_FILING is false")
    if filing_enabled and not live_api_status.ready:
        blockers.extend(live_api_status.blockers)

    enabled = filing_enabled and live_api_status.enabled
    return AutonomousBureauFilingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        bureau_live_api_ready=live_api_status.ready,
        blockers=tuple(blockers),
    )
