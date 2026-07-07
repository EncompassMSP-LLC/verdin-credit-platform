"""Admin-gated native mobile passkey client service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.native_mobile_passkey_client import get_native_mobile_passkey_client_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.native_mobile_passkey_client_processor import (
    approve_native_mobile_passkey_client_run,
    submit_native_mobile_passkey_client_run,
)
from api.modules.enterprise.native_mobile_passkey_client_repository import (
    NativeMobilePasskeyClientRunListFilters,
    NativeMobilePasskeyClientRunRepository,
)
from api.modules.enterprise.native_mobile_passkey_client_schemas import (
    NativeMobilePasskeyClientRunListParams,
    NativeMobilePasskeyClientRunResponse,
    NativeMobilePasskeyClientRunResultResponse,
    NativeMobilePasskeyClientStatusResponse,
    NativeMobilePasskeyClientSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class NativeMobilePasskeyClientService:
    def __init__(
        self,
        run_repo: NativeMobilePasskeyClientRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> NativeMobilePasskeyClientService:
        return cls(NativeMobilePasskeyClientRunRepository(session), session=session)

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
                detail="Insufficient permissions to view native mobile passkey client runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit native mobile passkey client runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve native mobile passkey client runs",
            )

    def _require_ready(self) -> None:
        client_status = get_native_mobile_passkey_client_status()
        if not client_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Native mobile passkey client is not ready",
                    "blockers": list(client_status.blockers),
                },
            )

    def get_status_response(self) -> NativeMobilePasskeyClientStatusResponse:
        return NativeMobilePasskeyClientStatusResponse.from_status(
            get_native_mobile_passkey_client_status()
        )

    async def list_runs(
        self,
        user: User,
        params: NativeMobilePasskeyClientRunListParams,
    ) -> PaginatedResponse[NativeMobilePasskeyClientRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            NativeMobilePasskeyClientRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [NativeMobilePasskeyClientRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_readiness_run(
        self,
        user: User,
        mobile_passkey_readiness_run_id: uuid.UUID,
        body: NativeMobilePasskeyClientSubmitRequest,
    ) -> NativeMobilePasskeyClientRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_native_mobile_passkey_client_run(
                session=self._session,
                organization_id=organization_id,
                mobile_passkey_readiness_run_id=mobile_passkey_readiness_run_id,
                client_summary=body.client_summary,
                platform=body.platform,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return NativeMobilePasskeyClientRunResultResponse(
            completed_at=summary.completed_at,
            run=NativeMobilePasskeyClientRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> NativeMobilePasskeyClientRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_native_mobile_passkey_client_run(
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
        return NativeMobilePasskeyClientRunResultResponse(
            completed_at=summary.completed_at,
            run=NativeMobilePasskeyClientRunResponse.from_model(summary.run),
        )
