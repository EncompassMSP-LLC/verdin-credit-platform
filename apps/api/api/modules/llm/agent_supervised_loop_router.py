"""Human-gated agent supervised loop scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_supervised_loop_dependencies import (
    require_agent_supervised_loops_enabled,
)
from api.modules.llm.agent_supervised_loop_schemas import (
    AgentSupervisedLoopRunListParams,
    AgentSupervisedLoopRunResponse,
    AgentSupervisedLoopRunResultResponse,
    AgentSupervisedLoopStatusResponse,
    AgentSupervisedLoopSubmitRequest,
)
from api.modules.llm.agent_supervised_loop_service import AgentSupervisedLoopService

agent_supervised_loop_router = APIRouter(
    prefix="/supervised-loops", tags=["Agent Supervised Loops"]
)


def get_agent_supervised_loop_service(
    db: AsyncSession = Depends(get_db),
) -> AgentSupervisedLoopService:
    return AgentSupervisedLoopService.from_session(db)


@agent_supervised_loop_router.get("/status", response_model=AgentSupervisedLoopStatusResponse)
async def get_agent_supervised_loop_status_endpoint(
    _: None = Depends(require_agent_supervised_loops_enabled),
    service: AgentSupervisedLoopService = Depends(get_agent_supervised_loop_service),
) -> AgentSupervisedLoopStatusResponse:
    return service.get_status_response()


@agent_supervised_loop_router.get(
    "/runs",
    response_model=PaginatedResponse[AgentSupervisedLoopRunResponse],
)
async def list_agent_supervised_loop_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    _: None = Depends(require_agent_supervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentSupervisedLoopService = Depends(get_agent_supervised_loop_service),
) -> PaginatedResponse[AgentSupervisedLoopRunResponse]:
    params = AgentSupervisedLoopRunListParams(page=page, page_size=page_size, case_id=case_id)
    return await service.list_runs(current_user, params)


@agent_supervised_loop_router.post(
    "/tool-requests/{tool_invocation_request_id}/start",
    response_model=AgentSupervisedLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_agent_supervised_loop_run_endpoint(
    tool_invocation_request_id: uuid.UUID,
    body: AgentSupervisedLoopSubmitRequest,
    _: None = Depends(require_agent_supervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentSupervisedLoopService = Depends(get_agent_supervised_loop_service),
) -> AgentSupervisedLoopRunResultResponse:
    return await service.submit_from_tool_request(current_user, tool_invocation_request_id, body)


@agent_supervised_loop_router.post(
    "/runs/{run_id}/approve",
    response_model=AgentSupervisedLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_agent_supervised_loop_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_agent_supervised_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentSupervisedLoopService = Depends(get_agent_supervised_loop_service),
) -> AgentSupervisedLoopRunResultResponse:
    return await service.approve_run(current_user, run_id)
