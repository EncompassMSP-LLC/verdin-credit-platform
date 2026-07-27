"""Create or upgrade the verdin-demo organization (DEMO type + feature flags).

Usage (dev/sales only):
  python -m scripts.seed_demo.seed_demo_org

Production deployments must never run this module.
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

import api.models  # noqa: F401
from api.core.config import get_settings
from api.database.session import AsyncSessionLocal
from api.modules.auth.models import Organization, OrganizationType
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature

DEMO_SLUG = "verdin-demo"
DEMO_NAME = "Ultimate Credit Repair LLC (Demo)"

_DEMO_FEATURES = (
    OrgDemoFeature.DEMO_DATA,
    OrgDemoFeature.DEMO_NOTIFICATIONS,
    OrgDemoFeature.SAMPLE_BORROWERS,
    OrgDemoFeature.TRAINING_MODE,
)


async def seed_demo_org() -> uuid.UUID:
    settings = get_settings()
    if settings.app_env == "production":
        raise RuntimeError("seed_demo_org refuses to run when APP_ENV=production")
    if not settings.allow_demo_orgs:
        raise RuntimeError("seed_demo_org requires ALLOW_DEMO_ORGS=true")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Organization).where(Organization.slug == DEMO_SLUG))
        org = result.scalar_one_or_none()
        if org is None:
            org = Organization(
                id=uuid.uuid4(),
                name=DEMO_NAME,
                slug=DEMO_SLUG,
                is_active=True,
                organization_type=OrganizationType.DEMO,
            )
            session.add(org)
            await session.flush()
            print(f"Created demo organization {org.id}")
        else:
            org.organization_type = OrganizationType.DEMO
            org.is_active = True
            print(f"Upgraded existing organization {org.id} to DEMO")

        for feature in _DEMO_FEATURES:
            existing = await session.execute(
                select(OrganizationFeatureFlag).where(
                    OrganizationFeatureFlag.organization_id == org.id,
                    OrganizationFeatureFlag.feature == feature,
                    OrganizationFeatureFlag.deleted_at.is_(None),
                )
            )
            row = existing.scalar_one_or_none()
            if row is None:
                session.add(
                    OrganizationFeatureFlag(
                        id=uuid.uuid4(),
                        organization_id=org.id,
                        feature=feature,
                        enabled=True,
                    )
                )
            else:
                row.enabled = True

        await session.commit()
        return org.id


def main() -> None:
    org_id = asyncio.run(seed_demo_org())
    print(f"Demo org ready: {org_id}")


if __name__ == "__main__":
    main()
