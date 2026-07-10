"""Client self-enrollment persistence models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.database.base import Base


class ClientEnrollmentStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ClientEnrollment(Base):
    __tablename__ = "client_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    status: Mapped[ClientEnrollmentStatus] = mapped_column(
        Enum(
            ClientEnrollmentStatus,
            name="client_enrollment_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=ClientEnrollmentStatus.PENDING_PAYMENT,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mailing_address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    mailing_address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mailing_city: Mapped[str] = mapped_column(String(100), nullable=False)
    mailing_state: Mapped[str] = mapped_column(String(50), nullable=False)
    mailing_postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )
    stripe_payment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True
    )
    portal_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_portal_users.id"), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
