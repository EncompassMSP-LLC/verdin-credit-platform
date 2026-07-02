"""Reporting API schemas — read-optimized operational summaries."""

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
