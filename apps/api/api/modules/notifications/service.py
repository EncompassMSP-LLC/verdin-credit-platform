"""Notification service — business logic for in-app notifications."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.email_delivery import get_email_delivery_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.notifications.permissions import NOTIFICATION_CREATE_ROLE
from api.modules.notifications.repository import NotificationListFilters, NotificationRepository
from api.modules.notifications.schemas import (
    EmailDeliveryStatusResponse,
    NotificationCreate,
    NotificationListParams,
    NotificationResponse,
    UnreadCountResponse,
)


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        user_repo: UserRepository | None = None,
    ) -> None:
        self._notifications = notification_repo
        self._users = user_repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "NotificationService":
        return cls(NotificationRepository(session), UserRepository(session))

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_create(self, user: User) -> None:
        if not has_permission(user.role, NOTIFICATION_CREATE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create notifications",
            )

    @staticmethod
    def _to_response(notification: Notification) -> NotificationResponse:
        return NotificationResponse.model_validate(notification)

    async def create_notification(
        self,
        actor: User,
        body: NotificationCreate,
    ) -> NotificationResponse:
        organization_id = self._require_organization(actor)
        self._require_create(actor)
        assert self._users is not None

        recipient = await self._users.get_by_id(body.recipient_user_id)
        if recipient is None or recipient.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient user not found",
            )

        notification = Notification(
            organization_id=organization_id,
            recipient_user_id=body.recipient_user_id,
            title=body.title,
            body=body.body,
            category=body.category,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            source_module=body.source_module,
            action_url=body.action_url,
        )
        created = await self._notifications.create(notification)
        return self._to_response(created)

    async def notify_user(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        title: str,
        body: str | None = None,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        source_module: str | None = None,
        action_url: str | None = None,
    ) -> NotificationResponse:
        """Internal helper for other modules to enqueue in-app notifications."""
        notification = Notification(
            organization_id=organization_id,
            recipient_user_id=recipient_user_id,
            title=title,
            body=body,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            source_module=source_module,
            action_url=action_url,
        )
        created = await self._notifications.create(notification)
        return self._to_response(created)

    async def list_notifications(
        self,
        user: User,
        params: NotificationListParams,
    ) -> PaginatedResponse[NotificationResponse]:
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        filters = NotificationListFilters(
            organization_id=organization_id,
            recipient_user_id=user.id,
            unread_only=params.unread_only,
            category=params.category,
            skip=skip,
            limit=params.page_size,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        items, total = await self._notifications.list_and_count(filters)
        return paginate(
            [self._to_response(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_unread_count(self, user: User) -> UnreadCountResponse:
        organization_id = self._require_organization(user)
        count = await self._notifications.count_unread(
            organization_id=organization_id,
            recipient_user_id=user.id,
        )
        return UnreadCountResponse(unread_count=count)

    async def mark_read(
        self,
        user: User,
        notification_id: uuid.UUID,
    ) -> NotificationResponse:
        organization_id = self._require_organization(user)
        notification = await self._notifications.get_by_id(
            notification_id,
            organization_id=organization_id,
            recipient_user_id=user.id,
        )
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        if notification.read_at is None:
            notification = await self._notifications.mark_read(notification)
        return self._to_response(notification)

    async def mark_all_read(self, user: User) -> UnreadCountResponse:
        organization_id = self._require_organization(user)
        await self._notifications.mark_all_read(
            organization_id=organization_id,
            recipient_user_id=user.id,
        )
        return UnreadCountResponse(unread_count=0)

    async def get_email_delivery_status(self, user: User) -> EmailDeliveryStatusResponse:
        self._require_organization(user)
        status = get_email_delivery_status()
        return EmailDeliveryStatusResponse(
            enabled=status.enabled,
            ready=status.ready,
            provider=status.provider,
            from_address=status.from_address,
            blockers=status.blockers,
        )
