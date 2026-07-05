"""Human-gated agent supervised loop service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.agent_supervised_loops import get_agent_supervised_loop_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.permissions import CASE_READ_ROLE, CASE_WRITE_ROLE
from api.modules.llm.agent_supervised_loop_processor import (
    approve_agent_supervised_loop_run,
    submit_agent_supervised_loop_run,
)
from api.modules.llm.agent_supervised_loop_repository import (
    AgentSupervisedLoopRunListFilters,
    AgentSupervisedLoopRunRepository,
)
from api.modules.llm.agent_supervised_loop_schemas import (
    AgentSupervisedLoopRunListParams,
    AgentSupervisedLoopRunResponse,
    AgentSupervisedLoopRunResultResponse,
    AgentSupervisedLoopStatusResponse,
    AgentSupervisedLoopSubmitRequest,
)


class AgentSupervisedLoopService:
    def __init__(
        self,
        run_repo: AgentSupervisedLoopRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentSupervisedLoopService:
        return cls(AgentSupervisedLoopRunRepository(session), session=session)

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
                detail="Insufficient permissions to view agent supervised loop runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit agent supervised loop runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve agent supervised loop runs",
            )

    def _require_ready(self) -> None:
        loop_status = get_agent_supervised_loop_status()
        if not loop_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent supervised loops are not ready",
                    "blockers": list(loop_status.blockers),
                },
            )

    def get_status_response(self) -> AgentSupervisedLoopStatusResponse:
        return AgentSupervisedLoopStatusResponse.from_status(get_agent_supervised_loop_status())

    async def list_runs(
        self,
        user: User,
        params: AgentSupervisedLoopRunListParams,
    ) -> PaginatedResponse[AgentSupervisedLoopRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            AgentSupervisedLoopRunListFilters(
                skip=skip,
                limit=params.page_size,
                case_id=params.case_id,
            ),
        )
        items = [AgentSupervisedLoopRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_tool_request(
        self,
        user: User,
        tool_invocation_request_id: uuid.UUID,
        body: AgentSupervisedLoopSubmitRequest,
    ) -> AgentSupervisedLoopRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_agent_supervised_loop_run(
                session=self._session,
                organization_id=organization_id,
                tool_invocation_request_id=tool_invocation_request_id,
                loop_summary=body.loop_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not invoked" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return AgentSupervisedLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=AgentSupervisedLoopRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> AgentSupervisedLoopRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_agent_supervised_loop_run(
                session=self._session,
                organization_id=organization_id,
                run_id=run_id,
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
        return AgentSupervisedLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=AgentSupervisedLoopRunResponse.from_model(summary.run),
        )
