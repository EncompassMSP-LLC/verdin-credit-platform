"""Admin-gated HRIS lifecycle sync service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.hris_lifecycle_sync import get_hris_lifecycle_sync_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.hris_lifecycle_processor import (
    approve_hris_lifecycle_sync_run,
    submit_hris_lifecycle_sync_run,
)
from api.modules.enterprise.hris_lifecycle_repository import (
    HrisLifecycleSyncRunListFilters,
    HrisLifecycleSyncRunRepository,
)
from api.modules.enterprise.hris_lifecycle_schemas import (
    HrisLifecycleSyncRunListParams,
    HrisLifecycleSyncRunResponse,
    HrisLifecycleSyncRunResultResponse,
    HrisLifecycleSyncStatusResponse,
    HrisLifecycleSyncSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class HrisLifecycleSyncService:
    def __init__(
        self,
        run_repo: HrisLifecycleSyncRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> HrisLifecycleSyncService:
        return cls(HrisLifecycleSyncRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view HRIS lifecycle sync runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit HRIS lifecycle sync runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve HRIS lifecycle sync runs",
            )

    def _require_ready(self) -> None:
        lifecycle_status = get_hris_lifecycle_sync_status()
        if not lifecycle_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "HRIS lifecycle sync is not ready",
                    "blockers": list(lifecycle_status.blockers),
                },
            )

    def get_status_response(self) -> HrisLifecycleSyncStatusResponse:
        return HrisLifecycleSyncStatusResponse.from_status(get_hris_lifecycle_sync_status())

    async def list_runs(
        self,
        user: User,
        params: HrisLifecycleSyncRunListParams,
    ) -> PaginatedResponse[HrisLifecycleSyncRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            HrisLifecycleSyncRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [HrisLifecycleSyncRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_bidirectional_run(
        self,
        user: User,
        hris_bidirectional_sync_run_id: uuid.UUID,
        body: HrisLifecycleSyncSubmitRequest,
    ) -> HrisLifecycleSyncRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_hris_lifecycle_sync_run(
                session=self._session,
                organization_id=organization_id,
                hris_bidirectional_sync_run_id=hris_bidirectional_sync_run_id,
                lifecycle_summary=body.lifecycle_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not completed" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return HrisLifecycleSyncRunResultResponse(
            completed_at=summary.completed_at,
            run=HrisLifecycleSyncRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> HrisLifecycleSyncRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_hris_lifecycle_sync_run(
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
        return HrisLifecycleSyncRunResultResponse(
            completed_at=summary.completed_at,
            run=HrisLifecycleSyncRunResponse.from_model(summary.run),
        )
