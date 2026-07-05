"""Admin-gated Stripe tax calculation endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.dependencies import require_stripe_tax_calculation_enabled
from api.modules.billing.tax_calculation_schemas import (
    StripeTaxCalculationRequest,
    StripeTaxCalculationRunListParams,
    StripeTaxCalculationRunResponse,
    StripeTaxCalculationRunResultResponse,
    StripeTaxCalculationStatusResponse,
)
from api.modules.billing.tax_calculation_service import StripeTaxCalculationService

tax_calculation_router = APIRouter(prefix="/tax-calculation", tags=["Stripe Tax Calculation"])


def get_stripe_tax_calculation_service(
    db: AsyncSession = Depends(get_db),
) -> StripeTaxCalculationService:
    return StripeTaxCalculationService.from_session(db)


@tax_calculation_router.get("/status", response_model=StripeTaxCalculationStatusResponse)
async def get_stripe_tax_calculation_status_endpoint(
    _: None = Depends(require_stripe_tax_calculation_enabled),
    service: StripeTaxCalculationService = Depends(get_stripe_tax_calculation_service),
) -> StripeTaxCalculationStatusResponse:
    return service.get_status_response()


@tax_calculation_router.get(
    "/runs",
    response_model=PaginatedResponse[StripeTaxCalculationRunResponse],
)
async def list_stripe_tax_calculation_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_stripe_tax_calculation_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeTaxCalculationService = Depends(get_stripe_tax_calculation_service),
) -> PaginatedResponse[StripeTaxCalculationRunResponse]:
    params = StripeTaxCalculationRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@tax_calculation_router.post(
    "/pdf-runs/{invoice_pdf_run_id}/calculate",
    response_model=StripeTaxCalculationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_stripe_tax_calculation_run_endpoint(
    invoice_pdf_run_id: uuid.UUID,
    body: StripeTaxCalculationRequest,
    _: None = Depends(require_stripe_tax_calculation_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeTaxCalculationService = Depends(get_stripe_tax_calculation_service),
) -> StripeTaxCalculationRunResultResponse:
    return await service.submit_from_pdf_run(current_user, invoice_pdf_run_id, body)


@tax_calculation_router.post(
    "/runs/{run_id}/approve",
    response_model=StripeTaxCalculationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_stripe_tax_calculation_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_stripe_tax_calculation_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeTaxCalculationService = Depends(get_stripe_tax_calculation_service),
) -> StripeTaxCalculationRunResultResponse:
    return await service.approve_run(current_user, run_id)
