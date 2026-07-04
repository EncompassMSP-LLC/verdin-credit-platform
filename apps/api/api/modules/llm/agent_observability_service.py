"""Agent observability service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.agent_observability import get_agent_observability_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.permissions import CASE_READ_ROLE, CASE_WRITE_ROLE
from api.modules.llm.agent_observability_models import AgentObservabilityRunStatus
from api.modules.llm.agent_observability_processor import run_agent_observability_scaffold
from api.modules.llm.agent_observability_repository import (
    AgentObservabilityRunListFilters,
    AgentObservabilityRunRepository,
)
from api.modules.llm.agent_observability_schemas import (
    AgentObservabilityRunListParams,
    AgentObservabilityRunRequest,
    AgentObservabilityRunResponse,
    AgentObservabilityRunResultResponse,
    AgentObservabilityStatusResponse,
)


class AgentObservabilityService:
    def __init__(
        self,
        run_repo: AgentObservabilityRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentObservabilityService:
        return cls(AgentObservabilityRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, CASE_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view agent observability runs",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to run agent observability scaffold",
            )

    def get_status_response(self) -> AgentObservabilityStatusResponse:
        return AgentObservabilityStatusResponse.from_status(get_agent_observability_status())

    async def list_runs(
        self,
        user: User,
        params: AgentObservabilityRunListParams,
    ) -> PaginatedResponse[AgentObservabilityRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            AgentObservabilityRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [AgentObservabilityRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def run_scaffold(
        self,
        user: User,
        body: AgentObservabilityRunRequest,
    ) -> AgentObservabilityRunResultResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        observability_status = get_agent_observability_status()
        if not observability_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent observability is not ready",
                    "blockers": list(observability_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await run_agent_observability_scaffold(
            session=self._session,
            organization_id=organization_id,
            agent_kind=body.agent_kind,
            case_id=body.case_id,
            performed_by_user_id=user.id,
        )
        if summary.run.status == AgentObservabilityRunStatus.FAILED:
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary.run.error_message or "Agent observability run failed",
            )
        await self._session.commit()
        return AgentObservabilityRunResultResponse(
            completed_at=summary.completed_at,
            run=AgentObservabilityRunResponse.from_model(summary.run),
        )
