"""Platform event contract."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PlatformEvent:
    """Immutable domain event published through the event bus."""

    event_type: str
    event_category: str
    title: str
    organization_id: UUID
    source_module: str
    description: str | None = None
    case_id: UUID | None = None
    account_id: UUID | None = None
    document_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    performed_by: UUID | None = None
    occurred_at: datetime | None = None

    def resolved_occurred_at(self) -> datetime:
        return self.occurred_at or datetime.now(UTC)
