"""Notification repository — owns all Notification database access."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.notifications.schemas import NotificationSortField, NotificationSortOrder


@dataclass(frozen=True, slots=True)
class NotificationListFilters:
    organization_id: uuid.UUID
    recipient_user_id: uuid.UUID
    unread_only: bool | None = None
    category: NotificationCategory | None = None
    skip: int = 0
    limit: int = 20
    sort_by: NotificationSortField = "created_at"
    sort_order: NotificationSortOrder = "desc"


_SORT_COLUMNS: dict[NotificationSortField, InstrumentedAttribute[Any]] = {
    "created_at": Notification.created_at,
    "read_at": Notification.read_at,
}


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> Notification | None:
        result = await self._session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.organization_id == organization_id,
                Notification.recipient_user_id == recipient_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_and_count(
        self,
        filters: NotificationListFilters,
    ) -> tuple[list[Notification], int]:
        query = select(Notification).where(
            Notification.organization_id == filters.organization_id,
            Notification.recipient_user_id == filters.recipient_user_id,
        )
        if filters.unread_only:
            query = query.where(Notification.read_at.is_(None))
        if filters.category is not None:
            query = query.where(Notification.category == filters.category)

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        if filters.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count_unread(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.organization_id == organization_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.read_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def mark_read(
        self,
        notification: Notification,
        *,
        read_at: datetime | None = None,
    ) -> Notification:
        notification.read_at = read_at or datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def mark_all_read(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        read_at: datetime | None = None,
    ) -> None:
        timestamp = read_at or datetime.now(UTC)
        await self._session.execute(
            update(Notification)
            .where(
                Notification.organization_id == organization_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=timestamp)
        )
