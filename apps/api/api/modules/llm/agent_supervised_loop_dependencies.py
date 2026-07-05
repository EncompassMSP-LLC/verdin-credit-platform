"""Agent supervised loop feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.llm.agent_tool_calling_dependencies import (
    require_agent_external_tool_calling_enabled,
)


def require_agent_supervised_loops_enabled() -> None:
    require_agent_external_tool_calling_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_SUPERVISED_LOOPS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent supervised loops are not enabled",
        )
