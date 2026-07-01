"""Client management service — business logic for clients and contacts."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.clients.models import Client, ClientContact
from api.modules.clients.permissions import CLIENT_DELETE_ROLE, CLIENT_WRITE_ROLE
from api.modules.clients.repository import (
    ClientContactListFilters,
    ClientListFilters,
    ClientRepository,
)
from api.modules.clients.schemas import (
    ClientContactCreate,
    ClientContactListParams,
    ClientContactResponse,
    ClientContactUpdate,
    ClientCreate,
    ClientListParams,
    ClientResponse,
    ClientUpdate,
)


class ClientService:
    def __init__(self, client_repo: ClientRepository, session: AsyncSession | None = None) -> None:
        self._clients = client_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientService":
        return cls(ClientRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify clients",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete clients",
            )

    async def _get_client_for_user(self, client_id: uuid.UUID, user: User) -> Client:
        organization_id = self._require_organization(user)
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    async def create_client(self, user: User, data: ClientCreate) -> ClientResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)

        client = Client(
            organization_id=organization_id,
            display_name=data.display_name,
            email=str(data.email) if data.email else None,
            phone=data.phone,
            status=data.status,
            notes=data.notes,
        )
        apply_audit_on_create(client, user.id)
        await self._clients.add(client)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(client)
        return ClientResponse.from_model(client)

    async def list_clients(
        self, user: User, params: ClientListParams
    ) -> PaginatedResponse[ClientResponse]:
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        items, total = await self._clients.list_clients(
            ClientListFilters(
                organization_id=organization_id,
                search=params.search,
                status=params.status,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        return paginate(
            [ClientResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_client(self, user: User, client_id: uuid.UUID) -> ClientResponse:
        client = await self._get_client_for_user(client_id, user)
        return ClientResponse.from_model(client)

    async def update_client(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientUpdate,
    ) -> ClientResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        updates = data.model_dump(exclude_unset=True)
        if "email" in updates:
            updates["email"] = str(updates["email"]) if updates["email"] is not None else None
        for key, value in updates.items():
            setattr(client, key, value)
        apply_audit_on_update(client, user.id)
        await self._clients.save(client)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(client)
        return ClientResponse.from_model(client)

    async def delete_client(self, user: User, client_id: uuid.UUID) -> None:
        self._require_delete(user)
        client = await self._get_client_for_user(client_id, user)
        client.soft_delete()
        apply_audit_on_update(client, user.id)
        await self._clients.save(client)
        if self._session is not None:
            await self._session.commit()

    async def create_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientContactCreate,
    ) -> ClientContactResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        if data.is_primary:
            await self._clients.clear_primary_contacts(
                organization_id=client.organization_id,
                client_id=client.id,
            )

        contact = ClientContact(
            organization_id=client.organization_id,
            client_id=client.id,
            full_name=data.full_name,
            email=str(data.email) if data.email else None,
            phone=data.phone,
            relationship_type=data.relationship_type,
            is_primary=data.is_primary,
            notes=data.notes,
        )
        apply_audit_on_create(contact, user.id)
        await self._clients.add_contact(contact)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(contact)
        return ClientContactResponse.from_model(contact)

    async def list_contacts(
        self,
        user: User,
        client_id: uuid.UUID,
        params: ClientContactListParams,
    ) -> PaginatedResponse[ClientContactResponse]:
        client = await self._get_client_for_user(client_id, user)
        skip = (params.page - 1) * params.page_size
        items, total = await self._clients.list_contacts(
            ClientContactListFilters(
                organization_id=client.organization_id,
                client_id=client.id,
                search=params.search,
                relationship_type=params.relationship_type,
                is_primary=params.is_primary,
                skip=skip,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        return paginate(
            [ClientContactResponse.from_model(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> ClientContactResponse:
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return ClientContactResponse.from_model(contact)

    async def update_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
        data: ClientContactUpdate,
    ) -> ClientContactResponse:
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

        updates = data.model_dump(exclude_unset=True)
        if updates.get("is_primary"):
            await self._clients.clear_primary_contacts(
                organization_id=client.organization_id,
                client_id=client.id,
                except_contact_id=contact.id,
            )
        if "email" in updates:
            updates["email"] = str(updates["email"]) if updates["email"] is not None else None
        for key, value in updates.items():
            setattr(contact, key, value)
        apply_audit_on_update(contact, user.id)
        await self._clients.save_contact(contact)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(contact)
        return ClientContactResponse.from_model(contact)

    async def delete_contact(
        self,
        user: User,
        client_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> None:
        self._require_delete(user)
        client = await self._get_client_for_user(client_id, user)
        contact = await self._clients.get_contact_by_id(
            contact_id,
            organization_id=client.organization_id,
            client_id=client.id,
        )
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        contact.soft_delete()
        apply_audit_on_update(contact, user.id)
        await self._clients.save_contact(contact)
        if self._session is not None:
            await self._session.commit()
