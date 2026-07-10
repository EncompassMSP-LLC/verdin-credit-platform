"""Operator-gated unsupervised autonomous filing loop endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.unsupervised_autonomous_filing_loop_dependencies import (
    require_unsupervised_autonomous_filing_loops_enabled,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_schemas import (
    UnsupervisedAutonomousFilingLoopRunListParams,
    UnsupervisedAutonomousFilingLoopRunResponse,
    UnsupervisedAutonomousFilingLoopRunResultResponse,
    UnsupervisedAutonomousFilingLoopStatusResponse,
    UnsupervisedAutonomousFilingLoopSubmitRequest,
)
from api.modules.accounts.unsupervised_autonomous_filing_loop_service import (
    UnsupervisedAutonomousFilingLoopService,
)
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

unsupervised_autonomous_filing_loop_router = APIRouter(
    prefix="/unsupervised-autonomous-filing-loops",
    tags=["Unsupervised Autonomous Filing Loops"],
)


def get_unsupervised_autonomous_filing_loop_service(
    db: AsyncSession = Depends(get_db),
) -> UnsupervisedAutonomousFilingLoopService:
    return UnsupervisedAutonomousFilingLoopService.from_session(db)


@unsupervised_autonomous_filing_loop_router.get(
    "/status",
    response_model=UnsupervisedAutonomousFilingLoopStatusResponse,
)
async def get_unsupervised_autonomous_filing_loop_status_endpoint(
    _: None = Depends(require_unsupervised_autonomous_filing_loops_enabled),
    service: UnsupervisedAutonomousFilingLoopService = Depends(
        get_unsupervised_autonomous_filing_loop_service
    ),
) -> UnsupervisedAutonomousFilingLoopStatusResponse:
    return service.get_status_response()


@unsupervised_autonomous_filing_loop_router.get(
    "/runs",
    response_model=PaginatedResponse[UnsupervisedAutonomousFilingLoopRunResponse],
)
async def list_unsupervised_autonomous_filing_loop_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_unsupervised_autonomous_filing_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: UnsupervisedAutonomousFilingLoopService = Depends(
        get_unsupervised_autonomous_filing_loop_service
    ),
) -> PaginatedResponse[UnsupervisedAutonomousFilingLoopRunResponse]:
    params = UnsupervisedAutonomousFilingLoopRunListParams(
        page=page, page_size=page_size, account_id=account_id
    )
    return await service.list_runs(current_user, params)


@unsupervised_autonomous_filing_loop_router.post(
    "/api-filing-runs/{fully_autonomous_bureau_api_filing_run_id}/start",
    response_model=UnsupervisedAutonomousFilingLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_unsupervised_autonomous_filing_loop_run_endpoint(
    fully_autonomous_bureau_api_filing_run_id: uuid.UUID,
    body: UnsupervisedAutonomousFilingLoopSubmitRequest,
    _: None = Depends(require_unsupervised_autonomous_filing_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: UnsupervisedAutonomousFilingLoopService = Depends(
        get_unsupervised_autonomous_filing_loop_service
    ),
) -> UnsupervisedAutonomousFilingLoopRunResultResponse:
    return await service.submit_from_api_filing_run(
        current_user, fully_autonomous_bureau_api_filing_run_id, body
    )


@unsupervised_autonomous_filing_loop_router.post(
    "/runs/{run_id}/approve",
    response_model=UnsupervisedAutonomousFilingLoopRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_unsupervised_autonomous_filing_loop_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_unsupervised_autonomous_filing_loops_enabled),
    current_user: User = Depends(get_current_user),
    service: UnsupervisedAutonomousFilingLoopService = Depends(
        get_unsupervised_autonomous_filing_loop_service
    ),
) -> UnsupervisedAutonomousFilingLoopRunResultResponse:
    return await service.approve_run(current_user, run_id)
