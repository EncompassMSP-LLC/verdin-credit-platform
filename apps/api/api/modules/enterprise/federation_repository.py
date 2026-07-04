"""Repository for IdP federation provider registry."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.federation_models import IdpFederationProvider


class IdpFederationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key(
        self,
        organization_id: uuid.UUID,
        provider_key: str,
    ) -> IdpFederationProvider | None:
        result = await self._session.execute(
            select(IdpFederationProvider).where(
                IdpFederationProvider.organization_id == organization_id,
                IdpFederationProvider.provider_key == provider_key,
            )
        )
        return result.scalar_one_or_none()

    async def list_providers(
        self,
        organization_id: uuid.UUID,
    ) -> list[IdpFederationProvider]:
        result = await self._session.execute(
            select(IdpFederationProvider)
            .where(IdpFederationProvider.organization_id == organization_id)
            .order_by(
                IdpFederationProvider.is_primary.desc(),
                IdpFederationProvider.display_name.asc(),
            )
        )
        return list(result.scalars().all())

    async def count_providers(self, organization_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(IdpFederationProvider).where(
                IdpFederationProvider.organization_id == organization_id,
            )
        )
        return len(list(result.scalars().all()))

    async def clear_primary(self, organization_id: uuid.UUID) -> None:
        await self._session.execute(
            update(IdpFederationProvider)
            .where(IdpFederationProvider.organization_id == organization_id)
            .values(is_primary=False)
        )

    async def save_provider(self, provider: IdpFederationProvider) -> IdpFederationProvider:
        self._session.add(provider)
        await self._session.flush()
        await self._session.refresh(provider)
        return provider
