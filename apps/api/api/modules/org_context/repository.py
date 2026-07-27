"""Organization context persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.models import Organization
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature


class OrgContextRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_organization(self, organization_id: uuid.UUID) -> Organization | None:
        result = await self._session.execute(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_feature_flags(self, organization_id: uuid.UUID) -> list[OrganizationFeatureFlag]:
        result = await self._session.execute(
            select(OrganizationFeatureFlag).where(
                OrganizationFeatureFlag.organization_id == organization_id,
                OrganizationFeatureFlag.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_feature_flag(
        self, organization_id: uuid.UUID, feature: OrgDemoFeature
    ) -> OrganizationFeatureFlag | None:
        result = await self._session.execute(
            select(OrganizationFeatureFlag).where(
                OrganizationFeatureFlag.organization_id == organization_id,
                OrganizationFeatureFlag.feature == feature,
                OrganizationFeatureFlag.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def upsert_feature_flag(self, row: OrganizationFeatureFlag) -> OrganizationFeatureFlag:
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def save_feature_flag(self, row: OrganizationFeatureFlag) -> OrganizationFeatureFlag:
        await self._session.flush()
        await self._session.refresh(row)
        return row
