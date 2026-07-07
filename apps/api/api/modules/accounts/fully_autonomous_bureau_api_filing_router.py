"""Admin-gated fully autonomous bureau API filing endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.fully_autonomous_bureau_api_filing_dependencies import (
    require_fully_autonomous_bureau_api_filing_enabled,
)
from api.modules.accounts.fully_autonomous_bureau_api_filing_schemas import (
    FullyAutonomousBureauApiFilingRunListParams,
    FullyAutonomousBureauApiFilingRunResponse,
    FullyAutonomousBureauApiFilingRunResultResponse,
    FullyAutonomousBureauApiFilingStatusResponse,
    FullyAutonomousBureauApiFilingSubmitRequest,
)
from api.modules.accounts.fully_autonomous_bureau_api_filing_service import (
    FullyAutonomousBureauApiFilingService,
)
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

fully_autonomous_bureau_api_filing_router = APIRouter(
    prefix="/fully-autonomous-bureau-api-filing",
    tags=["Fully Autonomous Bureau API Filing"],
)


def get_fully_autonomous_bureau_api_filing_service(
    db: AsyncSession = Depends(get_db),
) -> FullyAutonomousBureauApiFilingService:
    return FullyAutonomousBureauApiFilingService.from_session(db)


@fully_autonomous_bureau_api_filing_router.get(
    "/status",
    response_model=FullyAutonomousBureauApiFilingStatusResponse,
)
async def get_fully_autonomous_bureau_api_filing_status_endpoint(
    _: None = Depends(require_fully_autonomous_bureau_api_filing_enabled),
    service: FullyAutonomousBureauApiFilingService = Depends(
        get_fully_autonomous_bureau_api_filing_service
    ),
) -> FullyAutonomousBureauApiFilingStatusResponse:
    return service.get_status_response()


@fully_autonomous_bureau_api_filing_router.get(
    "/runs",
    response_model=PaginatedResponse[FullyAutonomousBureauApiFilingRunResponse],
)
async def list_fully_autonomous_bureau_api_filing_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_fully_autonomous_bureau_api_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: FullyAutonomousBureauApiFilingService = Depends(
        get_fully_autonomous_bureau_api_filing_service
    ),
) -> PaginatedResponse[FullyAutonomousBureauApiFilingRunResponse]:
    params = FullyAutonomousBureauApiFilingRunListParams(
        page=page, page_size=page_size, account_id=account_id
    )
    return await service.list_runs(current_user, params)


@fully_autonomous_bureau_api_filing_router.post(
    "/filing-runs/{autonomous_bureau_filing_run_id}/execute",
    response_model=FullyAutonomousBureauApiFilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_fully_autonomous_bureau_api_filing_run_endpoint(
    autonomous_bureau_filing_run_id: uuid.UUID,
    body: FullyAutonomousBureauApiFilingSubmitRequest,
    _: None = Depends(require_fully_autonomous_bureau_api_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: FullyAutonomousBureauApiFilingService = Depends(
        get_fully_autonomous_bureau_api_filing_service
    ),
) -> FullyAutonomousBureauApiFilingRunResultResponse:
    return await service.submit_from_filing_run(current_user, autonomous_bureau_filing_run_id, body)


@fully_autonomous_bureau_api_filing_router.post(
    "/runs/{run_id}/approve",
    response_model=FullyAutonomousBureauApiFilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_fully_autonomous_bureau_api_filing_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_fully_autonomous_bureau_api_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: FullyAutonomousBureauApiFilingService = Depends(
        get_fully_autonomous_bureau_api_filing_service
    ),
) -> FullyAutonomousBureauApiFilingRunResultResponse:
    return await service.approve_run(current_user, run_id)
