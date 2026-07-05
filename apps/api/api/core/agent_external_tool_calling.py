"""Human-gated agent external tool invocation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.agent_execution import get_agent_execution_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentExternalToolCallingStatus:
    enabled: bool
    ready: bool
    agent_execution_ready: bool
    blockers: tuple[str, ...]


def get_agent_external_tool_calling_status() -> AgentExternalToolCallingStatus:
    tool_calling_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_EXTERNAL_TOOL_CALLING)
    execution_status = get_agent_execution_status()

    blockers: list[str] = []
    if not tool_calling_enabled:
        blockers.append("ENABLE_AGENT_EXTERNAL_TOOL_CALLING is false")
    if tool_calling_enabled and not execution_status.ready:
        blockers.extend(execution_status.blockers)

    enabled = tool_calling_enabled and execution_status.enabled
    return AgentExternalToolCallingStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        agent_execution_ready=execution_status.ready,
        blockers=tuple(blockers),
    )
