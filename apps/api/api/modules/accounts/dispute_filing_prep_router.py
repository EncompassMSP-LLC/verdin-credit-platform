"""Compliance-gated dispute filing prep endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.dispute_filing_prep_dependencies import (
    require_dispute_filing_prep_enabled,
)
from api.modules.accounts.dispute_filing_prep_schemas import (
    DisputeFilingPrepRequest,
    DisputeFilingPrepRunListParams,
    DisputeFilingPrepRunResponse,
    DisputeFilingPrepRunResultResponse,
    DisputeFilingPrepStatusResponse,
)
from api.modules.accounts.dispute_filing_prep_service import DisputeFilingPrepService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

dispute_filing_prep_router = APIRouter(prefix="/dispute-filing", tags=["Dispute Filing Prep"])


def get_dispute_filing_prep_service(
    db: AsyncSession = Depends(get_db),
) -> DisputeFilingPrepService:
    return DisputeFilingPrepService.from_session(db)


@dispute_filing_prep_router.get("/status", response_model=DisputeFilingPrepStatusResponse)
async def get_dispute_filing_prep_status_endpoint(
    _: None = Depends(require_dispute_filing_prep_enabled),
    service: DisputeFilingPrepService = Depends(get_dispute_filing_prep_service),
) -> DisputeFilingPrepStatusResponse:
    return service.get_status_response()


@dispute_filing_prep_router.get(
    "/runs", response_model=PaginatedResponse[DisputeFilingPrepRunResponse]
)
async def list_dispute_filing_prep_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: uuid.UUID | None = None,
    _: None = Depends(require_dispute_filing_prep_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeFilingPrepService = Depends(get_dispute_filing_prep_service),
) -> PaginatedResponse[DisputeFilingPrepRunResponse]:
    params = DisputeFilingPrepRunListParams(page=page, page_size=page_size, account_id=account_id)
    return await service.list_runs(current_user, params)


@dispute_filing_prep_router.post(
    "/runs/{run_id}/approve",
    response_model=DisputeFilingPrepRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_dispute_filing_prep_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_dispute_filing_prep_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeFilingPrepService = Depends(get_dispute_filing_prep_service),
) -> DisputeFilingPrepRunResultResponse:
    return await service.approve_run(current_user, run_id)


@dispute_filing_prep_router.post(
    "/accounts/{account_id}/prep",
    response_model=DisputeFilingPrepRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_dispute_filing_prep_endpoint(
    account_id: uuid.UUID,
    body: DisputeFilingPrepRequest,
    _: None = Depends(require_dispute_filing_prep_enabled),
    current_user: User = Depends(get_current_user),
    service: DisputeFilingPrepService = Depends(get_dispute_filing_prep_service),
) -> DisputeFilingPrepRunResultResponse:
    return await service.submit_prep(current_user, account_id, body)
