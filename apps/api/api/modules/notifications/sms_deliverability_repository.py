"""Repository for SMS deliverability dashboard aggregates."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.notifications.models import SmsDeliveryLog, SmsDeliveryLogStatus
from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
)


class SmsDeliverabilityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_campaign_runs(self, organization_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(SmsMarketingCampaignRun)
            .where(SmsMarketingCampaignRun.organization_id == organization_id)
        )
        return int(result.scalar_one())

    async def count_campaign_runs_by_status(
        self,
        organization_id: uuid.UUID,
        status: SmsMarketingCampaignStatus,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(SmsMarketingCampaignRun)
            .where(SmsMarketingCampaignRun.organization_id == organization_id)
            .where(SmsMarketingCampaignRun.status == status)
        )
        return int(result.scalar_one())

    async def count_delivery_logs_by_status(
        self,
        organization_id: uuid.UUID,
        status: SmsDeliveryLogStatus,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(SmsDeliveryLog)
            .where(SmsDeliveryLog.organization_id == organization_id)
            .where(SmsDeliveryLog.campaign_run_id.is_not(None))
            .where(SmsDeliveryLog.status == status)
        )
        return int(result.scalar_one())

    async def list_recent_campaign_outcomes(
        self,
        organization_id: uuid.UUID,
        *,
        limit: int = 5,
    ) -> list[SmsMarketingCampaignRun]:
        result = await self._session.execute(
            select(SmsMarketingCampaignRun)
            .where(SmsMarketingCampaignRun.organization_id == organization_id)
            .order_by(SmsMarketingCampaignRun.started_at.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())
