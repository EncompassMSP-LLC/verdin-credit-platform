"""Operator-gated bureau unsupervised re-filing readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.bureau_refiling import get_bureau_refiling_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class BureauUnsupervisedRefilingStatus:
    enabled: bool
    ready: bool
    bureau_refiling_ready: bool
    blockers: tuple[str, ...]


def get_bureau_unsupervised_refiling_status() -> BureauUnsupervisedRefilingStatus:
    unsupervised_enabled = is_feature_enabled(FeatureFlag.ENABLE_BUREAU_UNSUPERVISED_REFILING)
    refiling_status = get_bureau_refiling_status()

    blockers: list[str] = []
    if not unsupervised_enabled:
        blockers.append("ENABLE_BUREAU_UNSUPERVISED_REFILING is false")
    if unsupervised_enabled and not refiling_status.ready:
        blockers.extend(refiling_status.blockers)

    enabled = unsupervised_enabled and refiling_status.enabled
    return BureauUnsupervisedRefilingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        bureau_refiling_ready=refiling_status.ready,
        blockers=tuple(blockers),
    )
