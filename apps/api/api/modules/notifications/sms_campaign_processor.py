"""Synchronous SMS marketing campaign enqueue processor."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.repository import UserRepository
from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
    SmsMarketingTriggerSource,
)
from api.modules.notifications.sms_campaign_repository import SmsMarketingCampaignRunRepository


@dataclass(frozen=True)
class SmsMarketingCampaignRunSummary:
    run: SmsMarketingCampaignRun
    completed_at: datetime


async def enqueue_sms_marketing_campaign(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    campaign_name: str,
    message_body: str,
    recipient_user_ids: list[uuid.UUID],
    performed_by_user_id: uuid.UUID | None,
    run_repo: SmsMarketingCampaignRunRepository | None = None,
    user_repo: UserRepository | None = None,
) -> SmsMarketingCampaignRunSummary:
    runs = run_repo or SmsMarketingCampaignRunRepository(session)
    users = user_repo or UserRepository(session)
    started_at = runs.utcnow()

    recipients_queued = len(recipient_user_ids)
    messages_sent = 0
    messages_failed = 0

    for user_id in recipient_user_ids:
        recipient = await users.get_by_id(user_id)
        if recipient is None or recipient.organization_id != organization_id:
            messages_failed += 1
            continue
        if not recipient.phone_number:
            messages_failed += 1
            continue
        messages_sent += 1

    run = await runs.create_run(
        organization_id=organization_id,
        campaign_name=campaign_name,
        message_body=message_body,
        recipient_user_ids=[str(user_id) for user_id in recipient_user_ids],
        trigger_source=SmsMarketingTriggerSource.MANUAL,
        status=SmsMarketingCampaignStatus.RUNNING,
        performed_by_user_id=performed_by_user_id,
        started_at=started_at,
        recipients_queued=recipients_queued,
    )

    completed_at = runs.utcnow()
    run.status = SmsMarketingCampaignStatus.COMPLETED
    run.messages_sent = messages_sent
    run.messages_failed = messages_failed
    run.completed_at = completed_at
    await session.flush()
    await session.refresh(run)
    return SmsMarketingCampaignRunSummary(run=run, completed_at=completed_at)
