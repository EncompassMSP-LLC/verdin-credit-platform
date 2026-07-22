"""Client repository — owns Client and ClientContact database access."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.accounts.dispute_letter_models import DisputeLetter
from api.modules.accounts.dispute_response_models import DisputeResponse
from api.modules.accounts.models import Account
from api.modules.cases.models import Case
from api.modules.client_portal.models import ClientPortalUser
from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship
from api.modules.clients.schemas import (
    ClientSortField,
    ClientSortOrder,
    ContactSortField,
    ContactSortOrder,
)
from api.modules.documents.models import Document
from api.modules.tasks.models import Task
from api.modules.timeline.models import Communication


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

    async def cascade_soft_delete_related(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        updated_by_id: uuid.UUID | None,
    ) -> None:
        """Soft-delete cases, accounts, and related history for a client.

        Timeline events remain append-only (not soft-deleted).
        """
        now = datetime.now(UTC)
        audited: dict[str, datetime | uuid.UUID] = {
            "deleted_at": now,
            "updated_at": now,
        }
        if updated_by_id is not None:
            audited["updated_by_id"] = updated_by_id
        plain: dict[str, datetime] = {"deleted_at": now, "updated_at": now}

        case_ids = list(
            (
                await self._session.execute(
                    select(Case.id).where(
                        Case.organization_id == organization_id,
                        Case.client_id == client_id,
                        Case.deleted_at.is_(None),
                    )
                )
            ).scalars()
        )

        if case_ids:
            await self._session.execute(
                update(Account)
                .where(
                    Account.organization_id == organization_id,
                    Account.case_id.in_(case_ids),
                    Account.deleted_at.is_(None),
                )
                .values(**audited)
            )
            await self._session.execute(
                update(DisputeLetter)
                .where(
                    DisputeLetter.organization_id == organization_id,
                    DisputeLetter.case_id.in_(case_ids),
                    DisputeLetter.deleted_at.is_(None),
                )
                .values(**audited)
            )
            await self._session.execute(
                update(DisputeResponse)
                .where(
                    DisputeResponse.organization_id == organization_id,
                    DisputeResponse.case_id.in_(case_ids),
                    DisputeResponse.deleted_at.is_(None),
                )
                .values(**audited)
            )
            await self._session.execute(
                update(Document)
                .where(
                    Document.organization_id == organization_id,
                    Document.case_id.in_(case_ids),
                    Document.deleted_at.is_(None),
                )
                .values(**audited)
            )
            await self._session.execute(
                update(Communication)
                .where(
                    Communication.case_id.in_(case_ids),
                    Communication.deleted_at.is_(None),
                )
                .values(**plain)
            )
            await self._session.execute(
                update(Task)
                .where(
                    Task.organization_id == organization_id,
                    Task.case_id.in_(case_ids),
                    Task.deleted_at.is_(None),
                )
                .values(**audited)
            )
            await self._session.execute(
                update(Case)
                .where(
                    Case.organization_id == organization_id,
                    Case.id.in_(case_ids),
                    Case.deleted_at.is_(None),
                )
                .values(**audited)
            )

        await self._session.execute(
            update(ClientContact)
            .where(
                ClientContact.organization_id == organization_id,
                ClientContact.client_id == client_id,
                ClientContact.deleted_at.is_(None),
            )
            .values(**audited)
        )
        await self._session.execute(
            update(ClientPortalUser)
            .where(
                ClientPortalUser.organization_id == organization_id,
                ClientPortalUser.client_id == client_id,
                ClientPortalUser.deleted_at.is_(None),
            )
            .values(**audited)
        )
