"""Map platform events to timeline rows."""

import uuid
from typing import Any

from verdin_event_bus import PlatformEvent

from api.modules.timeline.models import TimelineEvent


def timeline_event_from_platform(event: PlatformEvent) -> TimelineEvent:
    return TimelineEvent(
        id=uuid.uuid4(),
        organization_id=event.organization_id,
        case_id=event.case_id,
        account_id=event.account_id,
        document_id=event.document_id,
        event_type=event.event_type,
        event_category=event.event_category,
        title=event.title,
        description=event.description,
        event_metadata=dict(event.metadata),
        performed_by=event.performed_by,
        source_module=event.source_module,
        occurred_at=event.resolved_occurred_at(),
    )


async def persist_platform_event(event: PlatformEvent, context: dict[str, Any]) -> None:
    session = context.get("session")
    if session is None:
        return
    from api.modules.timeline.repository import TimelineRepository

    repo = TimelineRepository(session)
    await repo.append(timeline_event_from_platform(event))
