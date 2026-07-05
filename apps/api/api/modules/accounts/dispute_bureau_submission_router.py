"""Admin-gated dispute bureau submission endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.dispute_bureau_submission_dependencies import (
    require_dispute_bureau_submission_enabled,
)
from api.modules.accounts.dispute_bureau_submission_schemas import (
    DisputeBureauSubmissionRequest,
    DisputeBureauSubmissionRunListParams,
    DisputeBureauSubmissionRunResponse,
    DisputeBureauSubmissionRunResultResponse,
    DisputeBureauSubmissionStatusResponse,
)
from api.modules.accounts.dispute_bureau_submission_service import DisputeBureauSubmissionService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

dispute_bureau_submission_router = APIRouter(
    prefix="/dispute-bureau-submission",
    tags=["Dispute Bureau Submission"],
)


def get_dispute_bureau_submission_service(
    db: AsyncSession = Depends(get_db),
) -> DisputeBureauSubmissionService:
    return DisputeBureauSubmissionService.from_session(db)


@dispute_bureau_submission_router.get(
    "/status", response_model=DisputeBureauSubmissionStatusResponse
)
async def get_dispute_bureau_submission_status_endpoint(
    _: None = Depends(require_dispute_bureau_submission_enabled),
    service: DisputeBureauSubmissionService = Depends(get_dispute_bureau_submission_service),
) -> DisputeBureauSubmissionStatusResponse:
    return service.get_status_response()


@dispute_bureau_submission_router.get(
    "/runs",
    response_model=PaginatedResponse[DisputeBureauSubmissionRunResponse],
)
async def list_dispute_bureau_submission_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_dispute_bureau_submission_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeBureauSubmissionService = Depends(get_dispute_bureau_submission_service),
) -> PaginatedResponse[DisputeBureauSubmissionRunResponse]:
    params = DisputeBureauSubmissionRunListParams(
        page=page, page_size=page_size, account_id=account_id
    )
    return await service.list_runs(current_user, params)


@dispute_bureau_submission_router.post(
    "/prep-runs/{filing_prep_run_id}/submit",
    response_model=DisputeBureauSubmissionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_dispute_bureau_submission_endpoint(
    filing_prep_run_id: uuid.UUID,
    body: DisputeBureauSubmissionRequest,
    _: None = Depends(require_dispute_bureau_submission_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeBureauSubmissionService = Depends(get_dispute_bureau_submission_service),
) -> DisputeBureauSubmissionRunResultResponse:
    return await service.submit_from_prep_run(current_user, filing_prep_run_id, body)


@dispute_bureau_submission_router.post(
    "/runs/{run_id}/approve",
    response_model=DisputeBureauSubmissionRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_dispute_bureau_submission_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_dispute_bureau_submission_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeBureauSubmissionService = Depends(get_dispute_bureau_submission_service),
) -> DisputeBureauSubmissionRunResultResponse:
    return await service.approve_run(current_user, run_id)
