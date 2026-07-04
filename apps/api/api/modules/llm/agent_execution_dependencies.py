"""Agent execution feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.llm.agent_observability_dependencies import require_agent_observability_enabled


def require_agent_execution_enabled() -> None:
    require_agent_observability_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_EXECUTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent execution is not enabled",
        )
