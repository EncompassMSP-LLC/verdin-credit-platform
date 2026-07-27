"""Seed sample borrowers into the verdin-demo organization.

Usage: python -m scripts.seed_demo.seed_demo_borrowers
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
from api.modules.clients.models import Client, ClientStatus
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature
from scripts.seed_demo.seed_demo_org import DEMO_SLUG, seed_demo_org

_SAMPLE_BORROWERS = (
    ("Alex Rivera", "alex.rivera@demo.local", "555-0101"),
    ("Jordan Lee", "jordan.lee@demo.local", "555-0102"),
    ("Sam Patel", "sam.patel@demo.local", "555-0103"),
)


async def seed_demo_borrowers() -> list[uuid.UUID]:
    settings = get_settings()
    if settings.app_env == "production":
        raise RuntimeError("seed_demo_borrowers refuses to run when APP_ENV=production")
    if not settings.enable_sample_data:
        raise RuntimeError("seed_demo_borrowers requires ENABLE_SAMPLE_DATA=true")

    org_id = await seed_demo_org()
    created: list[uuid.UUID] = []

    async with AsyncSessionLocal() as session:
        org = await session.get(Organization, org_id)
        assert org is not None and org.organization_type == OrganizationType.DEMO

        flag = await session.execute(
            select(OrganizationFeatureFlag).where(
                OrganizationFeatureFlag.organization_id == org_id,
                OrganizationFeatureFlag.feature == OrgDemoFeature.SAMPLE_BORROWERS,
                OrganizationFeatureFlag.enabled.is_(True),
            )
        )
        if flag.scalar_one_or_none() is None:
            raise RuntimeError("Demo org missing sample_borrowers feature flag")

        owner = await session.execute(
            select(User).where(
                User.organization_id == org_id,
                User.email == "owner@verdin.demo",
            )
        )
        actor = owner.scalar_one_or_none()
        actor_id = actor.id if actor else None

        for name, email, phone in _SAMPLE_BORROWERS:
            existing = await session.execute(
                select(Client).where(
                    Client.organization_id == org_id,
                    Client.email == email,
                    Client.deleted_at.is_(None),
                )
            )
            if existing.scalar_one_or_none() is not None:
                print(f"Borrower already exists: {email}")
                continue
            client = Client(
                id=uuid.uuid4(),
                organization_id=org_id,
                display_name=name,
                email=email,
                phone=phone,
                status=ClientStatus.ACTIVE,
                notes=f"Seeded by seed_demo_borrowers for {DEMO_SLUG}",
            )
            if actor_id:
                apply_audit_on_create(client, actor_id)
            session.add(client)
            created.append(client.id)
            print(f"Created borrower {name}")

        await session.commit()
    return created


def main() -> None:
    ids = asyncio.run(seed_demo_borrowers())
    print(f"Created {len(ids)} demo borrowers")


if __name__ == "__main__":
    main()
