"""Client and contact domain models."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.database.base import Base


class ClientStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ContactRelationship(StrEnum):
    PRIMARY = "primary"
    SPOUSE = "spouse"
    ATTORNEY = "attorney"
    AUTHORIZED = "authorized"
    OTHER = "other"


class PreferredCommunicationChannel(StrEnum):
    MAIL = "mail"
    PHONE = "phone"
    EMAIL = "email"
    TEXT = "text"


class AttorneyRepresentationStatus(StrEnum):
    NONE = "none"
    REPRESENTED = "represented"
    UNKNOWN = "unknown"


class DncAssistanceStatus(StrEnum):
    NOT_STARTED = "not_started"
    CONSENT_RECORDED = "consent_recorded"
    REGISTRY_LINK_OPENED = "registry_link_opened"
    AWAITING_EMAIL_CONFIRMATION = "awaiting_email_confirmation"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Client(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus, name="client_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ClientStatus.ACTIVE,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    mailing_address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mailing_address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mailing_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mailing_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mailing_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    identity_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    proof_of_address_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    contacts: Mapped[list["ClientContact"]] = relationship(back_populates="client")
    identity_document: Mapped["Document | None"] = relationship(foreign_keys=[identity_document_id])
    proof_of_address_document: Mapped["Document | None"] = relationship(
        foreign_keys=[proof_of_address_document_id]
    )
    cases: Mapped[list["Case"]] = relationship(back_populates="client")
    communication_preferences: Mapped["ClientCommunicationPreferences | None"] = relationship(
        back_populates="client",
        uselist=False,
    )


class ClientContact(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "client_contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    relationship_type: Mapped[ContactRelationship] = mapped_column(
        "relationship",
        Enum(
            ContactRelationship,
            name="contact_relationship",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ContactRelationship.OTHER,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="contacts")


class ClientCommunicationPreferences(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Staff-mediated communication preferences and Do Not Call assistance (LRP-209)."""

    __tablename__ = "client_communication_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    preferred_channel: Mapped[PreferredCommunicationChannel] = mapped_column(
        Enum(
            PreferredCommunicationChannel,
            name="preferred_communication_channel",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=PreferredCommunicationChannel.MAIL,
    )
    do_not_text: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    do_not_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    best_calling_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workplace_calls_prohibited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attorney_representation_status: Mapped[AttorneyRepresentationStatus] = mapped_column(
        Enum(
            AttorneyRepresentationStatus,
            name="attorney_representation_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=AttorneyRepresentationStatus.UNKNOWN,
    )
    collector_opt_out_recorded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    collector_opt_out_recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dnc_assistance_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dnc_consent_attested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dnc_phone_ownership_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    dnc_disclosure_acknowledged: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    dnc_phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dnc_status: Mapped[DncAssistanceStatus] = mapped_column(
        Enum(
            DncAssistanceStatus,
            name="dnc_assistance_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=DncAssistanceStatus.NOT_STARTED,
    )
    dnc_registry_opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dnc_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dnc_followup_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    preference_events: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="communication_preferences")
