"""Reporting service — org-scoped operational read models."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.enterprise_reporting import get_enterprise_reporting_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.materialized_reporting import get_materialized_reporting_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.revenue_analytics import build_revenue_analytics
from api.core.stripe_billing import get_billing_status
from api.modules.auth.models import User
from api.modules.billing.repository import BillingRepository
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
from api.modules.reporting.repository import OperationsReportingRepository
from api.modules.reporting.schemas import (
    BureauPerformanceItem,
    BureauPerformanceReporting,
    BureauPerformanceReportingResponse,
    ClientReportingMetrics,
    EnterpriseReportingStatusResponse,
    MaterializedReportingStatusResponse,
    NotificationReportingMetrics,
    OperationsReporting,
    OperationsReportingResponse,
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
