"""Client portal repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.client_portal.models import ClientPortalUser


class ClientPortalUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        portal_user_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> ClientPortalUser | None:
        uid = uuid.UUID(str(portal_user_id))
        query = select(ClientPortalUser).where(
            ClientPortalUser.id == uid,
            ClientPortalUser.deleted_at.is_(None),
        )
        if organization_id is not None:
            query = query.where(ClientPortalUser.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> ClientPortalUser | None:
        result = await self._session.execute(
            select(ClientPortalUser).where(
                ClientPortalUser.email == email,
                ClientPortalUser.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_client_id(
        self,
        client_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> ClientPortalUser | None:
        result = await self._session.execute(
            select(ClientPortalUser).where(
                ClientPortalUser.client_id == client_id,
                ClientPortalUser.organization_id == organization_id,
                ClientPortalUser.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def add(self, portal_user: ClientPortalUser) -> ClientPortalUser:
        self._session.add(portal_user)
        await self._session.flush()
        return portal_user

    async def save(self, portal_user: ClientPortalUser) -> ClientPortalUser:
        await self._session.flush()
        return portal_user
