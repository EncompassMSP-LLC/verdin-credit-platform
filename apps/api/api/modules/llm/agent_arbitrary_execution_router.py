"""Admin-gated agent arbitrary execution scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_arbitrary_execution_dependencies import (
    require_agent_arbitrary_execution_enabled,
)
from api.modules.llm.agent_arbitrary_execution_schemas import (
    AgentArbitraryExecutionRunListParams,
    AgentArbitraryExecutionRunResponse,
    AgentArbitraryExecutionRunResultResponse,
    AgentArbitraryExecutionStatusResponse,
    AgentArbitraryExecutionSubmitRequest,
)
from api.modules.llm.agent_arbitrary_execution_service import AgentArbitraryExecutionService

agent_arbitrary_execution_router = APIRouter(
    prefix="/arbitrary-execution", tags=["Agent Arbitrary Execution"]
)


def get_agent_arbitrary_execution_service(
    db: AsyncSession = Depends(get_db),
) -> AgentArbitraryExecutionService:
    return AgentArbitraryExecutionService.from_session(db)


@agent_arbitrary_execution_router.get(
    "/status", response_model=AgentArbitraryExecutionStatusResponse
)
async def get_agent_arbitrary_execution_status_endpoint(
    _: None = Depends(require_agent_arbitrary_execution_enabled),
    service: AgentArbitraryExecutionService = Depends(get_agent_arbitrary_execution_service),
) -> AgentArbitraryExecutionStatusResponse:
    return service.get_status_response()


@agent_arbitrary_execution_router.get(
    "/runs",
    response_model=PaginatedResponse[AgentArbitraryExecutionRunResponse],
)
async def list_agent_arbitrary_execution_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    _: None = Depends(require_agent_arbitrary_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentArbitraryExecutionService = Depends(get_agent_arbitrary_execution_service),
) -> PaginatedResponse[AgentArbitraryExecutionRunResponse]:
    params = AgentArbitraryExecutionRunListParams(page=page, page_size=page_size, case_id=case_id)
    return await service.list_runs(current_user, params)


@agent_arbitrary_execution_router.post(
    "/unsupervised-runs/{agent_unsupervised_loop_run_id}/start",
    response_model=AgentArbitraryExecutionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_agent_arbitrary_execution_run_endpoint(
    agent_unsupervised_loop_run_id: uuid.UUID,
    body: AgentArbitraryExecutionSubmitRequest,
    _: None = Depends(require_agent_arbitrary_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentArbitraryExecutionService = Depends(get_agent_arbitrary_execution_service),
) -> AgentArbitraryExecutionRunResultResponse:
    return await service.submit_from_unsupervised_run(
        current_user, agent_unsupervised_loop_run_id, body
    )


@agent_arbitrary_execution_router.post(
    "/runs/{run_id}/approve",
    response_model=AgentArbitraryExecutionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_agent_arbitrary_execution_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_agent_arbitrary_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentArbitraryExecutionService = Depends(get_agent_arbitrary_execution_service),
) -> AgentArbitraryExecutionRunResultResponse:
    return await service.approve_run(current_user, run_id)
