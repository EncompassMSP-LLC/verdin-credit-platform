"""Operator-gated bureau live API integration endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.bureau_live_api_dependencies import require_bureau_live_api_enabled
from api.modules.accounts.bureau_live_api_schemas import (
    BureauLiveApiInvokeRequest,
    BureauLiveApiRunListParams,
    BureauLiveApiRunResponse,
    BureauLiveApiRunResultResponse,
    BureauLiveApiStatusResponse,
)
from api.modules.accounts.bureau_live_api_service import BureauLiveApiService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

bureau_live_api_router = APIRouter(prefix="/bureau-live-api", tags=["Bureau Live API"])


def get_bureau_live_api_service(
    db: AsyncSession = Depends(get_db),
) -> BureauLiveApiService:
    return BureauLiveApiService.from_session(db)


@bureau_live_api_router.get("/status", response_model=BureauLiveApiStatusResponse)
async def get_bureau_live_api_status_endpoint(
    _: None = Depends(require_bureau_live_api_enabled),
    service: BureauLiveApiService = Depends(get_bureau_live_api_service),
) -> BureauLiveApiStatusResponse:
    return service.get_status_response()


@bureau_live_api_router.get(
    "/runs",
    response_model=PaginatedResponse[BureauLiveApiRunResponse],
)
async def list_bureau_live_api_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_bureau_live_api_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauLiveApiService = Depends(get_bureau_live_api_service),
) -> PaginatedResponse[BureauLiveApiRunResponse]:
    params = BureauLiveApiRunListParams(page=page, page_size=page_size, account_id=account_id)
    return await service.list_runs(current_user, params)


@bureau_live_api_router.post(
    "/submission-runs/{bureau_submission_run_id}/invoke",
    response_model=BureauLiveApiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_bureau_live_api_run_endpoint(
    bureau_submission_run_id: uuid.UUID,
    body: BureauLiveApiInvokeRequest,
    _: None = Depends(require_bureau_live_api_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauLiveApiService = Depends(get_bureau_live_api_service),
) -> BureauLiveApiRunResultResponse:
    return await service.submit_from_submission_run(current_user, bureau_submission_run_id, body)


@bureau_live_api_router.post(
    "/runs/{run_id}/approve",
    response_model=BureauLiveApiRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_bureau_live_api_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_bureau_live_api_enabled),
    current_user: User = Depends(get_current_user),
    service: BureauLiveApiService = Depends(get_bureau_live_api_service),
) -> BureauLiveApiRunResultResponse:
    return await service.approve_run(current_user, run_id)
