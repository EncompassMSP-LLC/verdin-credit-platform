"""Bureau response ingestion audit scaffold endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.compliance.bureau_response_ingestion_schemas import (
    BureauResponseIngestionRunListParams,
    BureauResponseIngestionRunResponse,
    BureauResponseIngestionRunResultResponse,
    BureauResponseIngestionStartRequest,
    BureauResponseIngestionStatusResponse,
)
from api.modules.compliance.bureau_response_ingestion_service import BureauResponseIngestionService

bureau_response_ingestion_router = APIRouter(
    prefix="/bureau-response-ingestion",
    tags=["Bureau Response Ingestion"],
)


def get_bureau_response_ingestion_service(
    db: AsyncSession = Depends(get_db),
) -> BureauResponseIngestionService:
    return BureauResponseIngestionService.from_session(db)


@bureau_response_ingestion_router.get(
    "/status",
    response_model=BureauResponseIngestionStatusResponse,
)
async def get_bureau_response_ingestion_status(
    service: BureauResponseIngestionService = Depends(get_bureau_response_ingestion_service),
) -> BureauResponseIngestionStatusResponse:
    return service.get_status_response()


@bureau_response_ingestion_router.get(
    "/runs",
    response_model=PaginatedResponse[BureauResponseIngestionRunResponse],
)
async def list_bureau_response_ingestion_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: BureauResponseIngestionService = Depends(get_bureau_response_ingestion_service),
) -> PaginatedResponse[BureauResponseIngestionRunResponse]:
    params = BureauResponseIngestionRunListParams(
        page=page,
        page_size=page_size,
        case_id=case_id,
        account_id=account_id,
    )
    return await service.list_runs(current_user, params)


@bureau_response_ingestion_router.get(
    "/runs/{run_id}",
    response_model=BureauResponseIngestionRunResponse,
)
async def get_bureau_response_ingestion_run(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BureauResponseIngestionService = Depends(get_bureau_response_ingestion_service),
) -> BureauResponseIngestionRunResponse:
    return await service.get_run(current_user, run_id)


@bureau_response_ingestion_router.post(
    "/runs",
    response_model=BureauResponseIngestionRunResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_bureau_response_ingestion_run(
    body: BureauResponseIngestionStartRequest,
    current_user: User = Depends(get_current_user),
    service: BureauResponseIngestionService = Depends(get_bureau_response_ingestion_service),
) -> BureauResponseIngestionRunResultResponse:
    return await service.start_run(current_user, body)
