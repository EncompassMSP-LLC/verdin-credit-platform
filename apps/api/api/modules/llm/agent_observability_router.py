"""Agent observability scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_observability_dependencies import require_agent_observability_enabled
from api.modules.llm.agent_observability_schemas import (
    AgentObservabilityRunListParams,
    AgentObservabilityRunRequest,
    AgentObservabilityRunResponse,
    AgentObservabilityRunResultResponse,
    AgentObservabilityStatusResponse,
)
from api.modules.llm.agent_observability_service import AgentObservabilityService

agent_observability_router = APIRouter(prefix="/agents", tags=["Agent Observability"])


def get_agent_observability_service(
    db: AsyncSession = Depends(get_db),
) -> AgentObservabilityService:
    return AgentObservabilityService.from_session(db)


@agent_observability_router.get("/status", response_model=AgentObservabilityStatusResponse)
async def get_agent_observability_status_endpoint(
    _: None = Depends(require_agent_observability_enabled),
    service: AgentObservabilityService = Depends(get_agent_observability_service),
) -> AgentObservabilityStatusResponse:
    return service.get_status_response()


@agent_observability_router.get(
    "/runs",
    response_model=PaginatedResponse[AgentObservabilityRunResponse],
)
async def list_agent_observability_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_agent_observability_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentObservabilityService = Depends(get_agent_observability_service),
) -> PaginatedResponse[AgentObservabilityRunResponse]:
    params = AgentObservabilityRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@agent_observability_router.post(
    "/run",
    response_model=AgentObservabilityRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def run_agent_observability_scaffold_endpoint(
    body: AgentObservabilityRunRequest,
    _: None = Depends(require_agent_observability_enabled),
    current_user: User = Depends(get_current_user),
    service: AgentObservabilityService = Depends(get_agent_observability_service),
) -> AgentObservabilityRunResultResponse:
    return await service.run_scaffold(current_user, body)
