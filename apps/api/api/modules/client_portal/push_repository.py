"""Portal push subscription and delivery repositories."""

import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.client_portal.push_models import (
    PortalPushDeliveryLog,
    PortalPushSubscription,
)


@dataclass(frozen=True, slots=True)
class PortalPushDeliveryLogListFilters:
    organization_id: uuid.UUID
    portal_user_id: uuid.UUID | None = None
    skip: int = 0
    limit: int = 20


class PortalPushSubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        subscription_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
    ) -> PortalPushSubscription | None:
        query = select(PortalPushSubscription).where(
            PortalPushSubscription.id == subscription_id,
            PortalPushSubscription.organization_id == organization_id,
            PortalPushSubscription.portal_user_id == portal_user_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_endpoint(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
        endpoint: str,
    ) -> PortalPushSubscription | None:
        query = select(PortalPushSubscription).where(
            PortalPushSubscription.organization_id == organization_id,
            PortalPushSubscription.portal_user_id == portal_user_id,
            PortalPushSubscription.endpoint == endpoint,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_active_for_portal_user(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
    ) -> list[PortalPushSubscription]:
        query = select(PortalPushSubscription).where(
            PortalPushSubscription.organization_id == organization_id,
            PortalPushSubscription.portal_user_id == portal_user_id,
            PortalPushSubscription.is_active.is_(True),
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_active_for_portal_user(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
    ) -> int:
        query = select(func.count()).where(
            PortalPushSubscription.organization_id == organization_id,
            PortalPushSubscription.portal_user_id == portal_user_id,
            PortalPushSubscription.is_active.is_(True),
        )
        return int((await self._session.execute(query)).scalar_one())

    async def create(self, subscription: PortalPushSubscription) -> PortalPushSubscription:
        self._session.add(subscription)
        await self._session.flush()
        await self._session.refresh(subscription)
        return subscription

    async def save(self, subscription: PortalPushSubscription) -> PortalPushSubscription:
        await self._session.flush()
        await self._session.refresh(subscription)
        return subscription

    async def deactivate(
        self,
        subscription_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID,
    ) -> bool:
        existing = await self.get_by_id(
            subscription_id,
            organization_id=organization_id,
            portal_user_id=portal_user_id,
        )
        if existing is None:
            return False
        existing.is_active = False
        await self._session.flush()
        return True


class PortalPushDeliveryLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: PortalPushDeliveryLog) -> PortalPushDeliveryLog:
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def list_logs(
        self,
        filters: PortalPushDeliveryLogListFilters,
    ) -> tuple[list[PortalPushDeliveryLog], int]:
        base = select(PortalPushDeliveryLog).where(
            PortalPushDeliveryLog.organization_id == filters.organization_id,
        )
        if filters.portal_user_id is not None:
            base = base.where(PortalPushDeliveryLog.portal_user_id == filters.portal_user_id)

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        query = (
            base.order_by(PortalPushDeliveryLog.created_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total
