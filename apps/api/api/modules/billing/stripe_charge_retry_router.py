"""Admin-gated Stripe charge retry endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.stripe_charge_retry_dependencies import require_stripe_charge_retry_enabled
from api.modules.billing.stripe_charge_retry_schemas import (
    StripeChargeRetryRunListParams,
    StripeChargeRetryRunResponse,
    StripeChargeRetryRunResultResponse,
    StripeChargeRetryStatusResponse,
    StripeChargeRetrySubmitRequest,
)
from api.modules.billing.stripe_charge_retry_service import StripeChargeRetryService

stripe_charge_retry_router = APIRouter(prefix="/charge-retry", tags=["Stripe Charge Retry"])


def get_stripe_charge_retry_service(
    db: AsyncSession = Depends(get_db),
) -> StripeChargeRetryService:
    return StripeChargeRetryService.from_session(db)


@stripe_charge_retry_router.get("/status", response_model=StripeChargeRetryStatusResponse)
async def get_stripe_charge_retry_status_endpoint(
    _: None = Depends(require_stripe_charge_retry_enabled),
    service: StripeChargeRetryService = Depends(get_stripe_charge_retry_service),
) -> StripeChargeRetryStatusResponse:
    return service.get_status_response()


@stripe_charge_retry_router.get(
    "/runs",
    response_model=PaginatedResponse[StripeChargeRetryRunResponse],
)
async def list_stripe_charge_retry_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_stripe_charge_retry_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeChargeRetryService = Depends(get_stripe_charge_retry_service),
) -> PaginatedResponse[StripeChargeRetryRunResponse]:
    params = StripeChargeRetryRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@stripe_charge_retry_router.post(
    "/live-tax-api-runs/{stripe_live_tax_api_run_id}/retry",
    response_model=StripeChargeRetryRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_stripe_charge_retry_run_endpoint(
    stripe_live_tax_api_run_id: uuid.UUID,
    body: StripeChargeRetrySubmitRequest,
    _: None = Depends(require_stripe_charge_retry_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeChargeRetryService = Depends(get_stripe_charge_retry_service),
) -> StripeChargeRetryRunResultResponse:
    return await service.submit_from_live_tax_api_run(
        current_user, stripe_live_tax_api_run_id, body
    )


@stripe_charge_retry_router.post(
    "/runs/{run_id}/approve",
    response_model=StripeChargeRetryRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_stripe_charge_retry_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_stripe_charge_retry_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeChargeRetryService = Depends(get_stripe_charge_retry_service),
) -> StripeChargeRetryRunResultResponse:
    return await service.approve_run(current_user, run_id)
