"""SMS marketing campaign delivery processor."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.sms_delivery import (
    SmsDeliveryNotReadyError,
    SmsMessage,
    get_sms_delivery_settings,
    get_sms_delivery_status,
    send_sms_message,
)
from api.modules.auth.repository import UserRepository
from api.modules.notifications.models import SmsDeliveryLog, SmsDeliveryLogStatus
from api.modules.notifications.sms_campaign_models import SmsMarketingCampaignStatus
from api.modules.notifications.sms_campaign_repository import SmsMarketingCampaignRunRepository
from api.modules.notifications.sms_delivery_repository import SmsDeliveryLogRepository


@dataclass(frozen=True)
class SmsMarketingCampaignDeliverySummary:
    messages_sent: int
    messages_failed: int
    completed_at: datetime
    status: SmsMarketingCampaignStatus
    error_message: str | None = None


async def deliver_sms_marketing_campaign_run(
    *,
    session: AsyncSession,
    campaign_run_id: uuid.UUID,
    run_repo: SmsMarketingCampaignRunRepository | None = None,
    user_repo: UserRepository | None = None,
    delivery_log_repo: SmsDeliveryLogRepository | None = None,
) -> SmsMarketingCampaignDeliverySummary:
    runs = run_repo or SmsMarketingCampaignRunRepository(session)
    users = user_repo or UserRepository(session)
    delivery_logs = delivery_log_repo or SmsDeliveryLogRepository(session)
    settings = get_sms_delivery_settings()
    delivery_status = get_sms_delivery_status(settings)

    run = await runs.get_run_by_id(campaign_run_id)
    if run is None:
        raise ValueError(f"Campaign run {campaign_run_id} not found")

    if run.status not in (
        SmsMarketingCampaignStatus.PENDING,
        SmsMarketingCampaignStatus.RUNNING,
    ):
        completed_at = run.completed_at or runs.utcnow()
        return SmsMarketingCampaignDeliverySummary(
            messages_sent=run.messages_sent,
            messages_failed=run.messages_failed,
            completed_at=completed_at,
            status=run.status,
            error_message=run.error_message,
        )

    started_at = run.started_at or runs.utcnow()
    run.status = SmsMarketingCampaignStatus.RUNNING
    run.started_at = started_at
    await session.flush()

    messages_sent = 0
    messages_failed = 0
    run_error: str | None = None

    if not delivery_status.ready:
        run_error = "; ".join(delivery_status.blockers)
    else:
        for user_id_raw in run.recipient_user_ids:
            user_id = uuid.UUID(str(user_id_raw))
            recipient = await users.get_by_id(user_id)
            if recipient is None or recipient.organization_id != run.organization_id:
                messages_failed += 1
                continue
            if not recipient.phone_number:
                messages_failed += 1
                continue

            send_result = None
            try:
                send_result = await send_sms_message(
                    SmsMessage(to=recipient.phone_number, body=run.message_body),
                    settings=settings,
                )
            except SmsDeliveryNotReadyError as exc:
                run_error = "; ".join(exc.blockers)
                messages_failed += 1
                await delivery_logs.create(
                    SmsDeliveryLog(
                        organization_id=run.organization_id,
                        campaign_run_id=run.id,
                        recipient_user_id=recipient.id,
                        recipient_phone=recipient.phone_number,
                        body=run.message_body,
                        provider=delivery_status.provider,
                        status=SmsDeliveryLogStatus.FAILED,
                        error_message=run_error,
                        sent_by_user_id=run.performed_by_user_id,
                    )
                )
                break

            if send_result is None:
                messages_failed += 1
                continue

            if send_result.success:
                messages_sent += 1
            else:
                messages_failed += 1

            await delivery_logs.create(
                SmsDeliveryLog(
                    organization_id=run.organization_id,
                    campaign_run_id=run.id,
                    recipient_user_id=recipient.id,
                    recipient_phone=recipient.phone_number,
                    body=run.message_body,
                    provider=delivery_status.provider,
                    status=(
                        SmsDeliveryLogStatus.SENT
                        if send_result.success
                        else SmsDeliveryLogStatus.FAILED
                    ),
                    provider_message_id=send_result.provider_message_id,
                    error_message=send_result.error,
                    sent_by_user_id=run.performed_by_user_id,
                )
            )

    completed_at = runs.utcnow()
    run.messages_sent = messages_sent
    run.messages_failed = messages_failed
    run.completed_at = completed_at
    run.error_message = run_error

    if run_error and messages_sent == 0:
        run.status = SmsMarketingCampaignStatus.FAILED
    else:
        run.status = SmsMarketingCampaignStatus.COMPLETED

    await session.flush()
    await session.refresh(run)
    return SmsMarketingCampaignDeliverySummary(
        messages_sent=messages_sent,
        messages_failed=messages_failed,
        completed_at=completed_at,
        status=run.status,
        error_message=run_error,
    )
