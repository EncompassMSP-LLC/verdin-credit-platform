"""Dispute bureau submission feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_dispute_bureau_submission_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_DISPUTE_FILING_PREP):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute filing prep is not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_DISPUTE_BUREAU_SUBMISSION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute bureau submission is not enabled",
        )
