"""HRIS bidirectional sync scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.dependencies import require_hris_bidirectional_sync_enabled
from api.modules.enterprise.hris_sync_schemas import (
    HrisBidirectionalSyncRunListParams,
    HrisBidirectionalSyncRunRequest,
    HrisBidirectionalSyncRunResponse,
    HrisBidirectionalSyncRunResultResponse,
    HrisBidirectionalSyncStatusResponse,
)
from api.modules.enterprise.hris_sync_service import HrisBidirectionalSyncService

hris_sync_router = APIRouter(prefix="/hris-sync", tags=["HRIS Bidirectional Sync"])


def get_hris_bidirectional_sync_service(
    db: AsyncSession = Depends(get_db),
) -> HrisBidirectionalSyncService:
    return HrisBidirectionalSyncService.from_session(db)


@hris_sync_router.get("/status", response_model=HrisBidirectionalSyncStatusResponse)
async def get_hris_bidirectional_sync_status_endpoint(
    _: None = Depends(require_hris_bidirectional_sync_enabled),
    service: HrisBidirectionalSyncService = Depends(get_hris_bidirectional_sync_service),
) -> HrisBidirectionalSyncStatusResponse:
    return service.get_status_response()


@hris_sync_router.get(
    "/runs",
    response_model=PaginatedResponse[HrisBidirectionalSyncRunResponse],
)
async def list_hris_bidirectional_sync_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_hris_bidirectional_sync_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisBidirectionalSyncService = Depends(get_hris_bidirectional_sync_service),
) -> PaginatedResponse[HrisBidirectionalSyncRunResponse]:
    params = HrisBidirectionalSyncRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@hris_sync_router.post(
    "/run",
    response_model=HrisBidirectionalSyncRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def run_hris_bidirectional_sync_endpoint(
    body: HrisBidirectionalSyncRunRequest,
    _: None = Depends(require_hris_bidirectional_sync_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisBidirectionalSyncService = Depends(get_hris_bidirectional_sync_service),
) -> HrisBidirectionalSyncRunResultResponse:
    return await service.run_sync(current_user, body)
