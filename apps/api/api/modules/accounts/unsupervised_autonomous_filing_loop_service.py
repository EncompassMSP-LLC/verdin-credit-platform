"""Operator-gated unsupervised autonomous filing loop service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.unsupervised_autonomous_filing_loops import (
    get_unsupervised_autonomous_filing_loop_status,
)
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.unsupervised_autonomous_filing_loop_processor import (
    approve_unsupervised_autonomous_filing_loop_run,
    submit_unsupervised_autonomous_filing_loop_run,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_repository import (
    UnsupervisedAutonomousFilingLoopRunListFilters,
    UnsupervisedAutonomousFilingLoopRunRepository,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_schemas import (
    UnsupervisedAutonomousFilingLoopRunListParams,
    UnsupervisedAutonomousFilingLoopRunResponse,
    UnsupervisedAutonomousFilingLoopRunResultResponse,
    UnsupervisedAutonomousFilingLoopStatusResponse,
    UnsupervisedAutonomousFilingLoopSubmitRequest,
)
from api.modules.auth.models import User


class UnsupervisedAutonomousFilingLoopService:
    def __init__(
        self,
        run_repo: UnsupervisedAutonomousFilingLoopRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> UnsupervisedAutonomousFilingLoopService:
        return cls(UnsupervisedAutonomousFilingLoopRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view unsupervised autonomous filing loop runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Insufficient permissions to submit unsupervised autonomous filing loop runs"
                ),
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Insufficient permissions to approve unsupervised autonomous filing loop runs"
                ),
            )

    def _require_ready(self) -> None:
        loop_status = get_unsupervised_autonomous_filing_loop_status()
        if not loop_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Unsupervised autonomous filing loops are not ready",
                    "blockers": list(loop_status.blockers),
                },
            )

    def get_status_response(self) -> UnsupervisedAutonomousFilingLoopStatusResponse:
        return UnsupervisedAutonomousFilingLoopStatusResponse.from_status(
            get_unsupervised_autonomous_filing_loop_status()
        )

    async def list_runs(
        self,
        user: User,
        params: UnsupervisedAutonomousFilingLoopRunListParams,
    ) -> PaginatedResponse[UnsupervisedAutonomousFilingLoopRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            UnsupervisedAutonomousFilingLoopRunListFilters(
                skip=skip,
                limit=params.page_size,
                account_id=params.account_id,
            ),
        )
        items = [UnsupervisedAutonomousFilingLoopRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_api_filing_run(
        self,
        user: User,
        fully_autonomous_bureau_api_filing_run_id: uuid.UUID,
        body: UnsupervisedAutonomousFilingLoopSubmitRequest,
    ) -> UnsupervisedAutonomousFilingLoopRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_unsupervised_autonomous_filing_loop_run(
                session=self._session,
                organization_id=organization_id,
                fully_autonomous_bureau_api_filing_run_id=fully_autonomous_bureau_api_filing_run_id,
                loop_summary=body.loop_summary,
                loop_reference_id=body.loop_reference_id,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not executed" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return UnsupervisedAutonomousFilingLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=UnsupervisedAutonomousFilingLoopRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> UnsupervisedAutonomousFilingLoopRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_unsupervised_autonomous_filing_loop_run(
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
        return UnsupervisedAutonomousFilingLoopRunResultResponse(
            completed_at=summary.completed_at,
            run=UnsupervisedAutonomousFilingLoopRunResponse.from_model(summary.run),
        )
