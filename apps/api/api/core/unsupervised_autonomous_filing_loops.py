"""Operator-gated unsupervised autonomous filing loop helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.fully_autonomous_bureau_api_filing import (
    get_fully_autonomous_bureau_api_filing_status,
)


@dataclass(frozen=True)
class UnsupervisedAutonomousFilingLoopStatus:
    enabled: bool
    ready: bool
    fully_autonomous_bureau_api_filing_ready: bool
    blockers: tuple[str, ...]


def get_unsupervised_autonomous_filing_loop_status() -> UnsupervisedAutonomousFilingLoopStatus:
    loops_enabled = is_feature_enabled(FeatureFlag.ENABLE_UNSUPERVISED_AUTONOMOUS_FILING_LOOPS)
    api_filing_status = get_fully_autonomous_bureau_api_filing_status()

    blockers: list[str] = []
    if not loops_enabled:
        blockers.append("ENABLE_UNSUPERVISED_AUTONOMOUS_FILING_LOOPS is false")
    if loops_enabled and not api_filing_status.ready:
        blockers.extend(api_filing_status.blockers)

    enabled = loops_enabled and api_filing_status.enabled
    return UnsupervisedAutonomousFilingLoopStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        fully_autonomous_bureau_api_filing_ready=api_filing_status.ready,
        blockers=tuple(blockers),
    )
