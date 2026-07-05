"""HRIS bidirectional sync service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.hris_bidirectional_sync import get_hris_bidirectional_sync_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunStatus
from api.modules.enterprise.hris_sync_processor import run_hris_bidirectional_sync
from api.modules.enterprise.hris_sync_repository import (
    HrisBidirectionalSyncRunListFilters,
    HrisBidirectionalSyncRunRepository,
)
from api.modules.enterprise.hris_sync_schemas import (
    HrisBidirectionalSyncRunListParams,
    HrisBidirectionalSyncRunRequest,
    HrisBidirectionalSyncRunResponse,
    HrisBidirectionalSyncRunResultResponse,
    HrisBidirectionalSyncStatusResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class HrisBidirectionalSyncService:
    def __init__(
        self,
        run_repo: HrisBidirectionalSyncRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> HrisBidirectionalSyncService:
        return cls(HrisBidirectionalSyncRunRepository(session), session=session)

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
                detail="Insufficient permissions to view HRIS sync runs",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to run HRIS sync",
            )

    def get_status_response(self) -> HrisBidirectionalSyncStatusResponse:
        return HrisBidirectionalSyncStatusResponse.from_status(get_hris_bidirectional_sync_status())

    async def list_runs(
        self,
        user: User,
        params: HrisBidirectionalSyncRunListParams,
    ) -> PaginatedResponse[HrisBidirectionalSyncRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            HrisBidirectionalSyncRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [HrisBidirectionalSyncRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def run_sync(
        self,
        user: User,
        body: HrisBidirectionalSyncRunRequest,
    ) -> HrisBidirectionalSyncRunResultResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        sync_status = get_hris_bidirectional_sync_status()
        if not sync_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "HRIS bidirectional sync is not ready",
                    "blockers": list(sync_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await run_hris_bidirectional_sync(
            session=self._session,
            organization_id=organization_id,
            run_kind=body.run_kind,
            performed_by_user_id=user.id,
        )
        if summary.run.status == HrisBidirectionalSyncRunStatus.FAILED:
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary.run.error_message or "HRIS bidirectional sync run failed",
            )
        await self._session.commit()
        return HrisBidirectionalSyncRunResultResponse(
            completed_at=summary.completed_at,
            run=HrisBidirectionalSyncRunResponse.from_model(summary.run),
        )
