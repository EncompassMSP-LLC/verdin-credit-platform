"""Repository for SMS marketing campaign runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
    SmsMarketingTriggerSource,
)


class SmsMarketingCampaignRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class SmsMarketingCampaignRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        campaign_name: str,
        message_body: str,
        recipient_user_ids: list[str],
        trigger_source: SmsMarketingTriggerSource,
        status: SmsMarketingCampaignStatus,
        performed_by_user_id: uuid.UUID | None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        recipients_queued: int = 0,
        messages_sent: int = 0,
        messages_failed: int = 0,
        error_message: str | None = None,
    ) -> SmsMarketingCampaignRun:
        run = SmsMarketingCampaignRun(
            organization_id=organization_id,
            campaign_name=campaign_name,
            message_body=message_body,
            recipient_user_ids=recipient_user_ids,
            trigger_source=trigger_source,
            status=status,
            performed_by_user_id=performed_by_user_id,
            started_at=started_at,
            completed_at=completed_at,
            recipients_queued=recipients_queued,
            messages_sent=messages_sent,
            messages_failed=messages_failed,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: SmsMarketingCampaignRunListFilters,
    ) -> tuple[list[SmsMarketingCampaignRun], int]:
        base = (
            select(SmsMarketingCampaignRun)
            .where(SmsMarketingCampaignRun.organization_id == organization_id)
            .order_by(SmsMarketingCampaignRun.started_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(SmsMarketingCampaignRun)
            .where(SmsMarketingCampaignRun.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
