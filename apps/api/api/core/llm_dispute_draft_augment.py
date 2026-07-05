"""LLM dispute draft augment readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.llm import get_llm_gate_status


@dataclass(frozen=True)
class LlmDisputeDraftAugmentStatus:
    enabled: bool
    ready: bool
    llm_ready: bool
    blockers: tuple[str, ...]


def get_llm_dispute_draft_augment_status() -> LlmDisputeDraftAugmentStatus:
    augment_enabled = is_feature_enabled(FeatureFlag.ENABLE_LLM_DISPUTE_DRAFT_AUGMENT)
    llm_status = get_llm_gate_status()

    blockers: list[str] = []
    if not augment_enabled:
        blockers.append("ENABLE_LLM_DISPUTE_DRAFT_AUGMENT is false")
    if not llm_status.feature_enabled:
        blockers.append("ENABLE_LLM is false")
    if augment_enabled and llm_status.feature_enabled and not llm_status.ready:
        blockers.extend(llm_status.blockers)

    enabled = augment_enabled and llm_status.feature_enabled
    return LlmDisputeDraftAugmentStatus(
        enabled=enabled,
        ready=enabled and llm_status.ready,
        llm_ready=llm_status.ready,
        blockers=tuple(blockers),
    )
