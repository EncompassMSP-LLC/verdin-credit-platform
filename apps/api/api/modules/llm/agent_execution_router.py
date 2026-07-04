"""Human-gated agent execution scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_execution_dependencies import require_agent_execution_enabled
from api.modules.llm.agent_execution_schemas import (
    AgentExecutionStatusResponse,
    AgentExecutionStepListParams,
    AgentExecutionStepResponse,
    AgentExecutionStepResultResponse,
    AgentExecutionStepSubmitRequest,
)
from api.modules.llm.agent_execution_service import AgentExecutionService

agent_execution_router = APIRouter(prefix="/execution", tags=["Agent Execution"])


def get_agent_execution_service(
    db: AsyncSession = Depends(get_db),
) -> AgentExecutionService:
    return AgentExecutionService.from_session(db)


@agent_execution_router.get("/status", response_model=AgentExecutionStatusResponse)
async def get_agent_execution_status_endpoint(
    _: None = Depends(require_agent_execution_enabled),
    service: AgentExecutionService = Depends(get_agent_execution_service),
) -> AgentExecutionStatusResponse:
    return service.get_status_response()


@agent_execution_router.get(
    "/steps",
    response_model=PaginatedResponse[AgentExecutionStepResponse],
)
async def list_agent_execution_steps(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_agent_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentExecutionService = Depends(get_agent_execution_service),
) -> PaginatedResponse[AgentExecutionStepResponse]:
    params = AgentExecutionStepListParams(page=page, page_size=page_size)
    return await service.list_steps(current_user, params)


@agent_execution_router.post(
    "/steps",
    response_model=AgentExecutionStepResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_agent_execution_step_endpoint(
    body: AgentExecutionStepSubmitRequest,
    _: None = Depends(require_agent_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentExecutionService = Depends(get_agent_execution_service),
) -> AgentExecutionStepResultResponse:
    return await service.submit_step(current_user, body)


@agent_execution_router.post(
    "/steps/{step_id}/approve",
    response_model=AgentExecutionStepResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_agent_execution_step_endpoint(
    step_id: uuid.UUID,
    _: None = Depends(require_agent_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentExecutionService = Depends(get_agent_execution_service),
) -> AgentExecutionStepResultResponse:
    return await service.approve_step(current_user, step_id)
