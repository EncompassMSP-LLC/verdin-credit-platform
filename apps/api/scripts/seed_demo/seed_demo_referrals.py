"""Seed demo mortgage-partner referrals when partnerships exist.

Usage: python -m scripts.seed_demo.seed_demo_referrals

Does nothing (and exits 0) when no partnership exists — never creates production data.
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

import api.models  # noqa: F401
from api.core.audit import apply_audit_on_create
from api.core.config import get_settings
from api.database.session import AsyncSessionLocal
from api.modules.auth.models import Organization, OrganizationType, User
from api.modules.clients.models import Client
from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    OrgPartnership,
    PartnerReferral,
    ReferralStatus,
)
from scripts.seed_demo.seed_demo_borrowers import seed_demo_borrowers
from scripts.seed_demo.seed_demo_org import DEMO_SLUG, seed_demo_org


async def seed_demo_referrals() -> list[uuid.UUID]:
    settings = get_settings()
    if settings.app_env == "production":
        raise RuntimeError("seed_demo_referrals refuses to run when APP_ENV=production")

    org_id = await seed_demo_org()
    await seed_demo_borrowers()
    created: list[uuid.UUID] = []

    async with AsyncSessionLocal() as session:
        org = await session.get(Organization, org_id)
        assert org is not None and org.organization_type == OrganizationType.DEMO

        partnership_result = await session.execute(
            select(OrgPartnership).where(
                OrgPartnership.cro_organization_id == org_id,
                OrgPartnership.deleted_at.is_(None),
            )
        )
        partnership = partnership_result.scalars().first()
        if partnership is None:
            print(f"No partnership on {DEMO_SLUG}; skipping referral seed")
            return []

        clients = await session.execute(
            select(Client).where(
                Client.organization_id == org_id,
                Client.deleted_at.is_(None),
            )
        )
        client_rows = list(clients.scalars().all())
        if not client_rows:
            print("No demo borrowers; skipping referral seed")
            return []

        owner = await session.execute(select(User).where(User.email == "owner@verdin.demo"))
        actor = owner.scalar_one_or_none()

        for client in client_rows[:3]:
            existing = await session.execute(
                select(PartnerReferral).where(
                    PartnerReferral.partnership_id == partnership.id,
                    PartnerReferral.client_id == client.id,
                    PartnerReferral.deleted_at.is_(None),
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            referral = PartnerReferral(
                id=uuid.uuid4(),
                cro_organization_id=org_id,
                partnership_id=partnership.id,
                client_id=client.id,
                status=ReferralStatus.NEW,
                pipeline_stage=LoanPipelineStage.REFERRED,
            )
            if actor:
                apply_audit_on_create(referral, actor.id)
            session.add(referral)
            created.append(referral.id)
            print(f"Created referral for {client.display_name}")

        await session.commit()
    return created


def main() -> None:
    ids = asyncio.run(seed_demo_referrals())
    print(f"Created {len(ids)} demo referrals")


if __name__ == "__main__":
    main()
