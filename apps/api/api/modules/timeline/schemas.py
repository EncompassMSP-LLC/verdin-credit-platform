"""Timeline API schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.timeline.models import TimelineEvent

TimelineSortField = Literal["occurred_at", "created_at", "event_type"]
TimelineSortOrder = Literal["asc", "desc"]


class TimelineEventResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID | None
    account_id: uuid.UUID | None
    document_id: uuid.UUID | None
    event_type: str
    event_category: str
    title: str
    description: str | None
    metadata: dict[str, Any]
    performed_by: uuid.UUID | None
    source_module: str
    occurred_at: datetime
    created_at: datetime

    @classmethod
    def from_model(cls, event: TimelineEvent) -> "TimelineEventResponse":
        return cls(
            id=event.id,
            organization_id=event.organization_id,
            case_id=event.case_id,
            account_id=event.account_id,
            document_id=event.document_id,
            event_type=event.event_type,
            event_category=event.event_category,
            title=event.title,
            description=event.description,
            metadata=dict(event.event_metadata or {}),
            performed_by=event.performed_by,
            source_module=event.source_module,
            occurred_at=event.occurred_at,
            created_at=event.created_at,
        )


class TimelineListParams(PaginationParams):
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    event_type: str | None = Field(default=None, max_length=100)
    event_category: str | None = Field(default=None, max_length=50)
    performed_by: uuid.UUID | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None
    sort_by: TimelineSortField = "occurred_at"
    sort_order: TimelineSortOrder = "desc"
