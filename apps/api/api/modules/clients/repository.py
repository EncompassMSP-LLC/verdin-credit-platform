"""Client repository — owns Client and ClientContact database access."""

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship
from api.modules.clients.schemas import (
    ClientSortField,
    ClientSortOrder,
    ContactSortField,
    ContactSortOrder,
)


@dataclass(frozen=True, slots=True)
class ClientListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    status: ClientStatus | None = None
    skip: int = 0
    limit: int = 20
    sort_by: ClientSortField = "created_at"
    sort_order: ClientSortOrder = "desc"


@dataclass(frozen=True, slots=True)
class ClientContactListFilters:
    organization_id: uuid.UUID
    client_id: uuid.UUID
    search: str | None = None
    relationship_type: ContactRelationship | None = None
    is_primary: bool | None = None
    skip: int = 0
    limit: int = 20
    sort_by: ContactSortField = "created_at"
    sort_order: ContactSortOrder = "desc"


_CLIENT_SORT_COLUMNS: dict[ClientSortField, InstrumentedAttribute[Any]] = {
    "created_at": Client.created_at,
    "updated_at": Client.updated_at,
    "display_name": Client.display_name,
    "status": Client.status,
}

_CONTACT_SORT_COLUMNS: dict[ContactSortField, InstrumentedAttribute[Any]] = {
    "created_at": ClientContact.created_at,
    "updated_at": ClientContact.updated_at,
    "full_name": ClientContact.full_name,
    "relationship": ClientContact.relationship_type,
}


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        client_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Client | None:
        uid = uuid.UUID(str(client_id))
        query = select(Client).where(Client.id == uid, Client.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Client.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_clients(self, filters: ClientListFilters) -> tuple[list[Client], int]:
        base = select(Client).where(
            Client.organization_id == filters.organization_id,
            Client.deleted_at.is_(None),
        )
        if filters.status is not None:
            base = base.where(Client.status == filters.status)
        if filters.search:
            term = f"%{filters.search.strip()}%"
            base = base.where(
                or_(
                    Client.display_name.ilike(term),
                    Client.email.ilike(term),
                    Client.phone.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _CLIENT_SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        query = base.order_by(order).offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def add(self, client: Client) -> Client:
        self._session.add(client)
        await self._session.flush()
        return client

    async def save(self, client: Client) -> Client:
        await self._session.flush()
        return client

    async def get_contact_by_id(
        self,
        contact_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> ClientContact | None:
        uid = uuid.UUID(str(contact_id))
        result = await self._session.execute(
            select(ClientContact).where(
                ClientContact.id == uid,
                ClientContact.organization_id == organization_id,
                ClientContact.client_id == client_id,
                ClientContact.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_contacts(
        self, filters: ClientContactListFilters
    ) -> tuple[list[ClientContact], int]:
        base = select(ClientContact).where(
            ClientContact.organization_id == filters.organization_id,
            ClientContact.client_id == filters.client_id,
            ClientContact.deleted_at.is_(None),
        )
        if filters.relationship_type is not None:
            base = base.where(ClientContact.relationship_type == filters.relationship_type)
        if filters.is_primary is not None:
            base = base.where(ClientContact.is_primary == filters.is_primary)
        if filters.search:
            term = f"%{filters.search.strip()}%"
            base = base.where(
                or_(
                    ClientContact.full_name.ilike(term),
                    ClientContact.email.ilike(term),
                    ClientContact.phone.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _CONTACT_SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        query = base.order_by(order).offset(filters.skip).limit(filters.limit)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def add_contact(self, contact: ClientContact) -> ClientContact:
        self._session.add(contact)
        await self._session.flush()
        return contact

    async def save_contact(self, contact: ClientContact) -> ClientContact:
        await self._session.flush()
        return contact

    async def clear_primary_contacts(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        except_contact_id: uuid.UUID | None = None,
    ) -> None:
        query = (
            update(ClientContact)
            .where(
                ClientContact.organization_id == organization_id,
                ClientContact.client_id == client_id,
                ClientContact.is_primary.is_(True),
                ClientContact.deleted_at.is_(None),
            )
            .values(is_primary=False)
        )
        if except_contact_id is not None:
            query = query.where(ClientContact.id != except_contact_id)
        await self._session.execute(query)
