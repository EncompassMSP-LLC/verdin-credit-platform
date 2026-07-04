"""Multi-IdP federation provider registry models."""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class IdpFederationProviderType(StrEnum):
    OIDC = "oidc"
    SAML = "saml"


class IdpFederationProvider(Base, TimestampMixin):
    __tablename__ = "idp_federation_providers"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "provider_key",
            name="uq_idp_federation_org_provider_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    provider_key: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_type: Mapped[IdpFederationProviderType] = mapped_column(
        Enum(
            IdpFederationProviderType,
            name="idp_federation_provider_type",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    issuer_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    registered_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
