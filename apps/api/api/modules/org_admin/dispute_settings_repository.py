"""Repository for per-organization dispute settings."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.dispute_settings_models import OrganizationDisputeSettings


class OrganizationDisputeSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_organization(
        self, organization_id: uuid.UUID
    ) -> OrganizationDisputeSettings | None:
        result = await self._session.execute(
            select(OrganizationDisputeSettings).where(
                OrganizationDisputeSettings.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def save(self, settings: OrganizationDisputeSettings) -> OrganizationDisputeSettings:
        self._session.add(settings)
        await self._session.flush()
        await self._session.refresh(settings)
        return settings
