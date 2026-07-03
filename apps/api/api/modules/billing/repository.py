"""Organization billing repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.billing.models import BillingWebhookEvent, OrganizationBillingAccount


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
