"""Audit mixins and utilities for tracking entity changes."""

import uuid
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class Auditable(Protocol):
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None


class SoftDeletable(Protocol):
    deleted_at: datetime | None

    def soft_delete(self) -> None: ...


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class AuditMixin:
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)


def apply_audit_on_create(entity: Auditable, user_id: uuid.UUID | None) -> None:
    if user_id is not None:
        entity.created_by_id = user_id
        entity.updated_by_id = user_id


def apply_audit_on_update(entity: Auditable, user_id: uuid.UUID | None) -> None:
    if user_id is not None:
        entity.updated_by_id = user_id
