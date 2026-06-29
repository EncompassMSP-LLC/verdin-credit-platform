"""Dashboard API schemas — single aggregated operations snapshot."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from api.core.responses import BaseSchema

QueueEntityType = Literal["task", "case", "document"]


class DashboardKpis(BaseSchema):
    open_cases: int
    active_accounts: int
    pending_tasks: int
    documents_processing: int
    ocr_queue: int
    average_resolution_time_hours: float | None = None


class DashboardProcessing(BaseSchema):
    uploads_today: int
    ocr_running: int
    ocr_failed: int
    classification_pending: int
    metadata_pending: int
    entity_resolution_pending: int


class DashboardQueueItem(BaseSchema):
    id: uuid.UUID
    title: str
    subtitle: str | None = None
    entity_type: QueueEntityType
    priority: str | None = None
    due_date: datetime | None = None
    case_id: uuid.UUID | None = None
    case_number: str | None = None


class DashboardWorkQueue(BaseSchema):
    overdue_tasks: list[DashboardQueueItem] = Field(default_factory=list)
    high_priority_cases: list[DashboardQueueItem] = Field(default_factory=list)
    documents_requiring_review: list[DashboardQueueItem] = Field(default_factory=list)
    ocr_failures: list[DashboardQueueItem] = Field(default_factory=list)
    unresolved_entity_matches: list[DashboardQueueItem] = Field(default_factory=list)


class DashboardTimelineItem(BaseSchema):
    id: uuid.UUID
    occurred_at: datetime
    event_type: str
    title: str
    description: str | None = None
    case_id: uuid.UUID | None = None
    case_number: str | None = None
    document_id: uuid.UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DashboardAi(BaseSchema):
    documents_classified: int
    metadata_extracted: int
    entity_resolution_rate: float
    average_confidence: float | None = None
    ai_ready_documents: int


class DashboardPerformance(BaseSchema):
    average_accounts_per_case: float
    average_documents_per_case: float
    cases_opened_this_week: int
    cases_completed_this_month: int
    resolution_rate: float
    processing_throughput: int


class DashboardResponse(BaseSchema):
    """Aggregated operations command center snapshot.

    Designed for polling today (`refresh_seconds`) and future WebSocket push
    without changing the response contract.
    """

    generated_at: datetime
    refresh_seconds: int = 30
    kpis: DashboardKpis
    processing: DashboardProcessing
    tasks: DashboardWorkQueue
    timeline: list[DashboardTimelineItem]
    ai: DashboardAi
    performance: DashboardPerformance
