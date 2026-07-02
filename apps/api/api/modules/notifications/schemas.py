"""Notification Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.modules.notifications.models import NotificationCategory

NotificationSortField = Literal["created_at", "read_at"]
NotificationSortOrder = Literal["asc", "desc"]


class NotificationCreate(BaseModel):
    recipient_user_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    body: str | None = None
    category: NotificationCategory = NotificationCategory.SYSTEM
    entity_type: str | None = Field(default=None, max_length=50)
    entity_id: uuid.UUID | None = None
    source_module: str | None = Field(default=None, max_length=50)
    action_url: str | None = Field(default=None, max_length=500)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    recipient_user_id: uuid.UUID
    title: str
    body: str | None
    category: NotificationCategory
    read_at: datetime | None
    entity_type: str | None
    entity_id: uuid.UUID | None
    source_module: str | None
    action_url: str | None
    created_at: datetime
    updated_at: datetime


class NotificationListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    unread_only: bool | None = None
    category: NotificationCategory | None = None
    sort_by: NotificationSortField = "created_at"
    sort_order: NotificationSortOrder = "desc"


class UnreadCountResponse(BaseModel):
    unread_count: int


class EmailDeliveryStatusResponse(BaseModel):
    enabled: bool
    ready: bool
    provider: str
    from_address: str | None
    blockers: list[str]
