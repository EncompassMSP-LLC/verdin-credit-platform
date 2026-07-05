"""Admin-gated autonomous bureau filing service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.autonomous_bureau_filing import get_autonomous_bureau_filing_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.autonomous_bureau_filing_processor import (
    approve_autonomous_bureau_filing_run,
    submit_autonomous_bureau_filing_run,
)
from api.modules.accounts.autonomous_bureau_filing_repository import (
    AutonomousBureauFilingRunListFilters,
    AutonomousBureauFilingRunRepository,
)
from api.modules.accounts.autonomous_bureau_filing_schemas import (
    AutonomousBureauFilingRunListParams,
    AutonomousBureauFilingRunResponse,
    AutonomousBureauFilingRunResultResponse,
    AutonomousBureauFilingStatusResponse,
    AutonomousBureauFilingSubmitRequest,
)
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.auth.models import User


class AutonomousBureauFilingService:
    def __init__(
        self,
        run_repo: AutonomousBureauFilingRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> AutonomousBureauFilingService:
        return cls(AutonomousBureauFilingRunRepository(session), session=session)

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
                detail="Insufficient permissions to view autonomous bureau filing runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit autonomous bureau filing runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve autonomous bureau filing runs",
            )

    def _require_ready(self) -> None:
        filing_status = get_autonomous_bureau_filing_status()
        if not filing_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Autonomous bureau filing is not ready",
                    "blockers": list(filing_status.blockers),
                },
            )

    def get_status_response(self) -> AutonomousBureauFilingStatusResponse:
        return AutonomousBureauFilingStatusResponse.from_status(
            get_autonomous_bureau_filing_status()
        )

    async def list_runs(
        self,
        user: User,
        params: AutonomousBureauFilingRunListParams,
    ) -> PaginatedResponse[AutonomousBureauFilingRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            AutonomousBureauFilingRunListFilters(
                skip=skip,
                limit=params.page_size,
                account_id=params.account_id,
            ),
        )
        items = [AutonomousBureauFilingRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_live_api_run(
        self,
        user: User,
        bureau_live_api_run_id: uuid.UUID,
        body: AutonomousBureauFilingSubmitRequest,
    ) -> AutonomousBureauFilingRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_autonomous_bureau_filing_run(
                session=self._session,
                organization_id=organization_id,
                bureau_live_api_run_id=bureau_live_api_run_id,
                filing_summary=body.filing_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not invoked" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return AutonomousBureauFilingRunResultResponse(
            completed_at=summary.completed_at,
            run=AutonomousBureauFilingRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> AutonomousBureauFilingRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_autonomous_bureau_filing_run(
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
        return AutonomousBureauFilingRunResultResponse(
            completed_at=summary.completed_at,
            run=AutonomousBureauFilingRunResponse.from_model(summary.run),
        )
