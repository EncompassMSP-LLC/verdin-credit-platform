"""Reporting endpoints — read-optimized operational summaries."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.models import AccountBureau
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.billing.dependencies import require_billing_enabled
from api.modules.reporting.dependencies import (
    get_reporting_organization_id,
    require_cross_org_benchmark_analytics_enabled,
    require_materialized_reporting_enabled,
    require_predictive_analytics_enabled,
)
from api.modules.reporting.live_unredacted_benchmark_blob_export_router import (
    live_unredacted_benchmark_blob_export_router,
)
from api.modules.reporting.schemas import (
    BureauPerformanceReportingResponse,
    CrossOrgBenchmarkAnalyticsResponse,
    CrossOrgBenchmarkAnalyticsStatusResponse,
    CrossOrgBenchmarkRefreshResponse,
    CrossOrgBenchmarkRunResponse,
    EnterpriseReportingStatusResponse,
    MaterializedReportingStatusResponse,
    OperationsReportingResponse,
    PredictiveAnalyticsStatusResponse,
    PredictiveOutcomeRefreshResultResponse,
    PredictiveOutcomesReportingResponse,
    ReinvestigationOutcomeAnalyticsResponse,
    ReinvestigationOutcomeBenchmarksResponse,
    ReportingMvRefreshResultResponse,
    ReportingMvRefreshRunListParams,
    ReportingMvRefreshRunResponse,
    RevenueAnalyticsReportingResponse,
    TeamProductivityReportingResponse,
)
from api.modules.reporting.service import ReportingService
from api.modules.reporting.unredacted_cross_org_benchmark_export_router import (
    unredacted_cross_org_benchmark_export_router,
)

router = APIRouter(prefix="/reporting", tags=["Reporting"])


def get_reporting_service(db: AsyncSession = Depends(get_db)) -> ReportingService:
    return ReportingService.from_session(db)


@router.get("/operations", response_model=OperationsReportingResponse)
async def get_operations_reporting(
    organization_id: uuid.UUID = Depends(get_reporting_organization_id),
    service: ReportingService = Depends(get_reporting_service),
) -> OperationsReportingResponse:
    """Return org-scoped operations reporting read model."""
    return await service.get_operations_summary_for_organization(organization_id)


@router.get("/status", response_model=EnterpriseReportingStatusResponse)
async def get_enterprise_reporting_status(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> EnterpriseReportingStatusResponse:
    return await service.get_enterprise_status(current_user)


@router.get("/bureau-performance", response_model=BureauPerformanceReportingResponse)
async def get_bureau_performance_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> BureauPerformanceReportingResponse:
    return await service.get_bureau_performance(current_user)


@router.get("/team-productivity", response_model=TeamProductivityReportingResponse)
async def get_team_productivity_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> TeamProductivityReportingResponse:
    return await service.get_team_productivity(current_user)


@router.get(
    "/reinvestigation-outcomes/benchmarks",
    response_model=ReinvestigationOutcomeBenchmarksResponse,
)
async def get_reinvestigation_outcome_benchmarks_reporting(
    baseline_days: int | None = Query(
        None, ge=7, le=365, description="Trailing baseline window; omit to use org default"
    ),
    recent_days: int | None = Query(
        None,
        ge=1,
        le=365,
        description="Recent comparison window; omit to use org default (must be <= baseline)",
    ),
    bureau: AccountBureau | None = Query(None, description="Filter to a single credit bureau"),
    group_by: str | None = Query(
        None, description="Optional roll-up dimension; currently only 'bureau'"
    ),
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> ReinvestigationOutcomeBenchmarksResponse:
    """Org-internal trailing baselines for reinvestigation outcomes (no cross-tenant data)."""
    return await service.get_reinvestigation_outcome_benchmarks(
        current_user,
        baseline_days=baseline_days,
        recent_days=recent_days,
        bureau=bureau,
        group_by=group_by,
    )


@router.get("/reinvestigation-outcomes", response_model=ReinvestigationOutcomeAnalyticsResponse)
async def get_reinvestigation_outcomes_reporting(
    start: date | None = Query(None, description="Filter by response day (inclusive lower bound)"),
    end: date | None = Query(None, description="Filter by response day (inclusive upper bound)"),
    bureau: AccountBureau | None = Query(None, description="Filter to a single credit bureau"),
    group_by: str | None = Query(
        None, description="Optional roll-up dimension; 'bureau' or 'recipient'"
    ),
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> ReinvestigationOutcomeAnalyticsResponse:
    """Org-scoped reinvestigation outcome analytics (computed over recorded responses)."""
    return await service.get_reinvestigation_outcomes(
        current_user, start=start, end=end, bureau=bureau, group_by=group_by
    )


@router.get(
    "/revenue",
    response_model=RevenueAnalyticsReportingResponse,
    dependencies=[Depends(require_billing_enabled)],
)
async def get_revenue_analytics_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> RevenueAnalyticsReportingResponse:
    return await service.get_revenue_analytics(current_user)


@router.get(
    "/predictive/status",
    response_model=PredictiveAnalyticsStatusResponse,
    dependencies=[Depends(require_predictive_analytics_enabled)],
)
async def get_predictive_analytics_status(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> PredictiveAnalyticsStatusResponse:
    return service.get_predictive_status(current_user)


@router.get(
    "/predictive/outcomes",
    response_model=PredictiveOutcomesReportingResponse,
    dependencies=[Depends(require_predictive_analytics_enabled)],
)
async def get_predictive_outcomes_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> PredictiveOutcomesReportingResponse:
    return await service.get_predictive_outcomes(current_user)


@router.post(
    "/predictive/refresh",
    response_model=PredictiveOutcomeRefreshResultResponse,
    dependencies=[Depends(require_predictive_analytics_enabled)],
)
async def refresh_predictive_outcomes_reporting(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> PredictiveOutcomeRefreshResultResponse:
    return await service.refresh_predictive_outcomes(current_user)


@router.get(
    "/cross-org-benchmarks/status",
    response_model=CrossOrgBenchmarkAnalyticsStatusResponse,
    dependencies=[Depends(require_cross_org_benchmark_analytics_enabled)],
)
async def get_cross_org_benchmark_status(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> CrossOrgBenchmarkAnalyticsStatusResponse:
    return service.get_cross_org_benchmark_status(current_user)


@router.get(
    "/cross-org-benchmarks",
    response_model=CrossOrgBenchmarkAnalyticsResponse,
    dependencies=[Depends(require_cross_org_benchmark_analytics_enabled)],
)
async def get_cross_org_benchmark_summary(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> CrossOrgBenchmarkAnalyticsResponse:
    return await service.get_cross_org_benchmark_summary(current_user)


@router.get(
    "/cross-org-benchmarks/runs",
    response_model=list[CrossOrgBenchmarkRunResponse],
    dependencies=[Depends(require_cross_org_benchmark_analytics_enabled)],
)
async def list_cross_org_benchmark_runs(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> list[CrossOrgBenchmarkRunResponse]:
    return await service.list_cross_org_benchmark_runs(current_user)


@router.post(
    "/cross-org-benchmarks/refresh",
    response_model=CrossOrgBenchmarkRefreshResponse,
    dependencies=[Depends(require_cross_org_benchmark_analytics_enabled)],
)
async def refresh_cross_org_benchmarks(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> CrossOrgBenchmarkRefreshResponse:
    return await service.refresh_cross_org_benchmarks(current_user)


@router.get(
    "/materialized-views/status",
    response_model=MaterializedReportingStatusResponse,
    dependencies=[Depends(require_materialized_reporting_enabled)],
)
async def get_materialized_reporting_status(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> MaterializedReportingStatusResponse:
    return await service.get_materialized_status(current_user)


@router.get(
    "/materialized-views/runs",
    response_model=PaginatedResponse[ReportingMvRefreshRunResponse],
    dependencies=[Depends(require_materialized_reporting_enabled)],
)
async def list_materialized_refresh_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> PaginatedResponse[ReportingMvRefreshRunResponse]:
    params = ReportingMvRefreshRunListParams(page=page, page_size=page_size)
    return await service.list_materialized_refresh_runs(current_user, params)


@router.post(
    "/materialized-views/refresh",
    response_model=ReportingMvRefreshResultResponse,
    dependencies=[Depends(require_materialized_reporting_enabled)],
)
async def refresh_materialized_reporting_views(
    current_user: User = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
) -> ReportingMvRefreshResultResponse:
    return await service.refresh_materialized_views(current_user)


router.include_router(unredacted_cross_org_benchmark_export_router)
router.include_router(live_unredacted_benchmark_blob_export_router)
