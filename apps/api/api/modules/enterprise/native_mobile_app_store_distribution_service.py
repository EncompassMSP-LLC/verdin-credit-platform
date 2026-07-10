"""Admin-gated native mobile app store distribution service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.native_mobile_app_store_distribution import (
    get_native_mobile_app_store_distribution_status,
)
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.native_mobile_app_store_distribution_processor import (
    approve_native_mobile_app_store_distribution_run,
    submit_native_mobile_app_store_distribution_run,
)
from api.modules.enterprise.native_mobile_app_store_distribution_repository import (
    NativeMobileAppStoreDistributionRunListFilters,
    NativeMobileAppStoreDistributionRunRepository,
)
from api.modules.enterprise.native_mobile_app_store_distribution_schemas import (
    NativeMobileAppStoreDistributionRunListParams,
    NativeMobileAppStoreDistributionRunResponse,
    NativeMobileAppStoreDistributionRunResultResponse,
    NativeMobileAppStoreDistributionStatusResponse,
    NativeMobileAppStoreDistributionSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class NativeMobileAppStoreDistributionService:
    def __init__(
        self,
        run_repo: NativeMobileAppStoreDistributionRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> NativeMobileAppStoreDistributionService:
        return cls(NativeMobileAppStoreDistributionRunRepository(session), session=session)

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
                detail=(
                    "Insufficient permissions to view native mobile app store distribution runs"
                ),
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Insufficient permissions to submit native mobile app store distribution runs"
                ),
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Insufficient permissions to approve native mobile app store distribution runs"
                ),
            )

    def _require_ready(self) -> None:
        distribution_status = get_native_mobile_app_store_distribution_status()
        if not distribution_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Native mobile app store distribution is not ready",
                    "blockers": list(distribution_status.blockers),
                },
            )

    def get_status_response(self) -> NativeMobileAppStoreDistributionStatusResponse:
        return NativeMobileAppStoreDistributionStatusResponse.from_status(
            get_native_mobile_app_store_distribution_status()
        )

    async def list_runs(
        self,
        user: User,
        params: NativeMobileAppStoreDistributionRunListParams,
    ) -> PaginatedResponse[NativeMobileAppStoreDistributionRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            NativeMobileAppStoreDistributionRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [NativeMobileAppStoreDistributionRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_passkey_client_run(
        self,
        user: User,
        native_mobile_passkey_client_run_id: uuid.UUID,
        body: NativeMobileAppStoreDistributionSubmitRequest,
    ) -> NativeMobileAppStoreDistributionRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_native_mobile_app_store_distribution_run(
                session=self._session,
                organization_id=organization_id,
                native_mobile_passkey_client_run_id=native_mobile_passkey_client_run_id,
                distribution_summary=body.distribution_summary,
                store_target=body.store_target,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return NativeMobileAppStoreDistributionRunResultResponse(
            completed_at=summary.completed_at,
            run=NativeMobileAppStoreDistributionRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> NativeMobileAppStoreDistributionRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_native_mobile_app_store_distribution_run(
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
        return NativeMobileAppStoreDistributionRunResultResponse(
            completed_at=summary.completed_at,
            run=NativeMobileAppStoreDistributionRunResponse.from_model(summary.run),
        )
