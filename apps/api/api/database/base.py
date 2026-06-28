"""SQLAlchemy declarative base."""

from sqlalchemy.orm import DeclarativeBase

from api.core.audit import AuditMixin, SoftDeleteMixin, TimestampMixin

__all__ = ["AuditMixin", "Base", "SoftDeleteMixin", "TimestampMixin"]


class Base(DeclarativeBase):
    pass
