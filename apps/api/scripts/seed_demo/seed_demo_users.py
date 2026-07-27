"""Seed demo staff users into the verdin-demo organization.

Usage: python -m scripts.seed_demo.seed_demo_users
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

import api.models  # noqa: F401
from api.core.config import get_settings
from api.core.constants import UserRole
from api.core.security import hash_password
from api.database.session import AsyncSessionLocal
from api.modules.auth.models import Organization, OrganizationType, User
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature
from scripts.seed_demo.seed_demo_org import seed_demo_org

_DEMO_USERS = (
    ("owner@verdin.demo", "Demo", "Owner", UserRole.OWNER),
    ("admin@verdin.demo", "Demo", "Admin", UserRole.ADMIN),
    ("manager@verdin.demo", "Demo", "Manager", UserRole.CASE_MANAGER),
)


async def seed_demo_users() -> list[uuid.UUID]:
    settings = get_settings()
    if settings.app_env == "production":
        raise RuntimeError("seed_demo_users refuses to run when APP_ENV=production")

    org_id = await seed_demo_org()
    created: list[uuid.UUID] = []

    async with AsyncSessionLocal() as session:
        org = await session.get(Organization, org_id)
        assert org is not None
        assert org.organization_type == OrganizationType.DEMO

        flag = await session.execute(
            select(OrganizationFeatureFlag).where(
                OrganizationFeatureFlag.organization_id == org_id,
                OrganizationFeatureFlag.feature == OrgDemoFeature.DEMO_DATA,
                OrganizationFeatureFlag.enabled.is_(True),
            )
        )
        if flag.scalar_one_or_none() is None:
            raise RuntimeError("Demo org missing demo_data feature flag")

        for email, first, last, role in _DEMO_USERS:
            existing = await session.execute(select(User).where(User.email == email))
            user = existing.scalar_one_or_none()
            if user is not None:
                print(f"User already exists: {email}")
                continue
            user = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=hash_password("changeme123"),
                first_name=first,
                last_name=last,
                role=role,
                organization_id=org_id,
                is_active=True,
            )
            session.add(user)
            created.append(user.id)
            print(f"Created {email}")

        await session.commit()
    return created


def main() -> None:
    ids = asyncio.run(seed_demo_users())
    print(f"Created {len(ids)} demo users")


if __name__ == "__main__":
    main()
