"""Enterprise identity enrollment domain models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class UserTotpEnrollment(Base, TimestampMixin):
    __tablename__ = "user_totp_enrollments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )
    encrypted_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    pending_encrypted_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    enrolled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserSsoEnrollment(Base, TimestampMixin):
    __tablename__ = "user_sso_enrollments"
    __table_args__ = (
        UniqueConstraint("provider", "issuer_url", "idp_subject", name="uq_user_sso_idp_subject"),
        UniqueConstraint("user_id", "provider", name="uq_user_sso_per_provider"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    issuer_url: Mapped[str] = mapped_column(String(500), nullable=False)
    idp_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
