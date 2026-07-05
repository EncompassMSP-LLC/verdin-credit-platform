"""Admin-gated Stripe invoice PDF generation endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.dependencies import require_stripe_invoice_pdf_enabled
from api.modules.billing.invoice_pdf_schemas import (
    StripeInvoicePdfRequest,
    StripeInvoicePdfRunListParams,
    StripeInvoicePdfRunResponse,
    StripeInvoicePdfRunResultResponse,
    StripeInvoicePdfStatusResponse,
)
from api.modules.billing.invoice_pdf_service import StripeInvoicePdfService

invoice_pdf_router = APIRouter(prefix="/invoice-pdf", tags=["Stripe Invoice PDF"])


def get_stripe_invoice_pdf_service(
    db: AsyncSession = Depends(get_db),
) -> StripeInvoicePdfService:
    return StripeInvoicePdfService.from_session(db)


@invoice_pdf_router.get("/status", response_model=StripeInvoicePdfStatusResponse)
async def get_stripe_invoice_pdf_status_endpoint(
    _: None = Depends(require_stripe_invoice_pdf_enabled),
    service: StripeInvoicePdfService = Depends(get_stripe_invoice_pdf_service),
) -> StripeInvoicePdfStatusResponse:
    return service.get_status_response()


@invoice_pdf_router.get(
    "/runs",
    response_model=PaginatedResponse[StripeInvoicePdfRunResponse],
)
async def list_stripe_invoice_pdf_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_stripe_invoice_pdf_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeInvoicePdfService = Depends(get_stripe_invoice_pdf_service),
) -> PaginatedResponse[StripeInvoicePdfRunResponse]:
    params = StripeInvoicePdfRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@invoice_pdf_router.post(
    "/collection-runs/{collection_run_id}/generate",
    response_model=StripeInvoicePdfRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_stripe_invoice_pdf_run_endpoint(
    collection_run_id: uuid.UUID,
    body: StripeInvoicePdfRequest,
    _: None = Depends(require_stripe_invoice_pdf_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeInvoicePdfService = Depends(get_stripe_invoice_pdf_service),
) -> StripeInvoicePdfRunResultResponse:
    return await service.submit_from_collection_run(current_user, collection_run_id, body)


@invoice_pdf_router.post(
    "/runs/{run_id}/approve",
    response_model=StripeInvoicePdfRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_stripe_invoice_pdf_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_stripe_invoice_pdf_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeInvoicePdfService = Depends(get_stripe_invoice_pdf_service),
) -> StripeInvoicePdfRunResultResponse:
    return await service.approve_run(current_user, run_id)
