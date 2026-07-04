"""Batch document LLM summary feature gate."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_batch_llm_summaries_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_LLM):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM features are not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_BATCH_LLM_SUMMARIES):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch LLM document summaries are not enabled",
        )
