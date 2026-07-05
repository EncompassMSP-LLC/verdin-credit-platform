"""Human-gated agent supervised loop readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_external_tool_calling import get_agent_external_tool_calling_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentSupervisedLoopStatus:
    enabled: bool
    ready: bool
    tool_calling_ready: bool
    blockers: tuple[str, ...]


def get_agent_supervised_loop_status() -> AgentSupervisedLoopStatus:
    loop_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_SUPERVISED_LOOPS)
    tool_status = get_agent_external_tool_calling_status()

    blockers: list[str] = []
    if not loop_enabled:
        blockers.append("ENABLE_AGENT_SUPERVISED_LOOPS is false")
    if loop_enabled and not tool_status.ready:
        blockers.extend(tool_status.blockers)

    enabled = loop_enabled and tool_status.enabled
    return AgentSupervisedLoopStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        tool_calling_ready=tool_status.ready,
        blockers=tuple(blockers),
    )
