"""Compliance-gated dispute filing prep readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_execution import get_agent_execution_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class DisputeFilingPrepStatus:
    enabled: bool
    ready: bool
    agent_execution_ready: bool
    blockers: tuple[str, ...]


def get_dispute_filing_prep_status() -> DisputeFilingPrepStatus:
    prep_enabled = is_feature_enabled(FeatureFlag.ENABLE_DISPUTE_FILING_PREP)
    execution_status = get_agent_execution_status()

    blockers: list[str] = []
    if not prep_enabled:
        blockers.append("ENABLE_DISPUTE_FILING_PREP is false")
    if prep_enabled and not execution_status.ready:
        blockers.extend(execution_status.blockers)

    enabled = prep_enabled and execution_status.enabled
    return DisputeFilingPrepStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        agent_execution_ready=execution_status.ready,
        blockers=tuple(blockers),
    )
