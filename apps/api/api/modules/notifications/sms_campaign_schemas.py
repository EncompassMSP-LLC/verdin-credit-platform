"""Pydantic schemas for SMS marketing campaign scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.sms_marketing import SmsMarketingCampaignStatus as SmsMarketingCampaignGateStatus
from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
    SmsMarketingTriggerSource,
)


class SmsMarketingCampaignStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    sms_delivery_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: SmsMarketingCampaignGateStatus
    ) -> "SmsMarketingCampaignStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            sms_delivery_ready=status.sms_delivery_ready,
            blockers=list(status.blockers),
        )


class SmsMarketingCampaignRunRequest(BaseSchema):
    campaign_name: str = Field(min_length=1, max_length=120)
    message_body: str = Field(min_length=1, max_length=1600)
    recipient_user_ids: list[uuid.UUID] = Field(min_length=1, max_length=100)


class SmsMarketingCampaignRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    campaign_name: str
    message_body: str
    recipient_user_ids: list[str]
    trigger_source: SmsMarketingTriggerSource
    status: SmsMarketingCampaignStatus
    recipients_queued: int
    messages_sent: int
    messages_failed: int
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: SmsMarketingCampaignRun) -> "SmsMarketingCampaignRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            campaign_name=run.campaign_name,
            message_body=run.message_body,
            recipient_user_ids=run.recipient_user_ids,
            trigger_source=run.trigger_source,
            status=run.status,
            recipients_queued=run.recipients_queued,
            messages_sent=run.messages_sent,
            messages_failed=run.messages_failed,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class SmsMarketingCampaignRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SmsMarketingCampaignRunResultResponse(BaseSchema):
    completed_at: datetime
    run: SmsMarketingCampaignRunResponse
