"""Agent observability readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class AgentObservabilityStatus:
    enabled: bool
    ready: bool
    ai_enabled: bool
    blockers: tuple[str, ...]


def get_agent_observability_status() -> AgentObservabilityStatus:
    ai_enabled = is_feature_enabled(FeatureFlag.ENABLE_AI)
    observability_enabled = is_feature_enabled(FeatureFlag.ENABLE_AGENT_OBSERVABILITY)

    blockers: list[str] = []
    if not ai_enabled:
        blockers.append("ENABLE_AI is false")
    if not observability_enabled:
        blockers.append("ENABLE_AGENT_OBSERVABILITY is false")

    enabled = ai_enabled and observability_enabled
    return AgentObservabilityStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        ai_enabled=ai_enabled,
        blockers=tuple(blockers),
    )
