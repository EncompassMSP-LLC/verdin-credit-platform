"""Reporting service — org-scoped operational read models."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.cross_org_benchmark import get_cross_org_benchmark_status
from api.core.enterprise_reporting import get_enterprise_reporting_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.materialized_reporting import get_materialized_reporting_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.predictive_analytics import build_predictive_outcomes, get_predictive_analytics_status
from api.core.revenue_analytics import build_revenue_analytics
from api.core.stripe_billing import get_billing_status
from api.modules.auth.models import User
from api.modules.billing.repository import BillingRepository
from api.modules.reporting.cross_org_benchmark_repository import CrossOrgBenchmarkRepository
from api.modules.reporting.materialized_models import (
    ReportingMvRefreshStatus,
    ReportingMvTriggerSource,
)
from api.modules.reporting.materialized_refresh import refresh_reporting_materialized_views
from api.modules.reporting.materialized_repository import (
    ReportingMvRefreshRunListFilters,
    ReportingMvRefreshRunRepository,
)
from api.modules.reporting.permissions import REPORTING_ADMIN_ROLE, REPORTING_READ_ROLE
from api.modules.reporting.predictive_models import (
    PredictiveOutcomeRefreshStatus,
    PredictiveOutcomeTriggerSource,
)
from api.modules.reporting.predictive_refresh import refresh_predictive_outcomes
from api.modules.reporting.predictive_repository import PredictiveOutcomeSnapshotRepository
from api.modules.reporting.repository import OperationsReportingRepository
from api.modules.reporting.schemas import (
    BureauPerformanceItem,
    BureauPerformanceReporting,
    BureauPerformanceReportingResponse,
    ClientReportingMetrics,
    CrossOrgBenchmarkAnalytics,
    CrossOrgBenchmarkAnalyticsResponse,
    CrossOrgBenchmarkAnalyticsStatusResponse,
    CrossOrgBenchmarkRefreshResponse,
    CrossOrgBenchmarkRunResponse,
    EnterpriseReportingStatusResponse,
    MaterializedReportingStatusResponse,
    NotificationReportingMetrics,
    OperationsReporting,
    OperationsReportingResponse,
    PredictiveAnalyticsStatusResponse,
    PredictiveOutcomeRefreshResultResponse,
    PredictiveOutcomeRefreshRunResponse,
    PredictiveOutcomes,
    PredictiveOutcomesReportingResponse,
    ReportingMvRefreshResultResponse,
    ReportingMvRefreshRunListParams,
    ReportingMvRefreshRunResponse,
    RevenueAnalytics,
    RevenueAnalyticsReportingResponse,
    TeamMemberProductivity,
    TeamProductivityReporting,
    TeamProductivityReportingResponse,
)


class ReportingService:
    def __init__(
        self,
        repo: OperationsReportingRepository,
        *,
        session: AsyncSession | None = None,
    ) -> None:
        self._reporting = repo
        self._session = session
        self._mv_runs = ReportingMvRefreshRunRepository(session) if session is not None else None
        self._billing = BillingRepository(session) if session is not None else None
        self._predictive_snapshots = (
            PredictiveOutcomeSnapshotRepository(session) if session is not None else None
        )
        self._cross_org_benchmarks = (
            CrossOrgBenchmarkRepository(session) if session is not None else None
        )

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ReportingService":
        return cls(OperationsReportingRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_admin(self, user: User) -> None:
        if not has_permission(user.role, REPORTING_ADMIN_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage reporting",
            )

    def _use_materialized_views(self) -> bool:
        return is_feature_enabled(FeatureFlag.ENABLE_MATERIALIZED_REPORTING)

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, REPORTING_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view reporting",
            )

    async def get_operations_summary(self, user: User) -> OperationsReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        return await self.get_operations_summary_for_organization(organization_id)

    async def get_operations_summary_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> OperationsReportingResponse:
        raw = await self._reporting.get_operations_summary(organization_id)
        return OperationsReportingResponse(
            generated_at=datetime.now(UTC),
            operations=OperationsReporting(
                clients=ClientReportingMetrics(**raw["clients"]),
                dispute_accounts=raw["dispute_accounts"],
                dispute_letters=raw["dispute_letters"],
                notifications=NotificationReportingMetrics(**raw["notifications"]),
                portal_users=raw["portal_users"],
            ),
        )

    async def get_operations_metrics(self, user: User) -> OperationsReporting:
        """Return operations metrics without envelope (for dashboard embedding)."""
        response = await self.get_operations_summary(user)
        return response.operations

    async def get_enterprise_status(self, user: User) -> EnterpriseReportingStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return get_enterprise_reporting_status()

    async def get_bureau_performance(self, user: User) -> BureauPerformanceReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._use_materialized_views():
            raw = await self._reporting.get_bureau_performance_from_views(organization_id)
        else:
            raw = await self._reporting.get_bureau_performance(organization_id)
        return BureauPerformanceReportingResponse(
            generated_at=datetime.now(UTC),
            bureau_performance=BureauPerformanceReporting(
                bureaus=[BureauPerformanceItem(**item) for item in raw["bureaus"]],
                total_accounts=raw["total_accounts"],
            ),
        )

    async def get_team_productivity(self, user: User) -> TeamProductivityReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._use_materialized_views():
            raw = await self._reporting.get_team_productivity_from_views(organization_id)
        else:
            raw = await self._reporting.get_team_productivity(organization_id)
        return TeamProductivityReportingResponse(
            generated_at=datetime.now(UTC),
            team_productivity=TeamProductivityReporting(
                members=[TeamMemberProductivity(**item) for item in raw["members"]],
                open_tasks_total=raw["open_tasks_total"],
                completed_tasks_30d_total=raw["completed_tasks_30d_total"],
                assigned_open_cases_total=raw["assigned_open_cases_total"],
                closed_cases_30d_total=raw["closed_cases_30d_total"],
            ),
        )

    async def get_materialized_status(self, user: User) -> MaterializedReportingStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        if self._mv_runs is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Materialized reporting repository is not configured",
            )
        last_refreshed_at = await self._mv_runs.get_latest_started_at()
        return get_materialized_reporting_status(last_refreshed_at=last_refreshed_at)

    async def list_materialized_refresh_runs(
        self,
        user: User,
        params: ReportingMvRefreshRunListParams,
    ) -> PaginatedResponse[ReportingMvRefreshRunResponse]:
        self._require_read(user)
        self._require_organization(user)
        if self._mv_runs is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Materialized reporting repository is not configured",
            )
        skip = (params.page - 1) * params.page_size
        runs, total = await self._mv_runs.list_runs(
            ReportingMvRefreshRunListFilters(skip=skip, limit=params.page_size)
        )
        items = [ReportingMvRefreshRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def refresh_materialized_views(self, user: User) -> ReportingMvRefreshResultResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )
        summary = await refresh_reporting_materialized_views(
            self._session,
            trigger_source=ReportingMvTriggerSource.MANUAL,
            organization_id=organization_id,
            run_repo=self._mv_runs,
        )
        await self._session.commit()
        if summary.run.status is ReportingMvRefreshStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=summary.run.error_message or "Materialized view refresh failed",
            )
        return ReportingMvRefreshResultResponse(
            views_refreshed=summary.views_refreshed,
            run=ReportingMvRefreshRunResponse.from_model(summary.run),
        )

    async def get_revenue_analytics(self, user: User) -> RevenueAnalyticsReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._billing is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Billing repository is not configured",
            )

        billing_status = get_billing_status()
        account = await self._billing.get_billing_account(organization_id)
        operations = await self._reporting.get_operations_summary(organization_id)
        clients = operations["clients"]

        raw = build_revenue_analytics(
            billing_enabled=billing_status.enabled,
            billing_ready=billing_status.ready,
            account=account,
            active_clients=clients["active"],
            portal_enabled_clients=clients["portal_enabled"],
            portal_users=operations["portal_users"],
        )
        return RevenueAnalyticsReportingResponse(
            generated_at=datetime.now(UTC),
            revenue_analytics=RevenueAnalytics(**raw),
        )

    def get_predictive_status(self, user: User) -> PredictiveAnalyticsStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        status_value = get_predictive_analytics_status()
        return PredictiveAnalyticsStatusResponse(
            enabled=status_value.enabled,
            ready=status_value.ready,
            blockers=list(status_value.blockers),
        )

    async def get_predictive_outcomes(self, user: User) -> PredictiveOutcomesReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._predictive_snapshots is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Predictive analytics repository is not configured",
            )

        snapshot = await self._predictive_snapshots.get_snapshot(organization_id)
        if snapshot is not None:
            raw = dict(snapshot.payload)
            raw["last_refreshed_at"] = snapshot.refreshed_at
        else:
            historical = await self._reporting.get_historical_outcome_raw(organization_id)
            raw = build_predictive_outcomes(**historical, last_refreshed_at=None)

        return PredictiveOutcomesReportingResponse(
            generated_at=datetime.now(UTC),
            predictive_outcomes=PredictiveOutcomes(**raw),
        )

    async def refresh_predictive_outcomes(
        self, user: User
    ) -> PredictiveOutcomeRefreshResultResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not configured",
            )

        summary = await refresh_predictive_outcomes(
            self._session,
            organization_id=organization_id,
            trigger_source=PredictiveOutcomeTriggerSource.MANUAL,
            snapshot_repo=self._predictive_snapshots,
        )
        await self._session.commit()
        if summary.run.status is PredictiveOutcomeRefreshStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=summary.run.error_message or "Predictive outcome refresh failed",
            )
        return PredictiveOutcomeRefreshResultResponse(
            refreshed_at=summary.refreshed_at,
            run=PredictiveOutcomeRefreshRunResponse.from_model(summary.run),
        )

    def get_cross_org_benchmark_status(
        self, user: User
    ) -> CrossOrgBenchmarkAnalyticsStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        status_value = get_cross_org_benchmark_status()
        return CrossOrgBenchmarkAnalyticsStatusResponse(
            enabled=status_value.enabled,
            ready=status_value.ready,
            blockers=list(status_value.blockers),
        )

    async def get_cross_org_benchmark_summary(
        self, user: User
    ) -> CrossOrgBenchmarkAnalyticsResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._cross_org_benchmarks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cross-org benchmark repository is not configured",
            )
        summary = await self._cross_org_benchmarks.build_summary(organization_id)
        return CrossOrgBenchmarkAnalyticsResponse(
            generated_at=datetime.now(UTC),
            benchmarks=CrossOrgBenchmarkAnalytics(
                organization_id=summary.organization_id,
                active_clients=summary.active_clients,
                open_cases=summary.open_cases,
                resolved_accounts=summary.resolved_accounts,
                cohort_average_active_clients=summary.cohort_average_active_clients,
                cohort_average_open_cases=summary.cohort_average_open_cases,
                cohort_average_resolved_accounts=summary.cohort_average_resolved_accounts,
                active_clients_percentile=summary.active_clients_percentile,
                open_cases_percentile=summary.open_cases_percentile,
                resolved_accounts_percentile=summary.resolved_accounts_percentile,
                organizations_evaluated=summary.organizations_evaluated,
            ),
        )

    async def refresh_cross_org_benchmarks(self, user: User) -> CrossOrgBenchmarkRefreshResponse:
        self._require_admin(user)
        organization_id = self._require_organization(user)
        if self._cross_org_benchmarks is None or self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cross-org benchmark repository is not configured",
            )
        summary = await self._cross_org_benchmarks.build_summary(organization_id)
        run = await self._cross_org_benchmarks.create_run(
            requested_by_id=user.id,
            organizations_evaluated=summary.organizations_evaluated,
        )
        await self._session.commit()
        return CrossOrgBenchmarkRefreshResponse(
            generated_at=run.generated_at,
            run=CrossOrgBenchmarkRunResponse(
                id=run.id,
                requested_by_id=run.requested_by_id,
                trigger_source=run.trigger_source.value,
                status=run.status.value,
                organizations_evaluated=run.organizations_evaluated,
                generated_at=run.generated_at,
                error_message=run.error_message,
            ),
        )

    async def list_cross_org_benchmark_runs(self, user: User) -> list[CrossOrgBenchmarkRunResponse]:
        self._require_read(user)
        self._require_organization(user)
        if self._cross_org_benchmarks is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cross-org benchmark repository is not configured",
            )
        runs = await self._cross_org_benchmarks.list_runs()
        return [
            CrossOrgBenchmarkRunResponse(
                id=run.id,
                requested_by_id=run.requested_by_id,
                trigger_source=run.trigger_source.value,
                status=run.status.value,
                organizations_evaluated=run.organizations_evaluated,
                generated_at=run.generated_at,
                error_message=run.error_message,
            )
            for run in runs
        ]
