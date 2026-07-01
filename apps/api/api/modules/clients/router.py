"""Client management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.clients.models import ClientStatus, ContactRelationship
from api.modules.clients.schemas import (
    ClientContactCreate,
    ClientContactListParams,
    ClientContactResponse,
    ClientContactUpdate,
    ClientCreate,
    ClientListParams,
    ClientResponse,
    ClientSortField,
    ClientSortOrder,
    ClientUpdate,
    ContactSortField,
    ContactSortOrder,
)
from api.modules.clients.service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService.from_session(db)


def get_client_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    status: ClientStatus | None = None,
    sort_by: ClientSortField = "created_at",
    sort_order: ClientSortOrder = "desc",
) -> ClientListParams:
    return ClientListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def get_contact_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    relationship_type: ContactRelationship | None = None,
    is_primary: bool | None = None,
    sort_by: ContactSortField = "created_at",
    sort_order: ContactSortOrder = "desc",
) -> ClientContactListParams:
    return ClientContactListParams(
        page=page,
        page_size=page_size,
        search=search,
        relationship_type=relationship_type,
        is_primary=is_primary,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    body: ClientCreate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    return await service.create_client(current_user, body)


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    params: ClientListParams = Depends(get_client_list_params),
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> PaginatedResponse[ClientResponse]:
    return await service.list_clients(current_user, params)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    return await service.get_client(current_user, client_id)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    body: ClientUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    return await service.update_client(current_user, client_id, body)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> None:
    await service.delete_client(current_user, client_id)


@router.post(
    "/{client_id}/contacts",
    response_model=ClientContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_client_contact(
    client_id: uuid.UUID,
    body: ClientContactCreate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientContactResponse:
    return await service.create_contact(current_user, client_id, body)


@router.get("/{client_id}/contacts", response_model=PaginatedResponse[ClientContactResponse])
async def list_client_contacts(
    client_id: uuid.UUID,
    params: ClientContactListParams = Depends(get_contact_list_params),
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> PaginatedResponse[ClientContactResponse]:
    return await service.list_contacts(current_user, client_id, params)


@router.get("/{client_id}/contacts/{contact_id}", response_model=ClientContactResponse)
async def get_client_contact(
    client_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientContactResponse:
    return await service.get_contact(current_user, client_id, contact_id)


@router.patch("/{client_id}/contacts/{contact_id}", response_model=ClientContactResponse)
async def update_client_contact(
    client_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: ClientContactUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientContactResponse:
    return await service.update_contact(current_user, client_id, contact_id, body)


@router.delete("/{client_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_contact(
    client_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> None:
    await service.delete_contact(current_user, client_id, contact_id)
