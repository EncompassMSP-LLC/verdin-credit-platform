"""Admin-gated Stripe invoice PDF generation service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.stripe_invoice_pdf import get_stripe_invoice_pdf_status
from api.modules.auth.models import User
from api.modules.billing.invoice_pdf_processor import (
    approve_stripe_invoice_pdf_run,
    submit_stripe_invoice_pdf_run,
)
from api.modules.billing.invoice_pdf_repository import (
    StripeInvoicePdfRunListFilters,
    StripeInvoicePdfRunRepository,
)
from api.modules.billing.invoice_pdf_schemas import (
    StripeInvoicePdfRequest,
    StripeInvoicePdfRunListParams,
    StripeInvoicePdfRunResponse,
    StripeInvoicePdfRunResultResponse,
    StripeInvoicePdfStatusResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class StripeInvoicePdfService:
    def __init__(
        self,
        run_repo: StripeInvoicePdfRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> StripeInvoicePdfService:
        return cls(StripeInvoicePdfRunRepository(session), session=session)

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
                detail="Insufficient permissions to view Stripe invoice PDF runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit Stripe invoice PDF runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve Stripe invoice PDF runs",
            )

    def _require_ready(self) -> None:
        pdf_status = get_stripe_invoice_pdf_status()
        if not pdf_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Stripe invoice PDF generation is not ready",
                    "blockers": list(pdf_status.blockers),
                },
            )

    def get_status_response(self) -> StripeInvoicePdfStatusResponse:
        return StripeInvoicePdfStatusResponse.from_status(get_stripe_invoice_pdf_status())

    async def list_runs(
        self,
        user: User,
        params: StripeInvoicePdfRunListParams,
    ) -> PaginatedResponse[StripeInvoicePdfRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            StripeInvoicePdfRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [StripeInvoicePdfRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_collection_run(
        self,
        user: User,
        collection_run_id: uuid.UUID,
        body: StripeInvoicePdfRequest,
    ) -> StripeInvoicePdfRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_stripe_invoice_pdf_run(
                session=self._session,
                organization_id=organization_id,
                collection_run_id=collection_run_id,
                generation_summary=body.generation_summary,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT
                if "not completed" in detail
                or "not an invoice PDF" in detail
                or "did not generate" in detail
                else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return StripeInvoicePdfRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeInvoicePdfRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> StripeInvoicePdfRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_stripe_invoice_pdf_run(
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
        return StripeInvoicePdfRunResultResponse(
            completed_at=summary.completed_at,
            run=StripeInvoicePdfRunResponse.from_model(summary.run),
        )
