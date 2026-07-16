"""Reporting service — org-scoped operational read models."""

import uuid
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

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
from api.modules.accounts.models import AccountBureau
from api.modules.accounts.reinvestigation_analytics import (
    ReinvestigationOutcomeAnalytics as ReinvestigationOutcomeAnalyticsResult,
)
from api.modules.accounts.reinvestigation_analytics import (
    ReinvestigationOutcomeRow,
    compute_reinvestigation_outcome_analytics,
)
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
    ReinvestigationOutcomeAnalytics,
    ReinvestigationOutcomeAnalyticsResponse,
    ReinvestigationOutcomeBenchmarkPeriod,
    ReinvestigationOutcomeBenchmarksResponse,
    ReinvestigationOutcomeBureauBreakdown,
    ReinvestigationOutcomeFilters,
    ReinvestigationOutcomeRateDeltas,
    ReinvestigationOutcomeRecipientBreakdown,
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

    async def get_reinvestigation_outcomes(
        self,
        user: User,
        *,
        start: date | None = None,
        end: date | None = None,
        bureau: AccountBureau | None = None,
        group_by: str | None = None,
    ) -> ReinvestigationOutcomeAnalyticsResponse:
        """Per-org reinvestigation outcome analytics over recorded responses.

        Read-only aggregate (deletion / verification / correction / favorable
        rates + time-to-response) scoped to the caller's organization — no
        cross-tenant benchmarks and no live bureau contact. Optional ``start`` /
        ``end`` (by response day, inclusive) and ``bureau`` filters narrow the
        recorded responses; the applied filters are echoed back. When
        ``group_by="bureau"``, ``by_bureau`` carries a per-bureau roll-up of the
        same analytics shape so operators can compare all bureaus in one call.
        When ``group_by="recipient"``, ``by_recipient`` rolls up by the linked
        dispute letter's recipient type (credit bureau vs furnisher); unlinked
        responses are bucketed as ``unknown``.
        """
        self._require_read(user)
        organization_id = self._require_organization(user)
        if group_by is not None and group_by not in {"bureau", "recipient"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="group_by must be 'bureau', 'recipient', or omitted",
            )
        raw = await self._reporting.get_reinvestigation_outcomes(
            organization_id, start=start, end=end, bureau=bureau
        )
        result = compute_reinvestigation_outcome_analytics(
            [
                ReinvestigationOutcomeRow(
                    outcome=row["outcome"],
                    days_to_response=row["days_to_response"],
                )
                for row in raw
            ]
        )
        by_bureau: list[ReinvestigationOutcomeBureauBreakdown] = []
        by_recipient: list[ReinvestigationOutcomeRecipientBreakdown] = []
        if group_by == "bureau":
            by_bureau = self._build_bureau_breakdown(raw)
        elif group_by == "recipient":
            by_recipient = self._build_recipient_breakdown(raw)
        return ReinvestigationOutcomeAnalyticsResponse(
            generated_at=datetime.now(UTC),
            filters=ReinvestigationOutcomeFilters(
                start=start,
                end=end,
                bureau=bureau.value if bureau is not None else None,
                group_by=group_by,
            ),
            analytics=self._to_reinvestigation_analytics_schema(result),
            by_bureau=by_bureau,
            by_recipient=by_recipient,
        )

    async def get_reinvestigation_outcome_benchmarks(
        self,
        user: User,
        *,
        baseline_days: int | None = None,
        recent_days: int | None = None,
        bureau: AccountBureau | None = None,
    ) -> ReinvestigationOutcomeBenchmarksResponse:
        """Org-internal trailing baselines for reinvestigation outcome rates.

        Computes the same analytics shape over a trailing ``baseline_days``
        window and a nested ``recent_days`` window (both ending today, UTC),
        then returns advisory ``rate_deltas`` (recent minus baseline). Scoped
        strictly to the caller's organization — no cross-tenant data and no
        live bureau contact. When window args are omitted, org dispute-settings
        defaults apply (platform 90/30 when unset).
        """
        self._require_read(user)
        organization_id = self._require_organization(user)
        org_baseline, org_recent = await self._resolve_benchmark_window_defaults(organization_id)
        resolved_baseline = org_baseline if baseline_days is None else baseline_days
        resolved_recent = org_recent if recent_days is None else recent_days
        if resolved_baseline < 7 or resolved_baseline > 365:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="baseline_days must be between 7 and 365",
            )
        if resolved_recent < 1 or resolved_recent > resolved_baseline:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="recent_days must be between 1 and baseline_days",
            )

        end = datetime.now(UTC).date()
        baseline_start = end - timedelta(days=resolved_baseline - 1)
        recent_start = end - timedelta(days=resolved_recent - 1)

        baseline_raw = await self._reporting.get_reinvestigation_outcomes(
            organization_id, start=baseline_start, end=end, bureau=bureau
        )
        recent_raw = await self._reporting.get_reinvestigation_outcomes(
            organization_id, start=recent_start, end=end, bureau=bureau
        )

        baseline_result = compute_reinvestigation_outcome_analytics(
            [
                ReinvestigationOutcomeRow(
                    outcome=row["outcome"],
                    days_to_response=row["days_to_response"],
                )
                for row in baseline_raw
            ]
        )
        recent_result = compute_reinvestigation_outcome_analytics(
            [
                ReinvestigationOutcomeRow(
                    outcome=row["outcome"],
                    days_to_response=row["days_to_response"],
                )
                for row in recent_raw
            ]
        )
        baseline = self._to_reinvestigation_analytics_schema(baseline_result)
        recent = self._to_reinvestigation_analytics_schema(recent_result)
        return ReinvestigationOutcomeBenchmarksResponse(
            generated_at=datetime.now(UTC),
            scope="organization",
            bureau=bureau.value if bureau is not None else None,
            baseline_period=ReinvestigationOutcomeBenchmarkPeriod(
                start=baseline_start,
                end=end,
                window_days=resolved_baseline,
            ),
            baseline=baseline,
            recent_period=ReinvestigationOutcomeBenchmarkPeriod(
                start=recent_start,
                end=end,
                window_days=resolved_recent,
            ),
            recent=recent,
            rate_deltas=ReinvestigationOutcomeRateDeltas(
                deletion_rate=recent.deletion_rate - baseline.deletion_rate,
                verification_rate=recent.verification_rate - baseline.verification_rate,
                correction_rate=recent.correction_rate - baseline.correction_rate,
                favorable_rate=recent.favorable_rate - baseline.favorable_rate,
                no_response_rate=recent.no_response_rate - baseline.no_response_rate,
            ),
        )

    async def _resolve_benchmark_window_defaults(
        self, organization_id: uuid.UUID
    ) -> tuple[int, int]:
        from api.modules.org_admin.dispute_settings_models import (
            DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
            DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
        )
        from api.modules.org_admin.dispute_settings_repository import (
            OrganizationDisputeSettingsRepository,
        )

        if self._session is None:
            return (
                DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
                DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
            )
        settings = await OrganizationDisputeSettingsRepository(self._session).get_by_organization(
            organization_id
        )
        if settings is None:
            return (
                DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
                DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
            )
        return (
            settings.reinvestigation_benchmark_baseline_days,
            settings.reinvestigation_benchmark_recent_days,
        )

    @staticmethod
    def _to_reinvestigation_analytics_schema(
        result: ReinvestigationOutcomeAnalyticsResult,
    ) -> ReinvestigationOutcomeAnalytics:
        return ReinvestigationOutcomeAnalytics(
            total_responses=result.total_responses,
            counts=result.counts,
            deletion_rate=result.deletion_rate,
            verification_rate=result.verification_rate,
            correction_rate=result.correction_rate,
            favorable_rate=result.favorable_rate,
            no_response_rate=result.no_response_rate,
            avg_days_to_response=result.avg_days_to_response,
            median_days_to_response=result.median_days_to_response,
            measured_response_count=result.measured_response_count,
        )

    @classmethod
    def _build_bureau_breakdown(
        cls, raw: list[dict[str, object]]
    ) -> list[ReinvestigationOutcomeBureauBreakdown]:
        """Group raw response rows by bureau and compute per-bureau analytics."""
        by_bureau_rows: dict[str, list[ReinvestigationOutcomeRow]] = defaultdict(list)
        for row in raw:
            bureau_key = str(row.get("bureau") or "unknown")
            raw_days = row.get("days_to_response")
            days_to_response = raw_days if isinstance(raw_days, int) else None
            by_bureau_rows[bureau_key].append(
                ReinvestigationOutcomeRow(
                    outcome=str(row["outcome"]),
                    days_to_response=days_to_response,
                )
            )
        # Stable bureau ordering for deterministic responses.
        order = {"equifax": 0, "experian": 1, "transunion": 2}
        breakdown: list[ReinvestigationOutcomeBureauBreakdown] = []
        for bureau_key in sorted(by_bureau_rows, key=lambda b: (order.get(b, 9), b)):
            result = compute_reinvestigation_outcome_analytics(by_bureau_rows[bureau_key])
            breakdown.append(
                ReinvestigationOutcomeBureauBreakdown(
                    bureau=bureau_key,
                    analytics=cls._to_reinvestigation_analytics_schema(result),
                )
            )
        return breakdown

    @classmethod
    def _build_recipient_breakdown(
        cls, raw: list[dict[str, object]]
    ) -> list[ReinvestigationOutcomeRecipientBreakdown]:
        """Group raw response rows by recipient and compute per-recipient analytics."""
        by_recipient_rows: dict[str, list[ReinvestigationOutcomeRow]] = defaultdict(list)
        for row in raw:
            recipient_key = str(row.get("recipient") or "unknown")
            raw_days = row.get("days_to_response")
            days_to_response = raw_days if isinstance(raw_days, int) else None
            by_recipient_rows[recipient_key].append(
                ReinvestigationOutcomeRow(
                    outcome=str(row["outcome"]),
                    days_to_response=days_to_response,
                )
            )
        order = {"credit_bureau": 0, "furnisher": 1, "unknown": 9}
        breakdown: list[ReinvestigationOutcomeRecipientBreakdown] = []
        for recipient_key in sorted(by_recipient_rows, key=lambda r: (order.get(r, 5), r)):
            result = compute_reinvestigation_outcome_analytics(by_recipient_rows[recipient_key])
            breakdown.append(
                ReinvestigationOutcomeRecipientBreakdown(
                    recipient=recipient_key,
                    analytics=cls._to_reinvestigation_analytics_schema(result),
                )
            )
        return breakdown

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
