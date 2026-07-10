"""Client management endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.models import (
    AccountBureau,
    AccountStatus,
    AccountType,
    DisputeStatus,
    PaymentStatus,
)
from api.modules.accounts.schemas import (
    AccountListParams,
    AccountResponse,
    AccountSortField,
    AccountSortOrder,
)
from api.modules.accounts.service import AccountService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.client_portal.schemas import (
    ClientPortalUserProvision,
    ClientPortalUserResponse,
    ClientPortalUserUpdate,
)
from api.modules.client_portal.service import ClientPortalProvisioningService
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
from api.modules.documents.schemas import DocumentResponse
from api.modules.documents.service import DocumentService

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService.from_session(db)


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService.from_session(db)


def get_portal_provisioning_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalProvisioningService:
    return ClientPortalProvisioningService.from_session(db)


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService.from_session(db)


def get_client_account_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    bureau: AccountBureau | None = None,
    account_type: AccountType | None = None,
    account_status: AccountStatus | None = None,
    payment_status: PaymentStatus | None = None,
    dispute_status: DisputeStatus | None = None,
    sort_by: AccountSortField = "created_at",
    sort_order: AccountSortOrder = "desc",
) -> AccountListParams:
    return AccountListParams(
        page=page,
        page_size=page_size,
        search=search,
        bureau=bureau,
        account_type=account_type,
        account_status=account_status,
        payment_status=payment_status,
        dispute_status=dispute_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


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


@router.get("/{client_id}/accounts", response_model=PaginatedResponse[AccountResponse])
async def list_client_accounts(
    client_id: uuid.UUID,
    params: AccountListParams = Depends(get_client_account_list_params),
    current_user: User = Depends(get_current_user),
    client_service: ClientService = Depends(get_client_service),
    account_service: AccountService = Depends(get_account_service),
) -> PaginatedResponse[AccountResponse]:
    await client_service.get_client(current_user, client_id)
    return await account_service.list_client_accounts(current_user, client_id, params)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    body: ClientUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    return await service.update_client(current_user, client_id, body)


@router.post(
    "/{client_id}/identity-document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_client_identity_document(
    client_id: uuid.UUID,
    case_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    client_service: ClientService = Depends(get_client_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    await client_service.get_client(current_user, client_id)
    return await document_service.upload_identity_document(
        current_user,
        case_id=case_id,
        file=file,
        title=title,
        client_id=client_id,
    )


@router.post(
    "/{client_id}/proof-of-address-document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_client_proof_of_address_document(
    client_id: uuid.UUID,
    case_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    client_service: ClientService = Depends(get_client_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    await client_service.get_client(current_user, client_id)
    return await document_service.upload_proof_of_address_document(
        current_user,
        case_id=case_id,
        file=file,
        title=title,
        client_id=client_id,
    )


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


@router.post(
    "/{client_id}/portal-user",
    response_model=ClientPortalUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def provision_client_portal_user(
    client_id: uuid.UUID,
    body: ClientPortalUserProvision,
    current_user: User = Depends(get_current_user),
    service: ClientPortalProvisioningService = Depends(get_portal_provisioning_service),
) -> ClientPortalUserResponse:
    return await service.provision_portal_user(current_user, client_id, body)


@router.get("/{client_id}/portal-user", response_model=ClientPortalUserResponse)
async def get_client_portal_user(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientPortalProvisioningService = Depends(get_portal_provisioning_service),
) -> ClientPortalUserResponse:
    return await service.get_portal_user(current_user, client_id)


@router.patch("/{client_id}/portal-user", response_model=ClientPortalUserResponse)
async def update_client_portal_user(
    client_id: uuid.UUID,
    body: ClientPortalUserUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientPortalProvisioningService = Depends(get_portal_provisioning_service),
) -> ClientPortalUserResponse:
    return await service.update_portal_user(current_user, client_id, body)


@router.delete("/{client_id}/portal-user", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_client_portal_user(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientPortalProvisioningService = Depends(get_portal_provisioning_service),
) -> None:
    await service.revoke_portal_user(current_user, client_id)
