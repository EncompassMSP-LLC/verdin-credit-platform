"""Admin-gated Stripe live charge retry execution endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.stripe_live_charge_retry_execution_dependencies import (
    require_stripe_live_charge_retry_execution_enabled,
)
from api.modules.billing.stripe_live_charge_retry_execution_schemas import (
    StripeLiveChargeRetryExecutionRunListParams,
    StripeLiveChargeRetryExecutionRunResponse,
    StripeLiveChargeRetryExecutionRunResultResponse,
    StripeLiveChargeRetryExecutionStatusResponse,
    StripeLiveChargeRetryExecutionSubmitRequest,
)
from api.modules.billing.stripe_live_charge_retry_execution_service import (
    StripeLiveChargeRetryExecutionService,
)

stripe_live_charge_retry_execution_router = APIRouter(
    prefix="/live-charge-retry",
    tags=["Stripe Live Charge Retry"],
)


def get_stripe_live_charge_retry_execution_service(
    db: AsyncSession = Depends(get_db),
) -> StripeLiveChargeRetryExecutionService:
    return StripeLiveChargeRetryExecutionService.from_session(db)


@stripe_live_charge_retry_execution_router.get(
    "/status", response_model=StripeLiveChargeRetryExecutionStatusResponse
)
async def get_stripe_live_charge_retry_execution_status_endpoint(
    _: None = Depends(require_stripe_live_charge_retry_execution_enabled),
    service: StripeLiveChargeRetryExecutionService = Depends(
        get_stripe_live_charge_retry_execution_service
    ),
) -> StripeLiveChargeRetryExecutionStatusResponse:
    return service.get_status_response()


@stripe_live_charge_retry_execution_router.get(
    "/runs",
    response_model=PaginatedResponse[StripeLiveChargeRetryExecutionRunResponse],
)
async def list_stripe_live_charge_retry_execution_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_stripe_live_charge_retry_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveChargeRetryExecutionService = Depends(
        get_stripe_live_charge_retry_execution_service
    ),
) -> PaginatedResponse[StripeLiveChargeRetryExecutionRunResponse]:
    params = StripeLiveChargeRetryExecutionRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@stripe_live_charge_retry_execution_router.post(
    "/charge-retry-runs/{stripe_charge_retry_run_id}/execute",
    response_model=StripeLiveChargeRetryExecutionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_stripe_live_charge_retry_execution_run_endpoint(
    stripe_charge_retry_run_id: uuid.UUID,
    body: StripeLiveChargeRetryExecutionSubmitRequest,
    _: None = Depends(require_stripe_live_charge_retry_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveChargeRetryExecutionService = Depends(
        get_stripe_live_charge_retry_execution_service
    ),
) -> StripeLiveChargeRetryExecutionRunResultResponse:
    return await service.submit_from_charge_retry_run(
        current_user, stripe_charge_retry_run_id, body
    )


@stripe_live_charge_retry_execution_router.post(
    "/runs/{run_id}/approve",
    response_model=StripeLiveChargeRetryExecutionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_stripe_live_charge_retry_execution_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_stripe_live_charge_retry_execution_enabled),
    current_user: User = Depends(get_current_user),
    service: StripeLiveChargeRetryExecutionService = Depends(
        get_stripe_live_charge_retry_execution_service
    ),
) -> StripeLiveChargeRetryExecutionRunResultResponse:
    return await service.approve_run(current_user, run_id)
