"""Admin-gated Stripe live Tax API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.dependencies import require_stripe_live_tax_api_enabled
from api.modules.billing.stripe_live_tax_api_schemas import (
    StripeLiveTaxApiInvokeRequest,
    StripeLiveTaxApiRunListParams,
    StripeLiveTaxApiRunResponse,
    StripeLiveTaxApiRunResultResponse,
    StripeLiveTaxApiStatusResponse,
)
from api.modules.billing.stripe_live_tax_api_service import StripeLiveTaxApiService

stripe_live_tax_api_router = APIRouter(prefix="/live-tax-api", tags=["Stripe Live Tax API"])


def get_stripe_live_tax_api_service(
    db: AsyncSession = Depends(get_db),
) -> StripeLiveTaxApiService:
    return StripeLiveTaxApiService.from_session(db)


@stripe_live_tax_api_router.get("/status", response_model=StripeLiveTaxApiStatusResponse)
async def get_stripe_live_tax_api_status_endpoint(
    _: None = Depends(require_stripe_live_tax_api_enabled),
    service: StripeLiveTaxApiService = Depends(get_stripe_live_tax_api_service),
) -> StripeLiveTaxApiStatusResponse:
    return service.get_status_response()


@stripe_live_tax_api_router.get(
    "/runs",
    response_model=PaginatedResponse[StripeLiveTaxApiRunResponse],
)
async def list_stripe_live_tax_api_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_stripe_live_tax_api_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveTaxApiService = Depends(get_stripe_live_tax_api_service),
) -> PaginatedResponse[StripeLiveTaxApiRunResponse]:
    params = StripeLiveTaxApiRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@stripe_live_tax_api_router.post(
    "/tax-calculation-runs/{stripe_tax_calculation_run_id}/invoke",
    response_model=StripeLiveTaxApiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_stripe_live_tax_api_run_endpoint(
    stripe_tax_calculation_run_id: uuid.UUID,
    body: StripeLiveTaxApiInvokeRequest,
    _: None = Depends(require_stripe_live_tax_api_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveTaxApiService = Depends(get_stripe_live_tax_api_service),
) -> StripeLiveTaxApiRunResultResponse:
    return await service.submit_from_tax_calculation_run(
        current_user, stripe_tax_calculation_run_id, body
    )


@stripe_live_tax_api_router.post(
    "/runs/{run_id}/approve",
    response_model=StripeLiveTaxApiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_stripe_live_tax_api_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_stripe_live_tax_api_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveTaxApiService = Depends(get_stripe_live_tax_api_service),
) -> StripeLiveTaxApiRunResultResponse:
    return await service.approve_run(current_user, run_id)
