"""Agent arbitrary execution feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.llm.agent_unsupervised_loop_dependencies import (
    require_agent_unsupervised_loops_enabled,
)


def require_agent_arbitrary_execution_enabled() -> None:
    require_agent_unsupervised_loops_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_ARBITRARY_EXECUTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent arbitrary execution is not enabled",
        )
