"""Reporting API schemas — read-optimized operational summaries."""

import uuid
from datetime import datetime

from api.core.responses import BaseSchema


class ClientReportingMetrics(BaseSchema):
    total: int
    active: int
    portal_enabled: int


class NotificationReportingMetrics(BaseSchema):
    unread_total: int
    created_today: int


class OperationsReporting(BaseSchema):
    """Org-scoped operations read model for 4.8 reporting expansions."""

    clients: ClientReportingMetrics
    dispute_accounts: dict[str, int]
    dispute_letters: dict[str, int]
    notifications: NotificationReportingMetrics
    portal_users: int


class OperationsReportingResponse(BaseSchema):
    generated_at: datetime
    operations: OperationsReporting


class BureauPerformanceItem(BaseSchema):
    bureau: str
    total_accounts: int
    dispute_status: dict[str, int]
    sent_letters: int
    resolved_accounts: int


class BureauPerformanceReporting(BaseSchema):
    bureaus: list[BureauPerformanceItem]
    total_accounts: int


class BureauPerformanceReportingResponse(BaseSchema):
    generated_at: datetime
    bureau_performance: BureauPerformanceReporting


class TeamMemberProductivity(BaseSchema):
    user_id: uuid.UUID
    email: str
    full_name: str
    open_tasks: int
    completed_tasks_30d: int
    assigned_open_cases: int
    closed_cases_30d: int


class TeamProductivityReporting(BaseSchema):
    members: list[TeamMemberProductivity]
    open_tasks_total: int
    completed_tasks_30d_total: int
    assigned_open_cases_total: int
    closed_cases_30d_total: int


class TeamProductivityReportingResponse(BaseSchema):
    generated_at: datetime
    team_productivity: TeamProductivityReporting


class EnterpriseReportingStatusResponse(BaseSchema):
    enterprise_reporting_enabled: bool
    capabilities: list[str]
    deferred_capabilities: list[str]


class MaterializedReportingStatusResponse(BaseSchema):
    enabled: bool
    views: list[str]
    last_refreshed_at: datetime | None


class ReportingMvRefreshRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID | None
    trigger_source: str
    status: str
    views_refreshed: int
    started_at: datetime
    completed_at: datetime
    error_message: str | None

    @classmethod
    def from_model(cls, run: object) -> "ReportingMvRefreshRunResponse":
        from api.modules.reporting.materialized_models import ReportingMvRefreshRun

        if not isinstance(run, ReportingMvRefreshRun):
            raise TypeError("Expected ReportingMvRefreshRun")
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            trigger_source=run.trigger_source.value,
            status=run.status.value,
            views_refreshed=run.views_refreshed,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class ReportingMvRefreshRunListParams(BaseSchema):
    page: int = 1
    page_size: int = 20


class ReportingMvRefreshResultResponse(BaseSchema):
    views_refreshed: int
    run: ReportingMvRefreshRunResponse


class RevenueAnalytics(BaseSchema):
    billing_enabled: bool
    billing_ready: bool
    stripe_customer_configured: bool
    stripe_subscription_configured: bool
    subscription_active: bool
    subscription_status: str
    price_id: str | None
    current_period_end: datetime | None
    renewal_within_30_days: bool | None
    active_clients: int
    portal_enabled_clients: int
    portal_users: int
    readiness_score: int


class RevenueAnalyticsReportingResponse(BaseSchema):
    generated_at: datetime
    revenue_analytics: RevenueAnalytics


class PredictiveAnalyticsStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    blockers: list[str]


class PredictiveOutcomes(BaseSchema):
    cases_by_status: dict[str, int]
    accounts_by_dispute_status: dict[str, int]
    dispute_letters_by_status: dict[str, int]
    total_cases: int
    disputed_accounts: int
    cases_closed_30d: int
    cases_closed_90d: int
    accounts_dispute_resolved: int
    dispute_letters_sent: int
    case_closure_rate_90d: float | None
    dispute_resolution_rate: float | None
    outcome_score: int
    last_refreshed_at: datetime | None


class PredictiveOutcomesReportingResponse(BaseSchema):
    generated_at: datetime
    predictive_outcomes: PredictiveOutcomes


class PredictiveOutcomeRefreshRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    trigger_source: str
    status: str
    started_at: datetime
    completed_at: datetime
    error_message: str | None

    @classmethod
    def from_model(cls, run: object) -> "PredictiveOutcomeRefreshRunResponse":
        from api.modules.reporting.predictive_models import PredictiveOutcomeRefreshRun

        if not isinstance(run, PredictiveOutcomeRefreshRun):
            raise TypeError("Expected PredictiveOutcomeRefreshRun")
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            trigger_source=run.trigger_source.value,
            status=run.status.value,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class PredictiveOutcomeRefreshResultResponse(BaseSchema):
    refreshed_at: datetime
    run: PredictiveOutcomeRefreshRunResponse
