"""Portal notification service — borrower feed + read state (LRP-302A)."""

from __future__ import annotations

import uuid
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse, paginate
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.notification_models import PortalNotification
from api.modules.client_portal.notification_repository import (
    PortalNotificationListFilters,
    PortalNotificationRepository,
)
from api.modules.client_portal.schemas import (
    PortalNotificationListParams,
    PortalNotificationResponse,
    PortalUnreadCountResponse,
)
from api.modules.notifications.models import NotificationCategory


def sanitize_portal_action_url(action_url: str | None) -> str | None:
    """Allow only relative /portal/* deep links; drop absolute or staff URLs."""
    if not action_url:
        return None
    raw = action_url.strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if not path.startswith("/portal"):
        return None
    if ".." in path or "\\" in path:
        return None
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{path}{query}"[:500]


class ClientPortalNotificationService:
    def __init__(self, repo: PortalNotificationRepository) -> None:
        self._repo = repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalNotificationService:
        return cls(PortalNotificationRepository(session))

    @staticmethod
    def _to_response(notification: PortalNotification) -> PortalNotificationResponse:
        return PortalNotificationResponse(
            id=notification.id,
            title=notification.title,
            body=notification.body,
            category=notification.category,
            read_at=notification.read_at,
            entity_type=notification.entity_type,
            entity_id=notification.entity_id,
            action_url=sanitize_portal_action_url(notification.action_url),
            created_at=notification.created_at,
        )

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        recipient_portal_user_id: uuid.UUID,
        title: str,
        body: str | None = None,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        source_module: str | None = None,
        action_url: str | None = None,
    ) -> PortalNotification:
        notification = PortalNotification(
            organization_id=organization_id,
            client_id=client_id,
            recipient_portal_user_id=recipient_portal_user_id,
            title=title,
            body=body,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            source_module=source_module,
            action_url=sanitize_portal_action_url(action_url),
        )
        return await self._repo.create(notification)

    async def list_notifications(
        self,
        portal_user: ClientPortalUser,
        params: PortalNotificationListParams,
    ) -> PaginatedResponse[PortalNotificationResponse]:
        items, total = await self._repo.list_and_count(
            PortalNotificationListFilters(
                organization_id=portal_user.organization_id,
                recipient_portal_user_id=portal_user.id,
                client_id=portal_user.client_id,
                unread_only=params.unread_only,
                category=params.category,
                skip=(params.page - 1) * params.page_size,
                limit=params.page_size,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
            )
        )
        return paginate(
            [self._to_response(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_unread_count(self, portal_user: ClientPortalUser) -> PortalUnreadCountResponse:
        count = await self._repo.count_unread(
            organization_id=portal_user.organization_id,
            recipient_portal_user_id=portal_user.id,
            client_id=portal_user.client_id,
        )
        return PortalUnreadCountResponse(unread_count=count)

    async def mark_read(
        self,
        portal_user: ClientPortalUser,
        notification_id: uuid.UUID,
    ) -> PortalNotificationResponse:
        notification = await self._repo.get_by_id(
            notification_id,
            organization_id=portal_user.organization_id,
            recipient_portal_user_id=portal_user.id,
            client_id=portal_user.client_id,
        )
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        # Idempotent: already-read rows return unchanged (no audit noise).
        updated = await self._repo.mark_read(notification)
        return self._to_response(updated)

    async def mark_all_read(self, portal_user: ClientPortalUser) -> PortalUnreadCountResponse:
        await self._repo.mark_all_read(
            organization_id=portal_user.organization_id,
            recipient_portal_user_id=portal_user.id,
            client_id=portal_user.client_id,
        )
        return await self.get_unread_count(portal_user)
