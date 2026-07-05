"""Pydantic schemas for SMS deliverability dashboard scaffold."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.sms_deliverability_dashboard import SmsDeliverabilityDashboardStatus
from api.modules.notifications.sms_campaign_models import (
    SmsMarketingCampaignRun,
    SmsMarketingCampaignStatus,
    SmsMarketingTriggerSource,
)


class SmsDeliverabilityDashboardStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    delivery_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls,
        status: SmsDeliverabilityDashboardStatus,
    ) -> "SmsDeliverabilityDashboardStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            delivery_ready=status.delivery_ready,
            blockers=list(status.blockers),
        )


class SmsDeliverabilityCampaignOutcome(BaseSchema):
    id: UUID
    campaign_name: str
    status: SmsMarketingCampaignStatus
    trigger_source: SmsMarketingTriggerSource
    recipients_queued: int
    messages_sent: int
    messages_failed: int
    started_at: datetime | None
    completed_at: datetime | None

    @classmethod
    def from_model(cls, run: SmsMarketingCampaignRun) -> "SmsDeliverabilityCampaignOutcome":
        return cls(
            id=run.id,
            campaign_name=run.campaign_name,
            status=run.status,
            trigger_source=run.trigger_source,
            recipients_queued=run.recipients_queued,
            messages_sent=run.messages_sent,
            messages_failed=run.messages_failed,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )


class SmsDeliverabilityMetricsResponse(BaseSchema):
    total_campaign_runs: int
    completed_campaign_runs: int
    failed_campaign_runs: int
    pending_campaign_runs: int
    delivery_logs_sent: int
    delivery_logs_failed: int
    delivery_success_rate: float | None
    recent_campaign_outcomes: list[SmsDeliverabilityCampaignOutcome] = Field(default_factory=list)
