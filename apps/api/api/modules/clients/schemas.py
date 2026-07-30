"""Client and contact domain schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import EmailStr, Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.clients.models import (
    AttorneyRepresentationStatus,
    Client,
    ClientContact,
    ClientStatus,
    ContactRelationship,
    DncAssistanceStatus,
    PreferredCommunicationChannel,
)

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


class PreferenceEventItem(BaseSchema):
    at: str
    action: str
    actor_id: str | None = None
    detail: str | None = None


class ClientCommunicationPreferencesUpdate(BaseSchema):
    preferred_channel: PreferredCommunicationChannel | None = None
    do_not_text: bool | None = None
    do_not_email: bool | None = None
    best_calling_hours: str | None = Field(default=None, max_length=255)
    workplace_calls_prohibited: bool | None = None
    attorney_representation_status: AttorneyRepresentationStatus | None = None
    collector_opt_out_recorded: bool | None = None
    dnc_assistance_requested: bool | None = None
    dnc_consent_attested: bool | None = None
    dnc_phone_ownership_confirmed: bool | None = None
    dnc_disclosure_acknowledged: bool | None = None
    dnc_phone_number: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class ClientCommunicationPreferencesResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    preferred_channel: PreferredCommunicationChannel
    do_not_text: bool
    do_not_email: bool
    best_calling_hours: str | None
    workplace_calls_prohibited: bool
    attorney_representation_status: AttorneyRepresentationStatus
    collector_opt_out_recorded: bool
    collector_opt_out_recorded_at: datetime | None
    dnc_assistance_requested: bool
    dnc_consent_attested: bool
    dnc_phone_ownership_confirmed: bool
    dnc_disclosure_acknowledged: bool
    dnc_phone_number: str | None
    dnc_status: DncAssistanceStatus
    dnc_registry_opened_at: datetime | None
    dnc_completed_at: datetime | None
    dnc_followup_due_at: datetime | None
    preference_events: list[PreferenceEventItem]
    notes: str | None
    official_dnc_registry_url: str
    dnc_disclosure: str
    disclaimer: str
    communication_request_draft: str
    created_at: datetime
    updated_at: datetime


class UnwantedCallIncidentCreate(BaseSchema):
    called_at: datetime
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    creditor_or_collector_name: str | None = Field(default=None, max_length=255)
    party_type: Literal["creditor", "collector", "telemarketer", "unknown"] = "unknown"
    caller_number: str | None = Field(default=None, max_length=50)
    called_number: str | None = Field(default=None, max_length=50)
    channel: Literal["phone", "voip", "sms", "unknown"] = "phone"
    notes: str | None = None
    status: Literal[
        "open",
        "documenting",
        "draft_ready",
        "submitted_externally",
        "follow_up_due",
        "closed",
        "abandoned",
    ] = "open"
    follow_up_due_at: datetime | None = None
    follow_up_notes: str | None = None
    complaint_target: Literal["none", "ftc", "cfpb", "state_ag", "carrier", "other"] = "none"
    evidence_document_id: uuid.UUID | None = None


class UnwantedCallIncidentUpdate(BaseSchema):
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    creditor_or_collector_name: str | None = Field(default=None, max_length=255)
    party_type: Literal["creditor", "collector", "telemarketer", "unknown"] | None = None
    called_at: datetime | None = None
    caller_number: str | None = Field(default=None, max_length=50)
    called_number: str | None = Field(default=None, max_length=50)
    channel: Literal["phone", "voip", "sms", "unknown"] | None = None
    notes: str | None = None
    status: (
        Literal[
            "open",
            "documenting",
            "draft_ready",
            "submitted_externally",
            "follow_up_due",
            "closed",
            "abandoned",
        ]
        | None
    ) = None
    follow_up_due_at: datetime | None = None
    follow_up_notes: str | None = None
    complaint_target: Literal["none", "ftc", "cfpb", "state_ag", "carrier", "other"] | None = None
    external_submission_status: (
        Literal["not_started", "draft_prepared", "client_submitted", "staff_recorded"] | None
    ) = None
    external_reference: str | None = Field(default=None, max_length=255)
    evidence_document_id: uuid.UUID | None = None
    refresh_draft: bool = False


class UnwantedCallIncidentResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    account_id: uuid.UUID | None
    creditor_or_collector_name: str | None
    party_type: str
    called_at: datetime
    caller_number: str | None
    called_number: str | None
    channel: str
    notes: str | None
    preference_snapshot: dict[str, Any]
    eligibility_guidance: dict[str, Any]
    status: str
    follow_up_due_at: datetime | None
    follow_up_notes: str | None
    complaint_target: str
    external_submission_status: str
    external_reference: str | None
    evidence_document_id: uuid.UUID | None
    draft_text: str | None
    disclaimer: str
    created_at: datetime
    updated_at: datetime
    created_by_id: uuid.UUID | None = None


class UnwantedCallIncidentListResponse(BaseSchema):
    client_id: uuid.UUID
    disclaimer: str
    items: list[UnwantedCallIncidentResponse]
