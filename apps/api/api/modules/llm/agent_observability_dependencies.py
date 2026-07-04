"""Agent observability feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_agent_observability_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_AI):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI features are not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_OBSERVABILITY):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent observability is not enabled",
        )
