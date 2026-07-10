"""Ensure demo org has a pilot billing account for revenue reporting."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

import api.models  # noqa: F401 — register all ORM mappers
from api.database.session import AsyncSessionLocal
from api.modules.auth.models import Organization
from api.modules.billing.models import OrganizationBillingAccount, SubscriptionStatus


async def ensure_demo_billing() -> None:
    async with AsyncSessionLocal() as session:
        org_result = await session.execute(
            select(Organization).where(Organization.slug == "verdin-demo")
        )
        org = org_result.scalar_one_or_none()
        if org is None:
            print("Demo organization not found — run seed first.")
            return

        existing = await session.get(OrganizationBillingAccount, org.id)
        if existing is not None:
            print("Demo billing account already exists.")
            return

        session.add(
            OrganizationBillingAccount(
                organization_id=org.id,
                stripe_customer_id=f"cus_pilot_{uuid.uuid4().hex[:12]}",
                stripe_subscription_id=f"sub_pilot_{uuid.uuid4().hex[:12]}",
                subscription_status=SubscriptionStatus.ACTIVE,
                price_id="price_pilot_demo_monthly",
                current_period_end=datetime.now(UTC) + timedelta(days=25),
            )
        )
        await session.commit()
        print("Demo billing account created for verdin-demo.")


if __name__ == "__main__":
    asyncio.run(ensure_demo_billing())
