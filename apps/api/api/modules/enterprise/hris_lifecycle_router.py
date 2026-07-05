"""Admin-gated HRIS lifecycle sync endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.hris_lifecycle_dependencies import require_hris_lifecycle_sync_enabled
from api.modules.enterprise.hris_lifecycle_schemas import (
    HrisLifecycleSyncRunListParams,
    HrisLifecycleSyncRunResponse,
    HrisLifecycleSyncRunResultResponse,
    HrisLifecycleSyncStatusResponse,
    HrisLifecycleSyncSubmitRequest,
)
from api.modules.enterprise.hris_lifecycle_service import HrisLifecycleSyncService

hris_lifecycle_router = APIRouter(prefix="/hris-lifecycle", tags=["HRIS Lifecycle Sync"])


def get_hris_lifecycle_sync_service(
    db: AsyncSession = Depends(get_db),
) -> HrisLifecycleSyncService:
    return HrisLifecycleSyncService.from_session(db)


@hris_lifecycle_router.get("/status", response_model=HrisLifecycleSyncStatusResponse)
async def get_hris_lifecycle_sync_status_endpoint(
    _: None = Depends(require_hris_lifecycle_sync_enabled),
    service: HrisLifecycleSyncService = Depends(get_hris_lifecycle_sync_service),
) -> HrisLifecycleSyncStatusResponse:
    return service.get_status_response()


@hris_lifecycle_router.get(
    "/runs",
    response_model=PaginatedResponse[HrisLifecycleSyncRunResponse],
)
async def list_hris_lifecycle_sync_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_hris_lifecycle_sync_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisLifecycleSyncService = Depends(get_hris_lifecycle_sync_service),
) -> PaginatedResponse[HrisLifecycleSyncRunResponse]:
    params = HrisLifecycleSyncRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@hris_lifecycle_router.post(
    "/sync-runs/{hris_bidirectional_sync_run_id}/start",
    response_model=HrisLifecycleSyncRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_hris_lifecycle_sync_run_endpoint(
    hris_bidirectional_sync_run_id: uuid.UUID,
    body: HrisLifecycleSyncSubmitRequest,
    _: None = Depends(require_hris_lifecycle_sync_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisLifecycleSyncService = Depends(get_hris_lifecycle_sync_service),
) -> HrisLifecycleSyncRunResultResponse:
    return await service.submit_from_bidirectional_run(
        current_user, hris_bidirectional_sync_run_id, body
    )


@hris_lifecycle_router.post(
    "/runs/{run_id}/approve",
    response_model=HrisLifecycleSyncRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_hris_lifecycle_sync_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_hris_lifecycle_sync_enabled),
    current_user: User = Depends(get_current_user),
    service: HrisLifecycleSyncService = Depends(get_hris_lifecycle_sync_service),
) -> HrisLifecycleSyncRunResultResponse:
    return await service.approve_run(current_user, run_id)
