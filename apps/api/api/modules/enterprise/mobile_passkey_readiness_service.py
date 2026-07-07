"""Admin-gated mobile passkey readiness service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.mobile_passkey_readiness import get_mobile_passkey_readiness_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.mobile_passkey_readiness_processor import (
    approve_mobile_passkey_readiness_run,
    submit_mobile_passkey_readiness_run,
)
from api.modules.enterprise.mobile_passkey_readiness_repository import (
    MobilePasskeyReadinessRunListFilters,
    MobilePasskeyReadinessRunRepository,
)
from api.modules.enterprise.mobile_passkey_readiness_schemas import (
    MobilePasskeyReadinessRunListParams,
    MobilePasskeyReadinessRunResponse,
    MobilePasskeyReadinessRunResultResponse,
    MobilePasskeyReadinessStatusResponse,
    MobilePasskeyReadinessSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class MobilePasskeyReadinessService:
    def __init__(
        self,
        run_repo: MobilePasskeyReadinessRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> MobilePasskeyReadinessService:
        return cls(MobilePasskeyReadinessRunRepository(session), session=session)

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
                detail="Insufficient permissions to view mobile passkey readiness runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit mobile passkey readiness runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve mobile passkey readiness runs",
            )

    def _require_ready(self) -> None:
        passkey_status = get_mobile_passkey_readiness_status()
        if not passkey_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Mobile passkey readiness is not ready",
                    "blockers": list(passkey_status.blockers),
                },
            )

    def get_status_response(self) -> MobilePasskeyReadinessStatusResponse:
        return MobilePasskeyReadinessStatusResponse.from_status(
            get_mobile_passkey_readiness_status()
        )

    async def list_runs(
        self,
        user: User,
        params: MobilePasskeyReadinessRunListParams,
    ) -> PaginatedResponse[MobilePasskeyReadinessRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            MobilePasskeyReadinessRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [MobilePasskeyReadinessRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_ui_run(
        self,
        user: User,
        hris_passwordless_ui_run_id: uuid.UUID,
        body: MobilePasskeyReadinessSubmitRequest,
    ) -> MobilePasskeyReadinessRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_mobile_passkey_readiness_run(
                session=self._session,
                organization_id=organization_id,
                hris_passwordless_ui_run_id=hris_passwordless_ui_run_id,
                readiness_summary=body.readiness_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return MobilePasskeyReadinessRunResultResponse(
            completed_at=summary.completed_at,
            run=MobilePasskeyReadinessRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> MobilePasskeyReadinessRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_mobile_passkey_readiness_run(
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
        return MobilePasskeyReadinessRunResultResponse(
            completed_at=summary.completed_at,
            run=MobilePasskeyReadinessRunResponse.from_model(summary.run),
        )
