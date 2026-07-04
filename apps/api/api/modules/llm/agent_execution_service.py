"""Human-gated agent execution service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.agent_execution import get_agent_execution_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.permissions import CASE_READ_ROLE, CASE_WRITE_ROLE
from api.modules.llm.agent_execution_models import AgentExecutionStepStatus
from api.modules.llm.agent_execution_processor import (
    approve_agent_execution_step,
    submit_agent_execution_step,
)
from api.modules.llm.agent_execution_repository import (
    AgentExecutionStepListFilters,
    AgentExecutionStepRepository,
)
from api.modules.llm.agent_execution_schemas import (
    AgentExecutionStatusResponse,
    AgentExecutionStepListParams,
    AgentExecutionStepResponse,
    AgentExecutionStepResultResponse,
    AgentExecutionStepSubmitRequest,
)


class AgentExecutionService:
    def __init__(
        self,
        step_repo: AgentExecutionStepRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._steps = step_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentExecutionService:
        return cls(AgentExecutionStepRepository(session), session=session)

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
                detail="Insufficient permissions to view agent execution steps",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit agent execution steps",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve agent execution steps",
            )

    def get_status_response(self) -> AgentExecutionStatusResponse:
        return AgentExecutionStatusResponse.from_status(get_agent_execution_status())

    async def list_steps(
        self,
        user: User,
        params: AgentExecutionStepListParams,
    ) -> PaginatedResponse[AgentExecutionStepResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        skip = (params.page - 1) * params.page_size
        steps, total = await self._steps.list_steps(
            organization_id,
            AgentExecutionStepListFilters(skip=skip, limit=params.page_size),
        )
        items = [AgentExecutionStepResponse.from_model(step) for step in steps]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_step(
        self,
        user: User,
        body: AgentExecutionStepSubmitRequest,
    ) -> AgentExecutionStepResultResponse:
        self._require_submit(user)
        organization_id = self._require_organization(user)
        execution_status = get_agent_execution_status()
        if not execution_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent execution is not ready",
                    "blockers": list(execution_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await submit_agent_execution_step(
            session=self._session,
            organization_id=organization_id,
            agent_kind=body.agent_kind,
            step_summary=body.step_summary,
            case_id=body.case_id,
            requested_by_user_id=user.id,
        )
        if summary.step.status == AgentExecutionStepStatus.FAILED:
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary.step.error_message or "Agent execution step submission failed",
            )
        await self._session.commit()
        return AgentExecutionStepResultResponse(
            completed_at=summary.completed_at,
            step=AgentExecutionStepResponse.from_model(summary.step),
        )

    async def approve_step(
        self,
        user: User,
        step_id: uuid.UUID,
    ) -> AgentExecutionStepResultResponse:
        self._require_approve(user)
        organization_id = self._require_organization(user)
        execution_status = get_agent_execution_status()
        if not execution_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent execution is not ready",
                    "blockers": list(execution_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_agent_execution_step(
                session=self._session,
                organization_id=organization_id,
                step_id=step_id,
                approved_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT
                if "not pending approval" in detail
                else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return AgentExecutionStepResultResponse(
            completed_at=summary.completed_at,
            step=AgentExecutionStepResponse.from_model(summary.step),
        )
