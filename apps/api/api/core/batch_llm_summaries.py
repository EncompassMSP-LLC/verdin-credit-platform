"""Batch document LLM summary helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class BatchLlmSummaryStatus:
    enabled: bool
    ready: bool
    blockers: tuple[str, ...]


def get_batch_llm_summary_status() -> BatchLlmSummaryStatus:
    llm_enabled = is_feature_enabled(FeatureFlag.ENABLE_LLM)
    batch_enabled = is_feature_enabled(FeatureFlag.ENABLE_BATCH_LLM_SUMMARIES)

    blockers: list[str] = []
    if not llm_enabled:
        blockers.append("ENABLE_LLM is false")
    if not batch_enabled:
        blockers.append("ENABLE_BATCH_LLM_SUMMARIES is false")

    enabled = llm_enabled and batch_enabled
    return BatchLlmSummaryStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        blockers=tuple(blockers),
    )
