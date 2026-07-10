"""Client and contact domain models."""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
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
