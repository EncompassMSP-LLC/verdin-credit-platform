"""Client and contact domain schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.clients.models import Client, ClientContact, ClientStatus, ContactRelationship

ClientSortField = Literal["created_at", "updated_at", "display_name", "status"]
ClientSortOrder = Literal["asc", "desc"]

ContactSortField = Literal["created_at", "updated_at", "full_name", "relationship"]
ContactSortOrder = Literal["asc", "desc"]


class ClientCreate(BaseSchema):
    display_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    mailing_address_line1: str = Field(min_length=1, max_length=255)
    mailing_address_line2: str | None = Field(default=None, max_length=255)
    mailing_city: str = Field(min_length=1, max_length=100)
    mailing_state: str = Field(min_length=1, max_length=50)
    mailing_postal_code: str = Field(min_length=1, max_length=20)
    status: ClientStatus = ClientStatus.ACTIVE
    notes: str | None = None


class ClientUpdate(BaseSchema):
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    mailing_address_line1: str | None = Field(default=None, min_length=1, max_length=255)
    mailing_address_line2: str | None = Field(default=None, max_length=255)
    mailing_city: str | None = Field(default=None, min_length=1, max_length=100)
    mailing_state: str | None = Field(default=None, min_length=1, max_length=50)
    mailing_postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    status: ClientStatus | None = None
    notes: str | None = None


class ClientListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    status: ClientStatus | None = None
    sort_by: ClientSortField = "created_at"
    sort_order: ClientSortOrder = "desc"


class ClientResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    display_name: str
    email: str | None
    phone: str | None
    status: ClientStatus
    notes: str | None
    mailing_address_line1: str | None
    mailing_address_line2: str | None
    mailing_city: str | None
    mailing_state: str | None
    mailing_postal_code: str | None
    identity_document_id: uuid.UUID | None
    proof_of_address_document_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, client: Client) -> "ClientResponse":
        return cls(
            id=client.id,
            organization_id=client.organization_id,
            display_name=client.display_name,
            email=client.email,
            phone=client.phone,
            status=client.status,
            notes=client.notes,
            mailing_address_line1=client.mailing_address_line1,
            mailing_address_line2=client.mailing_address_line2,
            mailing_city=client.mailing_city,
            mailing_state=client.mailing_state,
            mailing_postal_code=client.mailing_postal_code,
            identity_document_id=client.identity_document_id,
            proof_of_address_document_id=client.proof_of_address_document_id,
            created_at=client.created_at,
            updated_at=client.updated_at,
            deleted_at=client.deleted_at,
            created_by_id=client.created_by_id,
            updated_by_id=client.updated_by_id,
        )


class ClientContactCreate(BaseSchema):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    relationship_type: ContactRelationship = ContactRelationship.OTHER
    is_primary: bool = False
    notes: str | None = None


class ClientContactUpdate(BaseSchema):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    relationship_type: ContactRelationship | None = None
    is_primary: bool | None = None
    notes: str | None = None


class ClientContactListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    relationship_type: ContactRelationship | None = None
    is_primary: bool | None = None
    sort_by: ContactSortField = "created_at"
    sort_order: ContactSortOrder = "desc"


class ClientContactResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    relationship_type: ContactRelationship
    is_primary: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, contact: ClientContact) -> "ClientContactResponse":
        return cls(
            id=contact.id,
            organization_id=contact.organization_id,
            client_id=contact.client_id,
            full_name=contact.full_name,
            email=contact.email,
            phone=contact.phone,
            relationship_type=contact.relationship_type,
            is_primary=contact.is_primary,
            notes=contact.notes,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            deleted_at=contact.deleted_at,
            created_by_id=contact.created_by_id,
            updated_by_id=contact.updated_by_id,
        )
