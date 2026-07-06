"""Operator-gated bureau unsupervised re-filing service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.bureau_unsupervised_refiling import get_bureau_unsupervised_refiling_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.bureau_unsupervised_refiling_processor import (
    approve_bureau_unsupervised_refiling_run,
    submit_bureau_unsupervised_refiling_run,
)
from api.modules.accounts.bureau_unsupervised_refiling_repository import (
    BureauUnsupervisedRefilingRunListFilters,
    BureauUnsupervisedRefilingRunRepository,
)
from api.modules.accounts.bureau_unsupervised_refiling_schemas import (
    BureauUnsupervisedRefilingRunListParams,
    BureauUnsupervisedRefilingRunResponse,
    BureauUnsupervisedRefilingRunResultResponse,
    BureauUnsupervisedRefilingStatusResponse,
    BureauUnsupervisedRefilingSubmitRequest,
)
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.auth.models import User


class BureauUnsupervisedRefilingService:
    def __init__(
        self,
        run_repo: BureauUnsupervisedRefilingRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> BureauUnsupervisedRefilingService:
        return cls(BureauUnsupervisedRefilingRunRepository(session), session=session)

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
                detail="Insufficient permissions to view bureau unsupervised re-filing runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit bureau unsupervised re-filing runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve bureau unsupervised re-filing runs",
            )

    def _require_ready(self) -> None:
        unsupervised_status = get_bureau_unsupervised_refiling_status()
        if not unsupervised_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Bureau unsupervised re-filing is not ready",
                    "blockers": list(unsupervised_status.blockers),
                },
            )

    def get_status_response(self) -> BureauUnsupervisedRefilingStatusResponse:
        return BureauUnsupervisedRefilingStatusResponse.from_status(
            get_bureau_unsupervised_refiling_status()
        )

    async def list_runs(
        self,
        user: User,
        params: BureauUnsupervisedRefilingRunListParams,
    ) -> PaginatedResponse[BureauUnsupervisedRefilingRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            BureauUnsupervisedRefilingRunListFilters(
                skip=skip,
                limit=params.page_size,
                account_id=params.account_id,
            ),
        )
        items = [BureauUnsupervisedRefilingRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_refiling_run(
        self,
        user: User,
        bureau_refiling_run_id: uuid.UUID,
        body: BureauUnsupervisedRefilingSubmitRequest,
    ) -> BureauUnsupervisedRefilingRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_bureau_unsupervised_refiling_run(
                session=self._session,
                organization_id=organization_id,
                bureau_refiling_run_id=bureau_refiling_run_id,
                refiling_summary=body.refiling_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not refiled" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return BureauUnsupervisedRefilingRunResultResponse(
            completed_at=summary.completed_at,
            run=BureauUnsupervisedRefilingRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> BureauUnsupervisedRefilingRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_bureau_unsupervised_refiling_run(
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
        return BureauUnsupervisedRefilingRunResultResponse(
            completed_at=summary.completed_at,
            run=BureauUnsupervisedRefilingRunResponse.from_model(summary.run),
        )
