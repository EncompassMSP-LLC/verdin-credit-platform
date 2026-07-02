"""Organization admin repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.models import Organization, User
from api.modules.org_admin.models import OrganizationApiKey


class OrgAdminRepository:
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

    async def count_active_users(self, organization_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.organization_id == organization_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def count_active_api_keys(self, organization_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(OrganizationApiKey)
            .where(
                OrganizationApiKey.organization_id == organization_id,
                OrganizationApiKey.is_active.is_(True),
                OrganizationApiKey.revoked_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def list_api_keys(self, organization_id: uuid.UUID) -> list[OrganizationApiKey]:
        result = await self._session.execute(
            select(OrganizationApiKey)
            .where(OrganizationApiKey.organization_id == organization_id)
            .order_by(OrganizationApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_api_key(
        self,
        api_key_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> OrganizationApiKey | None:
        result = await self._session.execute(
            select(OrganizationApiKey).where(
                OrganizationApiKey.id == api_key_id,
                OrganizationApiKey.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_api_key(self, api_key: OrganizationApiKey) -> OrganizationApiKey:
        self._session.add(api_key)
        await self._session.flush()
        await self._session.refresh(api_key)
        return api_key

    async def save_api_key(self, api_key: OrganizationApiKey) -> OrganizationApiKey:
        await self._session.flush()
        await self._session.refresh(api_key)
        return api_key

    async def list_active_api_keys_by_prefix(self, key_prefix: str) -> list[OrganizationApiKey]:
        result = await self._session.execute(
            select(OrganizationApiKey).where(
                OrganizationApiKey.key_prefix == key_prefix,
                OrganizationApiKey.is_active.is_(True),
                OrganizationApiKey.revoked_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def touch_api_key_last_used(self, api_key_id: uuid.UUID) -> None:
        api_key = await self._session.get(OrganizationApiKey, api_key_id)
        if api_key is None:
            return
        api_key.last_used_at = datetime.now(UTC)
        await self._session.flush()
