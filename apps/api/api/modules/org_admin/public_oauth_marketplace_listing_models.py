"""Admin-gated public OAuth marketplace listing run models."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.core.audit import TimestampMixin
from api.database.base import Base


class PublicOAuthMarketplaceListingRunStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    LISTED = "listed"
    REJECTED = "rejected"
    FAILED = "failed"


class PublicOAuthMarketplaceListingRun(Base, TimestampMixin):
    __tablename__ = "public_oauth_marketplace_listing_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    oauth_marketplace_publishing_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("oauth_marketplace_publishing_runs.id"),
        nullable=False,
        index=True,
    )
    oauth_developer_app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("oauth_developer_apps.id"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[PublicOAuthMarketplaceListingRunStatus] = mapped_column(
        Enum(
            PublicOAuthMarketplaceListingRunStatus,
            name="public_oauth_marketplace_listing_run_status",
            create_type=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    listing_summary: Mapped[str] = mapped_column(Text, nullable=False)
    marketplace_listing_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    public_listing_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    listed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
