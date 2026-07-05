"""LLM dispute draft augment feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_llm_dispute_draft_augment_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_LLM):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM features are not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_LLM_DISPUTE_DRAFT_AUGMENT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM dispute draft augment is not enabled",
        )
