"""Organization billing repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.models import (
    BillingUsageEvent,
    BillingWebhookEvent,
    OrganizationBillingAccount,
)


class BillingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_billing_account(
        self,
        organization_id: uuid.UUID,
    ) -> OrganizationBillingAccount | None:
        return await self._session.get(OrganizationBillingAccount, organization_id)

    async def get_billing_account_by_customer_id(
        self,
        stripe_customer_id: str,
    ) -> OrganizationBillingAccount | None:
        result = await self._session.execute(
            select(OrganizationBillingAccount).where(
                OrganizationBillingAccount.stripe_customer_id == stripe_customer_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_billing_account(
        self,
        account: OrganizationBillingAccount,
    ) -> OrganizationBillingAccount:
        self._session.add(account)
        await self._session.flush()
        await self._session.refresh(account)
        return account

    async def delete_billing_account(self, organization_id: uuid.UUID) -> bool:
        account = await self.get_billing_account(organization_id)
        if account is None:
            return False
        await self._session.delete(account)
        await self._session.flush()
        return True

    async def get_webhook_event(self, stripe_event_id: str) -> BillingWebhookEvent | None:
        result = await self._session.execute(
            select(BillingWebhookEvent).where(
                BillingWebhookEvent.stripe_event_id == stripe_event_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_webhook_event(self, event: BillingWebhookEvent) -> BillingWebhookEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(UTC)

    async def create_usage_event(self, event: BillingUsageEvent) -> BillingUsageEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def aggregate_usage_by_metric(
        self,
        organization_id: uuid.UUID,
    ) -> tuple[int, list[dict[str, int | str]], datetime | None, datetime | None]:
        metrics_result = await self._session.execute(
            select(
                BillingUsageEvent.metric_name,
                func.sum(BillingUsageEvent.quantity).label("total_quantity"),
            )
            .where(BillingUsageEvent.organization_id == organization_id)
            .group_by(BillingUsageEvent.metric_name)
            .order_by(BillingUsageEvent.metric_name),
        )
        metrics = [
            {"metric_name": row.metric_name, "total_quantity": int(row.total_quantity)}
            for row in metrics_result.all()
        ]

        bounds_result = await self._session.execute(
            select(
                func.count(BillingUsageEvent.id),
                func.min(BillingUsageEvent.recorded_at),
                func.max(BillingUsageEvent.recorded_at),
            ).where(BillingUsageEvent.organization_id == organization_id),
        )
        total_events, first_recorded_at, last_recorded_at = bounds_result.one()
        return int(total_events), metrics, first_recorded_at, last_recorded_at
