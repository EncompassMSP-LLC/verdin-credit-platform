"""Human-gated agent execution readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_observability import get_agent_observability_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentExecutionStatus:
    enabled: bool
    ready: bool
    observability_ready: bool
    blockers: tuple[str, ...]


def get_agent_execution_status() -> AgentExecutionStatus:
    observability_status = get_agent_observability_status()
    execution_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_EXECUTION)

    blockers: list[str] = []
    if not execution_enabled:
        blockers.append("ENABLE_AGENT_EXECUTION is false")
    if execution_enabled and not observability_status.ready:
        blockers.extend(observability_status.blockers)

    enabled = execution_enabled and observability_status.enabled
    return AgentExecutionStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        observability_ready=observability_status.ready,
        blockers=tuple(blockers),
    )
