"""Admin-gated live unredacted benchmark blob export service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.live_unredacted_benchmark_blob_export import (
    get_live_unredacted_benchmark_blob_export_status,
)
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.reporting.live_unredacted_benchmark_blob_export_processor import (
    approve_live_unredacted_benchmark_blob_export_run,
    submit_live_unredacted_benchmark_blob_export_run,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_repository import (
    LiveUnredactedBenchmarkBlobExportRunListFilters,
    LiveUnredactedBenchmarkBlobExportRunRepository,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_schemas import (
    LiveUnredactedBenchmarkBlobExportRunListParams,
    LiveUnredactedBenchmarkBlobExportRunResponse,
    LiveUnredactedBenchmarkBlobExportRunResultResponse,
    LiveUnredactedBenchmarkBlobExportStatusResponse,
    LiveUnredactedBenchmarkBlobExportSubmitRequest,
)
from api.modules.reporting.permissions import REPORTING_ADMIN_ROLE, REPORTING_READ_ROLE


class LiveUnredactedBenchmarkBlobExportService:
    def __init__(
        self,
        run_repo: LiveUnredactedBenchmarkBlobExportRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> LiveUnredactedBenchmarkBlobExportService:
        return cls(LiveUnredactedBenchmarkBlobExportRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, REPORTING_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view live unredacted benchmark blob exports",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, REPORTING_ADMIN_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit live unredacted benchmark blob exports",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve live unredacted benchmark blob exports",
            )

    def _require_ready(self) -> None:
        blob_status = get_live_unredacted_benchmark_blob_export_status()
        if not blob_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Live unredacted benchmark blob export is not ready",
                    "blockers": list(blob_status.blockers),
                },
            )

    def get_status_response(self) -> LiveUnredactedBenchmarkBlobExportStatusResponse:
        return LiveUnredactedBenchmarkBlobExportStatusResponse.from_status(
            get_live_unredacted_benchmark_blob_export_status()
        )

    async def list_runs(
        self,
        user: User,
        params: LiveUnredactedBenchmarkBlobExportRunListParams,
    ) -> PaginatedResponse[LiveUnredactedBenchmarkBlobExportRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            LiveUnredactedBenchmarkBlobExportRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [LiveUnredactedBenchmarkBlobExportRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_unredacted_export_run(
        self,
        user: User,
        unredacted_export_run_id: uuid.UUID,
        body: LiveUnredactedBenchmarkBlobExportSubmitRequest,
    ) -> LiveUnredactedBenchmarkBlobExportRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_live_unredacted_benchmark_blob_export_run(
                session=self._session,
                organization_id=organization_id,
                unredacted_export_run_id=unredacted_export_run_id,
                export_summary=body.export_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return LiveUnredactedBenchmarkBlobExportRunResultResponse(
            completed_at=summary.completed_at,
            run=LiveUnredactedBenchmarkBlobExportRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> LiveUnredactedBenchmarkBlobExportRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_live_unredacted_benchmark_blob_export_run(
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
        return LiveUnredactedBenchmarkBlobExportRunResultResponse(
            completed_at=summary.completed_at,
            run=LiveUnredactedBenchmarkBlobExportRunResponse.from_model(summary.run),
        )
