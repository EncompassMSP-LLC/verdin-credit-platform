"""Admin-gated live unredacted benchmark blob export endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.reporting.live_unredacted_benchmark_blob_export_dependencies import (
    require_live_unredacted_benchmark_blob_export_enabled,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_schemas import (
    LiveUnredactedBenchmarkBlobExportRunListParams,
    LiveUnredactedBenchmarkBlobExportRunResponse,
    LiveUnredactedBenchmarkBlobExportRunResultResponse,
    LiveUnredactedBenchmarkBlobExportStatusResponse,
    LiveUnredactedBenchmarkBlobExportSubmitRequest,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_service import (
    LiveUnredactedBenchmarkBlobExportService,
)

live_unredacted_benchmark_blob_export_router = APIRouter(
    prefix="/live-unredacted-benchmark-blob-exports",
    tags=["Live Unredacted Benchmark Blob Export"],
)


def get_live_unredacted_benchmark_blob_export_service(
    db: AsyncSession = Depends(get_db),
) -> LiveUnredactedBenchmarkBlobExportService:
    return LiveUnredactedBenchmarkBlobExportService.from_session(db)


@live_unredacted_benchmark_blob_export_router.get(
    "/status",
    response_model=LiveUnredactedBenchmarkBlobExportStatusResponse,
)
async def get_live_unredacted_benchmark_blob_export_status_endpoint(
    _: None = Depends(require_live_unredacted_benchmark_blob_export_enabled),
    service: LiveUnredactedBenchmarkBlobExportService = Depends(
        get_live_unredacted_benchmark_blob_export_service
    ),
) -> LiveUnredactedBenchmarkBlobExportStatusResponse:
    return service.get_status_response()


@live_unredacted_benchmark_blob_export_router.get(
    "/runs",
    response_model=PaginatedResponse[LiveUnredactedBenchmarkBlobExportRunResponse],
)
async def list_live_unredacted_benchmark_blob_export_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_live_unredacted_benchmark_blob_export_enabled),
    current_user: User = Depends(get_current_user),
    service: LiveUnredactedBenchmarkBlobExportService = Depends(
        get_live_unredacted_benchmark_blob_export_service
    ),
) -> PaginatedResponse[LiveUnredactedBenchmarkBlobExportRunResponse]:
    params = LiveUnredactedBenchmarkBlobExportRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@live_unredacted_benchmark_blob_export_router.post(
    "/unredacted-export-runs/{unredacted_export_run_id}/start",
    response_model=LiveUnredactedBenchmarkBlobExportRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_live_unredacted_benchmark_blob_export_run_endpoint(
    unredacted_export_run_id: uuid.UUID,
    body: LiveUnredactedBenchmarkBlobExportSubmitRequest,
    _: None = Depends(require_live_unredacted_benchmark_blob_export_enabled),
    current_user: User = Depends(get_current_user),
    service: LiveUnredactedBenchmarkBlobExportService = Depends(
        get_live_unredacted_benchmark_blob_export_service
    ),
) -> LiveUnredactedBenchmarkBlobExportRunResultResponse:
    return await service.submit_from_unredacted_export_run(
        current_user,
        unredacted_export_run_id,
        body,
    )


@live_unredacted_benchmark_blob_export_router.post(
    "/runs/{run_id}/approve",
    response_model=LiveUnredactedBenchmarkBlobExportRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_live_unredacted_benchmark_blob_export_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_live_unredacted_benchmark_blob_export_enabled),
    current_user: User = Depends(get_current_user),
    service: LiveUnredactedBenchmarkBlobExportService = Depends(
        get_live_unredacted_benchmark_blob_export_service
    ),
) -> LiveUnredactedBenchmarkBlobExportRunResultResponse:
    return await service.approve_run(current_user, run_id)
