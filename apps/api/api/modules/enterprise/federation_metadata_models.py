"""SAML federation metadata upload audit models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class SamlMetadataValidationStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"


class SamlFederationMetadataUpload(Base, TimestampMixin):
    __tablename__ = "saml_federation_metadata_uploads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    provider_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_xml: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    validation_status: Mapped[SamlMetadataValidationStatus] = mapped_column(
        Enum(
            SamlMetadataValidationStatus,
            name="saml_metadata_validation_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    validation_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
