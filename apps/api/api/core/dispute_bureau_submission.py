"""Admin-gated dispute bureau submission readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.dispute_filing_prep import get_dispute_filing_prep_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class DisputeBureauSubmissionStatus:
    enabled: bool
    ready: bool
    filing_prep_ready: bool
    blockers: tuple[str, ...]


def get_dispute_bureau_submission_status() -> DisputeBureauSubmissionStatus:
    submission_enabled = is_feature_enabled(FeatureFlag.ENABLE_DISPUTE_BUREAU_SUBMISSION)
    prep_status = get_dispute_filing_prep_status()

    blockers: list[str] = []
    if not submission_enabled:
        blockers.append("ENABLE_DISPUTE_BUREAU_SUBMISSION is false")
    if submission_enabled and not prep_status.ready:
        blockers.extend(prep_status.blockers)

    enabled = submission_enabled and prep_status.enabled
    return DisputeBureauSubmissionStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        filing_prep_ready=prep_status.ready,
        blockers=tuple(blockers),
    )
