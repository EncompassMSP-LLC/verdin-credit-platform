"""Admin-gated agent arbitrary execution readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_unsupervised_loops import get_agent_unsupervised_loop_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentArbitraryExecutionStatus:
    enabled: bool
    ready: bool
    unsupervised_loops_ready: bool
    blockers: tuple[str, ...]


def get_agent_arbitrary_execution_status() -> AgentArbitraryExecutionStatus:
    arbitrary_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_ARBITRARY_EXECUTION)
    unsupervised_status = get_agent_unsupervised_loop_status()

    blockers: list[str] = []
    if not arbitrary_enabled:
        blockers.append("ENABLE_AGENT_ARBITRARY_EXECUTION is false")
    if arbitrary_enabled and not unsupervised_status.ready:
        blockers.extend(unsupervised_status.blockers)

    enabled = arbitrary_enabled and unsupervised_status.enabled
    return AgentArbitraryExecutionStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        unsupervised_loops_ready=unsupervised_status.ready,
        blockers=tuple(blockers),
    )
