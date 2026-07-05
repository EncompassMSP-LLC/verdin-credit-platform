"""Admin-gated agent unsupervised loop service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.agent_unsupervised_loops import get_agent_unsupervised_loop_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.permissions import CASE_READ_ROLE, CASE_WRITE_ROLE
from api.modules.llm.agent_unsupervised_loop_processor import (
    approve_agent_unsupervised_loop_run,
    submit_agent_unsupervised_loop_run,
)
from api.modules.llm.agent_unsupervised_loop_repository import (
    AgentUnsupervisedLoopRunListFilters,
    AgentUnsupervisedLoopRunRepository,
)
from api.modules.llm.agent_unsupervised_loop_schemas import (
    AgentUnsupervisedLoopRunListParams,
    AgentUnsupervisedLoopRunResponse,
    AgentUnsupervisedLoopRunResultResponse,
    AgentUnsupervisedLoopStatusResponse,
    AgentUnsupervisedLoopSubmitRequest,
)


class AgentUnsupervisedLoopService:
    def __init__(
        self,
        run_repo: AgentUnsupervisedLoopRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentUnsupervisedLoopService:
        return cls(AgentUnsupervisedLoopRunRepository(session), session=session)

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
                detail="Insufficient permissions to view agent unsupervised loop runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit agent unsupervised loop runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve agent unsupervised loop runs",
            )

    def _require_ready(self) -> None:
        loop_status = get_agent_unsupervised_loop_status()
        if not loop_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Agent unsupervised loops are not ready",
                    "blockers": list(loop_status.blockers),
                },
            )

    def get_status_response(self) -> AgentUnsupervisedLoopStatusResponse:
        return AgentUnsupervisedLoopStatusResponse.from_status(get_agent_unsupervised_loop_status())

    async def list_runs(
        self,
        user: User,
        params: AgentUnsupervisedLoopRunListParams,
    ) -> PaginatedResponse[AgentUnsupervisedLoopRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            AgentUnsupervisedLoopRunListFilters(
                skip=skip,
                limit=params.page_size,
                case_id=params.case_id,
            ),
        )
        items = [AgentUnsupervisedLoopRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_supervised_run(
        self,
        user: User,
        agent_supervised_loop_run_id: uuid.UUID,
        body: AgentUnsupervisedLoopSubmitRequest,
    ) -> AgentUnsupervisedLoopRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_agent_unsupervised_loop_run(
                session=self._session,
                organization_id=organization_id,
                agent_supervised_loop_run_id=agent_supervised_loop_run_id,
                loop_summary=body.loop_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not completed" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return AgentUnsupervisedLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=AgentUnsupervisedLoopRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> AgentUnsupervisedLoopRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_agent_unsupervised_loop_run(
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
        return AgentUnsupervisedLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=AgentUnsupervisedLoopRunResponse.from_model(summary.run),
        )
