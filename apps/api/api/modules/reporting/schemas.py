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
