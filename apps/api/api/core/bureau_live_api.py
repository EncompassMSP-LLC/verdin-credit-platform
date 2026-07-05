"""Operator-gated bureau live API integration readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.dispute_bureau_submission import get_dispute_bureau_submission_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class BureauLiveApiStatus:
    enabled: bool
    ready: bool
    bureau_submission_ready: bool
    blockers: tuple[str, ...]


def get_bureau_live_api_status() -> BureauLiveApiStatus:
    live_api_enabled = is_feature_enabled(FeatureFlag.ENABLE_BUREAU_LIVE_API)
    submission_status = get_dispute_bureau_submission_status()

    blockers: list[str] = []
    if not live_api_enabled:
        blockers.append("ENABLE_BUREAU_LIVE_API is false")
    if live_api_enabled and not submission_status.ready:
        blockers.extend(submission_status.blockers)

    enabled = live_api_enabled and submission_status.enabled
    return BureauLiveApiStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        bureau_submission_ready=submission_status.ready,
        blockers=tuple(blockers),
    )
