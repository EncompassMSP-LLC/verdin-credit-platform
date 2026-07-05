"""Human-gated agent external tool invocation scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_tool_calling_dependencies import (
    require_agent_external_tool_calling_enabled,
)
from api.modules.llm.agent_tool_calling_schemas import (
    AgentExternalToolCallingStatusResponse,
    AgentToolInvocationRequestListParams,
    AgentToolInvocationRequestResponse,
    AgentToolInvocationRequestResultResponse,
    AgentToolInvocationSubmitRequest,
)
from api.modules.llm.agent_tool_calling_service import AgentToolCallingService

agent_tool_calling_router = APIRouter(prefix="/tool-calling", tags=["Agent Tool Calling"])


def get_agent_tool_calling_service(
    db: AsyncSession = Depends(get_db),
) -> AgentToolCallingService:
    return AgentToolCallingService.from_session(db)


@agent_tool_calling_router.get("/status", response_model=AgentExternalToolCallingStatusResponse)
async def get_agent_external_tool_calling_status_endpoint(
    _: None = Depends(require_agent_external_tool_calling_enabled),
    service: AgentToolCallingService = Depends(get_agent_tool_calling_service),
) -> AgentExternalToolCallingStatusResponse:
    return service.get_status_response()


@agent_tool_calling_router.get(
    "/requests",
    response_model=PaginatedResponse[AgentToolInvocationRequestResponse],
)
async def list_agent_tool_invocation_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    _: None = Depends(require_agent_external_tool_calling_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentToolCallingService = Depends(get_agent_tool_calling_service),
) -> PaginatedResponse[AgentToolInvocationRequestResponse]:
    params = AgentToolInvocationRequestListParams(page=page, page_size=page_size, case_id=case_id)
    return await service.list_requests(current_user, params)


@agent_tool_calling_router.post(
    "/requests",
    response_model=AgentToolInvocationRequestResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_agent_tool_invocation_request_endpoint(
    body: AgentToolInvocationSubmitRequest,
    _: None = Depends(require_agent_external_tool_calling_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentToolCallingService = Depends(get_agent_tool_calling_service),
) -> AgentToolInvocationRequestResultResponse:
    return await service.submit_request(current_user, body)


@agent_tool_calling_router.post(
    "/requests/{request_id}/approve",
    response_model=AgentToolInvocationRequestResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_agent_tool_invocation_request_endpoint(
    request_id: uuid.UUID,
    _: None = Depends(require_agent_external_tool_calling_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentToolCallingService = Depends(get_agent_tool_calling_service),
) -> AgentToolInvocationRequestResultResponse:
    return await service.approve_request(current_user, request_id)
