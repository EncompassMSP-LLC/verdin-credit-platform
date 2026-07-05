"""Admin-gated agent unsupervised loop readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_supervised_loops import get_agent_supervised_loop_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentUnsupervisedLoopStatus:
    enabled: bool
    ready: bool
    supervised_loops_ready: bool
    blockers: tuple[str, ...]


def get_agent_unsupervised_loop_status() -> AgentUnsupervisedLoopStatus:
    unsupervised_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_UNSUPERVISED_LOOPS)
    supervised_status = get_agent_supervised_loop_status()

    blockers: list[str] = []
    if not unsupervised_enabled:
        blockers.append("ENABLE_AGENT_UNSUPERVISED_LOOPS is false")
    if unsupervised_enabled and not supervised_status.ready:
        blockers.extend(supervised_status.blockers)

    enabled = unsupervised_enabled and supervised_status.enabled
    return AgentUnsupervisedLoopStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        supervised_loops_ready=supervised_status.ready,
        blockers=tuple(blockers),
    )
