"""Admin-gated multi-IdP bulk provisioning service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.bulk_idp_provisioning import get_bulk_idp_provisioning_status
from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.bulk_idp_provisioning_processor import (
    approve_bulk_idp_provisioning_run,
    submit_bulk_idp_provisioning_run,
)
from api.modules.enterprise.bulk_idp_provisioning_repository import (
    BulkIdpProvisioningRunListFilters,
    BulkIdpProvisioningRunRepository,
)
from api.modules.enterprise.bulk_idp_provisioning_schemas import (
    BulkIdpProvisioningRunListParams,
    BulkIdpProvisioningRunResponse,
    BulkIdpProvisioningRunResultResponse,
    BulkIdpProvisioningStatusResponse,
    BulkIdpProvisioningSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class BulkIdpProvisioningService:
    def __init__(
        self,
        run_repo: BulkIdpProvisioningRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> BulkIdpProvisioningService:
        return cls(BulkIdpProvisioningRunRepository(session), session=session)

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
                detail="Insufficient permissions to view bulk IdP provisioning runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit bulk IdP provisioning runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve bulk IdP provisioning runs",
            )

    def _require_ready(self) -> None:
        provisioning_status = get_bulk_idp_provisioning_status()
        if not provisioning_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Multi-IdP bulk provisioning is not ready",
                    "blockers": list(provisioning_status.blockers),
                },
            )

    def get_status_response(self) -> BulkIdpProvisioningStatusResponse:
        return BulkIdpProvisioningStatusResponse.from_status(get_bulk_idp_provisioning_status())

    async def list_runs(
        self,
        user: User,
        params: BulkIdpProvisioningRunListParams,
    ) -> PaginatedResponse[BulkIdpProvisioningRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            BulkIdpProvisioningRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [BulkIdpProvisioningRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_ui_run(
        self,
        user: User,
        hris_passwordless_ui_run_id: uuid.UUID,
        body: BulkIdpProvisioningSubmitRequest,
    ) -> BulkIdpProvisioningRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_bulk_idp_provisioning_run(
                session=self._session,
                organization_id=organization_id,
                hris_passwordless_ui_run_id=hris_passwordless_ui_run_id,
                provisioning_summary=body.provisioning_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return BulkIdpProvisioningRunResultResponse(
            completed_at=summary.completed_at,
            run=BulkIdpProvisioningRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> BulkIdpProvisioningRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_bulk_idp_provisioning_run(
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
        return BulkIdpProvisioningRunResultResponse(
            completed_at=summary.completed_at,
            run=BulkIdpProvisioningRunResponse.from_model(summary.run),
        )
