"""SMS delivery audit log repository."""

import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.notifications.models import SmsDeliveryLog


@dataclass(frozen=True, slots=True)
class SmsDeliveryLogListFilters:
    organization_id: uuid.UUID
    skip: int = 0
    limit: int = 20


class SmsDeliveryLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: SmsDeliveryLog) -> SmsDeliveryLog:
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def list_and_count(
        self,
        filters: SmsDeliveryLogListFilters,
    ) -> tuple[list[SmsDeliveryLog], int]:
        query = select(SmsDeliveryLog).where(
            SmsDeliveryLog.organization_id == filters.organization_id,
        )
        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        result = await self._session.execute(
            query.order_by(SmsDeliveryLog.created_at.desc())
            .offset(filters.skip)
            .limit(filters.limit)
        )
        return list(result.scalars().all()), total
