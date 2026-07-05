"""Admin-gated autonomous bureau filing endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.autonomous_bureau_filing_dependencies import (
    require_autonomous_bureau_filing_enabled,
)
from api.modules.accounts.autonomous_bureau_filing_schemas import (
    AutonomousBureauFilingRunListParams,
    AutonomousBureauFilingRunResponse,
    AutonomousBureauFilingRunResultResponse,
    AutonomousBureauFilingStatusResponse,
    AutonomousBureauFilingSubmitRequest,
)
from api.modules.accounts.autonomous_bureau_filing_service import AutonomousBureauFilingService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

autonomous_bureau_filing_router = APIRouter(
    prefix="/autonomous-bureau-filing", tags=["Autonomous Bureau Filing"]
)


def get_autonomous_bureau_filing_service(
    db: AsyncSession = Depends(get_db),
) -> AutonomousBureauFilingService:
    return AutonomousBureauFilingService.from_session(db)


@autonomous_bureau_filing_router.get("/status", response_model=AutonomousBureauFilingStatusResponse)
async def get_autonomous_bureau_filing_status_endpoint(
    _: None = Depends(require_autonomous_bureau_filing_enabled),
    service: AutonomousBureauFilingService = Depends(get_autonomous_bureau_filing_service),
) -> AutonomousBureauFilingStatusResponse:
    return service.get_status_response()


@autonomous_bureau_filing_router.get(
    "/runs",
    response_model=PaginatedResponse[AutonomousBureauFilingRunResponse],
)
async def list_autonomous_bureau_filing_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_autonomous_bureau_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: AutonomousBureauFilingService = Depends(get_autonomous_bureau_filing_service),
) -> PaginatedResponse[AutonomousBureauFilingRunResponse]:
    params = AutonomousBureauFilingRunListParams(
        page=page, page_size=page_size, account_id=account_id
    )
    return await service.list_runs(current_user, params)


@autonomous_bureau_filing_router.post(
    "/live-api-runs/{bureau_live_api_run_id}/file",
    response_model=AutonomousBureauFilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_autonomous_bureau_filing_run_endpoint(
    bureau_live_api_run_id: uuid.UUID,
    body: AutonomousBureauFilingSubmitRequest,
    _: None = Depends(require_autonomous_bureau_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: AutonomousBureauFilingService = Depends(get_autonomous_bureau_filing_service),
) -> AutonomousBureauFilingRunResultResponse:
    return await service.submit_from_live_api_run(current_user, bureau_live_api_run_id, body)


@autonomous_bureau_filing_router.post(
    "/runs/{run_id}/approve",
    response_model=AutonomousBureauFilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_autonomous_bureau_filing_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_autonomous_bureau_filing_enabled),
    current_user: User = Depends(get_current_user),
    service: AutonomousBureauFilingService = Depends(get_autonomous_bureau_filing_service),
) -> AutonomousBureauFilingRunResultResponse:
    return await service.approve_run(current_user, run_id)
