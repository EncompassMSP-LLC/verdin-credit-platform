"""Authentication domain models."""

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin
from api.core.constants import UserRole
from api.database.base import Base


class Organization(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    cases: Mapped[list["Case"]] = relationship(back_populates="organization")
    accounts: Mapped[list["Account"]] = relationship(back_populates="organization")


class User(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.READ_ONLY,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    organization: Mapped["Organization | None"] = relationship(back_populates="users")
    assigned_cases: Mapped[list["Case"]] = relationship(
        back_populates="assigned_to", foreign_keys="Case.assigned_to_id"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assigned_user", foreign_keys="Task.assigned_user_id"
    )
