"""Dispute filing prep feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_dispute_filing_prep_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_EXECUTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent execution is not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_DISPUTE_FILING_PREP):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute filing prep is not enabled",
        )
