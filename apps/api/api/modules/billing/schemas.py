"""Billing Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.billing.models import OrganizationBillingAccount, SubscriptionStatus


class BillingStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    provider: str
    default_price_id: str | None
    blockers: list[str]


class OrganizationBillingSummary(BaseSchema):
    enabled: bool
    ready: bool
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.NONE
    price_id: str | None = None
    current_period_end: datetime | None = None

    @classmethod
    def from_account(
        cls,
        *,
        enabled: bool,
        ready: bool,
        account: OrganizationBillingAccount | None,
    ) -> "OrganizationBillingSummary":
        if account is None:
            return cls(enabled=enabled, ready=ready)
        return cls(
            enabled=enabled,
            ready=ready,
            stripe_customer_id=account.stripe_customer_id,
            stripe_subscription_id=account.stripe_subscription_id,
            subscription_status=account.subscription_status,
            price_id=account.price_id,
            current_period_end=account.current_period_end,
        )


class BillingSetupResponse(BaseSchema):
    organization_id: uuid.UUID
    stripe_customer_id: str
    created: bool


class BillingDisconnectResponse(BaseSchema):
    organization_id: uuid.UUID
    disconnected: bool


class BillingSubscribeRequest(BaseSchema):
    price_id: str | None = Field(default=None, max_length=255)


class BillingSubscribeResponse(BaseSchema):
    organization_id: uuid.UUID
    stripe_customer_id: str
    stripe_subscription_id: str
    subscription_status: SubscriptionStatus
    price_id: str | None
    current_period_end: datetime | None


class StripeWebhookResponse(BaseSchema):
    received: bool
    event_id: str
    status: str


class BillingUsageMetricTotal(BaseSchema):
    metric_name: str
    total_quantity: int


class BillingUsageRecordRequest(BaseSchema):
    metric_name: str = Field(min_length=1, max_length=64)
    quantity: int = Field(default=1, ge=1, le=1_000_000)
    source: str = Field(default="manual", min_length=1, max_length=64)


class BillingUsageRecordResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    metric_name: str
    quantity: int
    source: str
    recorded_at: datetime


class BillingUsageSummaryResponse(BaseSchema):
    organization_id: uuid.UUID
    metering_enabled: bool
    stripe_customer_configured: bool
    total_events: int
    metrics: list[BillingUsageMetricTotal]
    first_recorded_at: datetime | None
    last_recorded_at: datetime | None
