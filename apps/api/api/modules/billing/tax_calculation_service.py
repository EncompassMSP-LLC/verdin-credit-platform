"""Admin-gated Stripe tax calculation service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.stripe_tax_calculation import get_stripe_tax_calculation_status
from api.modules.auth.models import User
from api.modules.billing.tax_calculation_processor import (
    approve_stripe_tax_calculation_run,
    submit_stripe_tax_calculation_run,
)
from api.modules.billing.tax_calculation_repository import (
    StripeTaxCalculationRunListFilters,
    StripeTaxCalculationRunRepository,
)
from api.modules.billing.tax_calculation_schemas import (
    StripeTaxCalculationRequest,
    StripeTaxCalculationRunListParams,
    StripeTaxCalculationRunResponse,
    StripeTaxCalculationRunResultResponse,
    StripeTaxCalculationStatusResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class StripeTaxCalculationService:
    def __init__(
        self,
        run_repo: StripeTaxCalculationRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> StripeTaxCalculationService:
        return cls(StripeTaxCalculationRunRepository(session), session=session)

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
                detail="Insufficient permissions to view Stripe tax calculation runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit Stripe tax calculation runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve Stripe tax calculation runs",
            )

    def _require_ready(self) -> None:
        tax_status = get_stripe_tax_calculation_status()
        if not tax_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Stripe tax calculation is not ready",
                    "blockers": list(tax_status.blockers),
                },
            )

    def get_status_response(self) -> StripeTaxCalculationStatusResponse:
        return StripeTaxCalculationStatusResponse.from_status(get_stripe_tax_calculation_status())

    async def list_runs(
        self,
        user: User,
        params: StripeTaxCalculationRunListParams,
    ) -> PaginatedResponse[StripeTaxCalculationRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            StripeTaxCalculationRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [StripeTaxCalculationRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_pdf_run(
        self,
        user: User,
        invoice_pdf_run_id: uuid.UUID,
        body: StripeTaxCalculationRequest,
    ) -> StripeTaxCalculationRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_stripe_tax_calculation_run(
                session=self._session,
                organization_id=organization_id,
                invoice_pdf_run_id=invoice_pdf_run_id,
                calculation_summary=body.calculation_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not generated" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return StripeTaxCalculationRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeTaxCalculationRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> StripeTaxCalculationRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_stripe_tax_calculation_run(
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
        return StripeTaxCalculationRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeTaxCalculationRunResponse.from_model(summary.run),
        )
