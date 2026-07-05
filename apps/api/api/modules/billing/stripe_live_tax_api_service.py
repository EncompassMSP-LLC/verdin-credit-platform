"""Admin-gated Stripe live Tax API service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.stripe_live_tax_api import get_stripe_live_tax_api_status
from api.modules.auth.models import User
from api.modules.billing.stripe_live_tax_api_processor import (
    approve_stripe_live_tax_api_run,
    submit_stripe_live_tax_api_run,
)
from api.modules.billing.stripe_live_tax_api_repository import (
    StripeLiveTaxApiRunListFilters,
    StripeLiveTaxApiRunRepository,
)
from api.modules.billing.stripe_live_tax_api_schemas import (
    StripeLiveTaxApiInvokeRequest,
    StripeLiveTaxApiRunListParams,
    StripeLiveTaxApiRunResponse,
    StripeLiveTaxApiRunResultResponse,
    StripeLiveTaxApiStatusResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class StripeLiveTaxApiService:
    def __init__(
        self,
        run_repo: StripeLiveTaxApiRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> StripeLiveTaxApiService:
        return cls(StripeLiveTaxApiRunRepository(session), session=session)

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
                detail="Insufficient permissions to view Stripe live Tax API runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit Stripe live Tax API runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve Stripe live Tax API runs",
            )

    def _require_ready(self) -> None:
        live_tax_status = get_stripe_live_tax_api_status()
        if not live_tax_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Stripe live Tax API is not ready",
                    "blockers": list(live_tax_status.blockers),
                },
            )

    def get_status_response(self) -> StripeLiveTaxApiStatusResponse:
        return StripeLiveTaxApiStatusResponse.from_status(get_stripe_live_tax_api_status())

    async def list_runs(
        self,
        user: User,
        params: StripeLiveTaxApiRunListParams,
    ) -> PaginatedResponse[StripeLiveTaxApiRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            StripeLiveTaxApiRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [StripeLiveTaxApiRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_tax_calculation_run(
        self,
        user: User,
        stripe_tax_calculation_run_id: uuid.UUID,
        body: StripeLiveTaxApiInvokeRequest,
    ) -> StripeLiveTaxApiRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_stripe_live_tax_api_run(
                session=self._session,
                organization_id=organization_id,
                stripe_tax_calculation_run_id=stripe_tax_calculation_run_id,
                invocation_summary=body.invocation_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT
                if "not calculated" in detail
                else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return StripeLiveTaxApiRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeLiveTaxApiRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> StripeLiveTaxApiRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_stripe_live_tax_api_run(
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
        return StripeLiveTaxApiRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeLiveTaxApiRunResponse.from_model(summary.run),
        )
