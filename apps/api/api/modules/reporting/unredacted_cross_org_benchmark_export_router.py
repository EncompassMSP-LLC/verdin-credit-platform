"""Admin-gated unredacted cross-org benchmark export endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.reporting.unredacted_cross_org_benchmark_export_dependencies import (
    require_unredacted_cross_org_benchmark_export_enabled,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_schemas import (
    UnredactedCrossOrgBenchmarkExportRunListParams,
    UnredactedCrossOrgBenchmarkExportRunResponse,
    UnredactedCrossOrgBenchmarkExportRunResultResponse,
    UnredactedCrossOrgBenchmarkExportStatusResponse,
    UnredactedCrossOrgBenchmarkExportSubmitRequest,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_service import (
    UnredactedCrossOrgBenchmarkExportService,
)

unredacted_cross_org_benchmark_export_router = APIRouter(
    prefix="/unredacted-cross-org-benchmark-exports",
    tags=["Unredacted Cross-Org Benchmark Export"],
)


def get_unredacted_cross_org_benchmark_export_service(
    db: AsyncSession = Depends(get_db),
) -> UnredactedCrossOrgBenchmarkExportService:
    return UnredactedCrossOrgBenchmarkExportService.from_session(db)


@unredacted_cross_org_benchmark_export_router.get(
    "/status",
    response_model=UnredactedCrossOrgBenchmarkExportStatusResponse,
)
async def get_unredacted_cross_org_benchmark_export_status_endpoint(
    _: None = Depends(require_unredacted_cross_org_benchmark_export_enabled),
    service: UnredactedCrossOrgBenchmarkExportService = Depends(
        get_unredacted_cross_org_benchmark_export_service
    ),
) -> UnredactedCrossOrgBenchmarkExportStatusResponse:
    return service.get_status_response()


@unredacted_cross_org_benchmark_export_router.get(
    "/runs",
    response_model=PaginatedResponse[UnredactedCrossOrgBenchmarkExportRunResponse],
)
async def list_unredacted_cross_org_benchmark_export_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_unredacted_cross_org_benchmark_export_enabled),
    current_user: User = Depends(get_current_user),
    service: UnredactedCrossOrgBenchmarkExportService = Depends(
        get_unredacted_cross_org_benchmark_export_service
    ),
) -> PaginatedResponse[UnredactedCrossOrgBenchmarkExportRunResponse]:
    params = UnredactedCrossOrgBenchmarkExportRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@unredacted_cross_org_benchmark_export_router.post(
    "/benchmark-runs/{cross_org_benchmark_run_id}/start",
    response_model=UnredactedCrossOrgBenchmarkExportRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_unredacted_cross_org_benchmark_export_run_endpoint(
    cross_org_benchmark_run_id: uuid.UUID,
    body: UnredactedCrossOrgBenchmarkExportSubmitRequest,
    _: None = Depends(require_unredacted_cross_org_benchmark_export_enabled),
    current_user: User = Depends(get_current_user),
    service: UnredactedCrossOrgBenchmarkExportService = Depends(
        get_unredacted_cross_org_benchmark_export_service
    ),
) -> UnredactedCrossOrgBenchmarkExportRunResultResponse:
    return await service.submit_from_benchmark_run(
        current_user,
        cross_org_benchmark_run_id,
        body,
    )


@unredacted_cross_org_benchmark_export_router.post(
    "/runs/{run_id}/approve",
    response_model=UnredactedCrossOrgBenchmarkExportRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_unredacted_cross_org_benchmark_export_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_unredacted_cross_org_benchmark_export_enabled),
    current_user: User = Depends(get_current_user),
    service: UnredactedCrossOrgBenchmarkExportService = Depends(
        get_unredacted_cross_org_benchmark_export_service
    ),
) -> UnredactedCrossOrgBenchmarkExportRunResultResponse:
    return await service.approve_run(current_user, run_id)
