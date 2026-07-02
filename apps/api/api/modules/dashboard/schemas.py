"""Dashboard API schemas — Mission Control product snapshot."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.reporting.schemas import OperationsReporting

AlertType = Literal[
    "ocr_failure",
    "unmatched_entity",
    "document_review",
    "overdue_task",
]
AlertSeverity = Literal["critical", "high", "medium"]
AlertEntityType = Literal["task", "case", "document"]


class DashboardOverview(BaseSchema):
    """Executive strip — what is happening right now."""

    open_cases: int
    active_accounts: int
    documents: int
    tasks_due_today: int
    overdue_tasks: int
    alert_count: int


class DashboardCases(BaseSchema):
    open: int
    high_priority: int
    created_today: int
    closed_today: int
    average_resolution_time_hours: float | None = None


class DashboardAccounts(BaseSchema):
    active: int
    total: int
    per_case: float


class DashboardDocuments(BaseSchema):
    total: int
    processing: int
    classification_confidence: float | None = None
    entity_resolution_confidence: float | None = None
    ai_ready: int
    unresolved: int


class DashboardTasks(BaseSchema):
    pending: int
    due_today: int
    overdue: int


class DashboardProcessing(BaseSchema):
    ocr_queue: int
    ocr_failed: int
    classification_pending: int
    metadata_pending: int
    entity_resolution_pending: int


class DashboardPerformance(BaseSchema):
    cases_created_today: int
    cases_closed_today: int
    average_resolution_time_hours: float | None = None
    documents_per_case: float
    accounts_per_case: float


class DashboardTimelineItem(BaseSchema):
    id: uuid.UUID
    occurred_at: datetime
    event_type: str
    title: str
    description: str | None = None
    case_id: uuid.UUID | None = None
    case_number: str | None = None
    document_id: uuid.UUID | None = None
    document_title: str | None = None
    file_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DashboardAlertItem(BaseSchema):
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    entity_type: AlertEntityType
    entity_id: uuid.UUID
    case_id: uuid.UUID | None = None
    case_number: str | None = None


class DashboardAlerts(BaseSchema):
    total: int
    items: list[DashboardAlertItem] = Field(default_factory=list)


class DashboardResponse(BaseSchema):
    """Mission Control snapshot — one request, full operational picture.

    Designed for polling today (`refresh_seconds`) and future WebSocket push
    without changing the response contract.
    """

    generated_at: datetime
    refresh_seconds: int = 30
    overview: DashboardOverview
    cases: DashboardCases
    accounts: DashboardAccounts
    documents: DashboardDocuments
    timeline: list[DashboardTimelineItem]
    tasks: DashboardTasks
    processing: DashboardProcessing
    performance: DashboardPerformance
    alerts: DashboardAlerts
    operations: OperationsReporting
