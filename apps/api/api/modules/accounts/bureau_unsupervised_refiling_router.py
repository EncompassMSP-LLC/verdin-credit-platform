"""Operator-gated bureau unsupervised re-filing endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.bureau_unsupervised_refiling_dependencies import (
    require_bureau_unsupervised_refiling_enabled,
)
from api.modules.accounts.bureau_unsupervised_refiling_schemas import (
    BureauUnsupervisedRefilingRunListParams,
    BureauUnsupervisedRefilingRunResponse,
    BureauUnsupervisedRefilingRunResultResponse,
    BureauUnsupervisedRefilingStatusResponse,
    BureauUnsupervisedRefilingSubmitRequest,
)
from api.modules.accounts.bureau_unsupervised_refiling_service import (
    BureauUnsupervisedRefilingService,
)
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

bureau_unsupervised_refiling_router = APIRouter(
    prefix="/bureau-unsupervised-refiling",
    tags=["Bureau Unsupervised Re-filing"],
)


def get_bureau_unsupervised_refiling_service(
    db: AsyncSession = Depends(get_db),
) -> BureauUnsupervisedRefilingService:
    return BureauUnsupervisedRefilingService.from_session(db)


@bureau_unsupervised_refiling_router.get(
    "/status", response_model=BureauUnsupervisedRefilingStatusResponse
)
async def get_bureau_unsupervised_refiling_status_endpoint(
    _: None = Depends(require_bureau_unsupervised_refiling_enabled),
    service: BureauUnsupervisedRefilingService = Depends(get_bureau_unsupervised_refiling_service),
) -> BureauUnsupervisedRefilingStatusResponse:
    return service.get_status_response()


@bureau_unsupervised_refiling_router.get(
    "/runs",
    response_model=PaginatedResponse[BureauUnsupervisedRefilingRunResponse],
)
async def list_bureau_unsupervised_refiling_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_bureau_unsupervised_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauUnsupervisedRefilingService = Depends(get_bureau_unsupervised_refiling_service),
) -> PaginatedResponse[BureauUnsupervisedRefilingRunResponse]:
    params = BureauUnsupervisedRefilingRunListParams(
        page=page, page_size=page_size, account_id=account_id
    )
    return await service.list_runs(current_user, params)


@bureau_unsupervised_refiling_router.post(
    "/refiling-runs/{bureau_refiling_run_id}/start",
    response_model=BureauUnsupervisedRefilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_bureau_unsupervised_refiling_run_endpoint(
    bureau_refiling_run_id: uuid.UUID,
    body: BureauUnsupervisedRefilingSubmitRequest,
    _: None = Depends(require_bureau_unsupervised_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauUnsupervisedRefilingService = Depends(get_bureau_unsupervised_refiling_service),
) -> BureauUnsupervisedRefilingRunResultResponse:
    return await service.submit_from_refiling_run(current_user, bureau_refiling_run_id, body)


@bureau_unsupervised_refiling_router.post(
    "/runs/{run_id}/approve",
    response_model=BureauUnsupervisedRefilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_bureau_unsupervised_refiling_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_bureau_unsupervised_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauUnsupervisedRefilingService = Depends(get_bureau_unsupervised_refiling_service),
) -> BureauUnsupervisedRefilingRunResultResponse:
    return await service.approve_run(current_user, run_id)
