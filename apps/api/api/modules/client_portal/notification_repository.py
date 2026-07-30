"""Portal notification repository — owns portal_notifications access."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.client_portal.notification_models import PortalNotification
from api.modules.notifications.models import NotificationCategory
from api.modules.notifications.schemas import NotificationSortField, NotificationSortOrder


@dataclass(frozen=True, slots=True)
class PortalNotificationListFilters:
    organization_id: uuid.UUID
    recipient_portal_user_id: uuid.UUID
    client_id: uuid.UUID
    unread_only: bool | None = None
    category: NotificationCategory | None = None
    skip: int = 0
    limit: int = 20
    sort_by: NotificationSortField = "created_at"
    sort_order: NotificationSortOrder = "desc"


_SORT_COLUMNS: dict[NotificationSortField, InstrumentedAttribute[Any]] = {
    "created_at": PortalNotification.created_at,
    "read_at": PortalNotification.read_at,
}


class PortalNotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: PortalNotification) -> PortalNotification:
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        recipient_portal_user_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> PortalNotification | None:
        result = await self._session.execute(
            select(PortalNotification).where(
                PortalNotification.id == notification_id,
                PortalNotification.organization_id == organization_id,
                PortalNotification.recipient_portal_user_id == recipient_portal_user_id,
                PortalNotification.client_id == client_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_and_count(
        self,
        filters: PortalNotificationListFilters,
    ) -> tuple[list[PortalNotification], int]:
        query = select(PortalNotification).where(
            PortalNotification.organization_id == filters.organization_id,
            PortalNotification.recipient_portal_user_id == filters.recipient_portal_user_id,
            PortalNotification.client_id == filters.client_id,
        )
        if filters.unread_only:
            query = query.where(PortalNotification.read_at.is_(None))
        if filters.category is not None:
            query = query.where(PortalNotification.category == filters.category)

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        if filters.sort_order == "asc":
            query = query.order_by(sort_column.asc(), PortalNotification.id.asc())
        else:
            query = query.order_by(sort_column.desc(), PortalNotification.id.desc())

        query = query.offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count_unread(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_portal_user_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(PortalNotification)
            .where(
                PortalNotification.organization_id == organization_id,
                PortalNotification.recipient_portal_user_id == recipient_portal_user_id,
                PortalNotification.client_id == client_id,
                PortalNotification.read_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def mark_read(
        self,
        notification: PortalNotification,
        *,
        read_at: datetime | None = None,
    ) -> PortalNotification:
        if notification.read_at is None:
            notification.read_at = read_at or datetime.now(UTC)
            await self._session.flush()
            await self._session.refresh(notification)
        return notification

    async def mark_all_read(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_portal_user_id: uuid.UUID,
        client_id: uuid.UUID,
        read_at: datetime | None = None,
    ) -> None:
        timestamp = read_at or datetime.now(UTC)
        await self._session.execute(
            update(PortalNotification)
            .where(
                PortalNotification.organization_id == organization_id,
                PortalNotification.recipient_portal_user_id == recipient_portal_user_id,
                PortalNotification.client_id == client_id,
                PortalNotification.read_at.is_(None),
            )
            .values(read_at=timestamp)
        )
