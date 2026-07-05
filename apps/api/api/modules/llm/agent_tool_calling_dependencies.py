"""Agent external tool calling feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.llm.agent_execution_dependencies import require_agent_execution_enabled


def require_agent_external_tool_calling_enabled() -> None:
    require_agent_execution_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_EXTERNAL_TOOL_CALLING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent external tool calling is not enabled",
        )
