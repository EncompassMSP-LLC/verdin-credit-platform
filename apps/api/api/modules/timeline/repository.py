"""Timeline event repository — append-only."""

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.timeline.models import TimelineEvent


@dataclass(frozen=True, slots=True)
class TimelineListFilters:
    organization_id: uuid.UUID
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    event_type: str | None = None
    event_category: str | None = None
    performed_by: uuid.UUID | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None
    skip: int = 0
    limit: int = 20
    sort_by: str = "occurred_at"
    sort_order: str = "desc"


_SORT_COLUMNS = {
    "occurred_at": TimelineEvent.occurred_at,
    "created_at": TimelineEvent.created_at,
    "event_type": TimelineEvent.event_type,
}


class TimelineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(self, event: TimelineEvent) -> TimelineEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def list_events(self, filters: TimelineListFilters) -> tuple[list[TimelineEvent], int]:
        base = select(TimelineEvent).where(TimelineEvent.organization_id == filters.organization_id)
        if filters.case_id is not None:
            base = base.where(TimelineEvent.case_id == filters.case_id)
        if filters.account_id is not None:
            base = base.where(TimelineEvent.account_id == filters.account_id)
        if filters.document_id is not None:
            base = base.where(TimelineEvent.document_id == filters.document_id)
        if filters.event_type is not None:
            base = base.where(TimelineEvent.event_type == filters.event_type)
        if filters.event_category is not None:
            base = base.where(TimelineEvent.event_category == filters.event_category)
        if filters.performed_by is not None:
            base = base.where(TimelineEvent.performed_by == filters.performed_by)
        if filters.occurred_from is not None:
            base = base.where(TimelineEvent.occurred_at >= filters.occurred_from)
        if filters.occurred_to is not None:
            base = base.where(TimelineEvent.occurred_at <= filters.occurred_to)

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        result = await self._session.execute(
            base.order_by(order).offset(filters.skip).limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(
        self,
        event_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> TimelineEvent | None:
        result = await self._session.execute(
            select(TimelineEvent).where(
                TimelineEvent.id == event_id,
                TimelineEvent.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()
