"""Admin-gated agent unsupervised loop scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_unsupervised_loop_dependencies import (
    require_agent_unsupervised_loops_enabled,
)
from api.modules.llm.agent_unsupervised_loop_schemas import (
    AgentUnsupervisedLoopRunListParams,
    AgentUnsupervisedLoopRunResponse,
    AgentUnsupervisedLoopRunResultResponse,
    AgentUnsupervisedLoopStatusResponse,
    AgentUnsupervisedLoopSubmitRequest,
)
from api.modules.llm.agent_unsupervised_loop_service import AgentUnsupervisedLoopService

agent_unsupervised_loop_router = APIRouter(
    prefix="/unsupervised-loops", tags=["Agent Unsupervised Loops"]
)


def get_agent_unsupervised_loop_service(
    db: AsyncSession = Depends(get_db),
) -> AgentUnsupervisedLoopService:
    return AgentUnsupervisedLoopService.from_session(db)


@agent_unsupervised_loop_router.get("/status", response_model=AgentUnsupervisedLoopStatusResponse)
async def get_agent_unsupervised_loop_status_endpoint(
    _: None = Depends(require_agent_unsupervised_loops_enabled),
    service: AgentUnsupervisedLoopService = Depends(get_agent_unsupervised_loop_service),
) -> AgentUnsupervisedLoopStatusResponse:
    return service.get_status_response()


@agent_unsupervised_loop_router.get(
    "/runs",
    response_model=PaginatedResponse[AgentUnsupervisedLoopRunResponse],
)
async def list_agent_unsupervised_loop_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    _: None = Depends(require_agent_unsupervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentUnsupervisedLoopService = Depends(get_agent_unsupervised_loop_service),
) -> PaginatedResponse[AgentUnsupervisedLoopRunResponse]:
    params = AgentUnsupervisedLoopRunListParams(page=page, page_size=page_size, case_id=case_id)
    return await service.list_runs(current_user, params)


@agent_unsupervised_loop_router.post(
    "/supervised-runs/{agent_supervised_loop_run_id}/start",
    response_model=AgentUnsupervisedLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_agent_unsupervised_loop_run_endpoint(
    agent_supervised_loop_run_id: uuid.UUID,
    body: AgentUnsupervisedLoopSubmitRequest,
    _: None = Depends(require_agent_unsupervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentUnsupervisedLoopService = Depends(get_agent_unsupervised_loop_service),
) -> AgentUnsupervisedLoopRunResultResponse:
    return await service.submit_from_supervised_run(
        current_user, agent_supervised_loop_run_id, body
    )


@agent_unsupervised_loop_router.post(
    "/runs/{run_id}/approve",
    response_model=AgentUnsupervisedLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_agent_unsupervised_loop_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_agent_unsupervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentUnsupervisedLoopService = Depends(get_agent_unsupervised_loop_service),
) -> AgentUnsupervisedLoopRunResultResponse:
    return await service.approve_run(current_user, run_id)
