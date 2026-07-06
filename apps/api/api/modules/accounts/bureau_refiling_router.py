"""Operator-gated bureau re-filing endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.bureau_refiling_dependencies import require_bureau_refiling_enabled
from api.modules.accounts.bureau_refiling_schemas import (
    BureauRefilingRunListParams,
    BureauRefilingRunResponse,
    BureauRefilingRunResultResponse,
    BureauRefilingStatusResponse,
    BureauRefilingSubmitRequest,
)
from api.modules.accounts.bureau_refiling_service import BureauRefilingService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

bureau_refiling_router = APIRouter(prefix="/bureau-refiling", tags=["Bureau Re-filing"])


def get_bureau_refiling_service(
    db: AsyncSession = Depends(get_db),
) -> BureauRefilingService:
    return BureauRefilingService.from_session(db)


@bureau_refiling_router.get("/status", response_model=BureauRefilingStatusResponse)
async def get_bureau_refiling_status_endpoint(
    _: None = Depends(require_bureau_refiling_enabled),
    service: BureauRefilingService = Depends(get_bureau_refiling_service),
) -> BureauRefilingStatusResponse:
    return service.get_status_response()


@bureau_refiling_router.get(
    "/runs",
    response_model=PaginatedResponse[BureauRefilingRunResponse],
)
async def list_bureau_refiling_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_bureau_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauRefilingService = Depends(get_bureau_refiling_service),
) -> PaginatedResponse[BureauRefilingRunResponse]:
    params = BureauRefilingRunListParams(page=page, page_size=page_size, account_id=account_id)
    return await service.list_runs(current_user, params)


@bureau_refiling_router.post(
    "/filing-runs/{autonomous_bureau_filing_run_id}/refile",
    response_model=BureauRefilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_bureau_refiling_run_endpoint(
    autonomous_bureau_filing_run_id: uuid.UUID,
    body: BureauRefilingSubmitRequest,
    _: None = Depends(require_bureau_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauRefilingService = Depends(get_bureau_refiling_service),
) -> BureauRefilingRunResultResponse:
    return await service.submit_from_filing_run(current_user, autonomous_bureau_filing_run_id, body)


@bureau_refiling_router.post(
    "/runs/{run_id}/approve",
    response_model=BureauRefilingRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_bureau_refiling_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_bureau_refiling_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauRefilingService = Depends(get_bureau_refiling_service),
) -> BureauRefilingRunResultResponse:
    return await service.approve_run(current_user, run_id)
