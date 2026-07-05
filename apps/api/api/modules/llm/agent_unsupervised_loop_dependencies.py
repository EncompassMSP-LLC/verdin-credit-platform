"""Agent unsupervised loop feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.llm.agent_supervised_loop_dependencies import (
    require_agent_supervised_loops_enabled,
)


def require_agent_unsupervised_loops_enabled() -> None:
    require_agent_supervised_loops_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_AGENT_UNSUPERVISED_LOOPS):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent unsupervised loops are not enabled",
        )
