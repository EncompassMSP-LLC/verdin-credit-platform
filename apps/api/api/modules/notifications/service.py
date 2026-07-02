"""Notification service — business logic for in-app notifications."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.email_delivery import (
    EmailDeliveryNotReadyError,
    EmailMessage,
    get_email_delivery_status,
    require_email_delivery_ready,
    send_email_message,
)
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.modules.notifications.email_delivery_repository import (
    EmailDeliveryLogListFilters,
    EmailDeliveryLogRepository,
)
from api.modules.notifications.models import (
    EmailDeliveryLog,
    EmailDeliveryLogStatus,
    Notification,
    NotificationCategory,
)
from api.modules.notifications.permissions import NOTIFICATION_CREATE_ROLE
from api.modules.notifications.repository import NotificationListFilters, NotificationRepository
from api.modules.notifications.schemas import (
    EmailDeliveryAttemptResponse,
    EmailDeliveryLogResponse,
    EmailDeliveryStatusResponse,
    EmailSendRequest,
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
        email_delivery_repo: EmailDeliveryLogRepository | None = None,
    ) -> None:
        self._notifications = notification_repo
        self._users = user_repo
        self._email_deliveries = email_delivery_repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "NotificationService":
        return cls(
            NotificationRepository(session),
            UserRepository(session),
            EmailDeliveryLogRepository(session),
        )

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
    def _to_response(
        notification: Notification,
        *,
        email_delivery: EmailDeliveryAttemptResponse | None = None,
    ) -> NotificationResponse:
        return NotificationResponse.model_validate(
            {
                **NotificationResponse.model_validate(notification).model_dump(),
                "email_delivery": email_delivery,
            }
        )

    @staticmethod
    def _to_delivery_log_response(log: EmailDeliveryLog) -> EmailDeliveryLogResponse:
        return EmailDeliveryLogResponse(
            id=log.id,
            organization_id=log.organization_id,
            notification_id=log.notification_id,
            recipient_user_id=log.recipient_user_id,
            recipient_email=log.recipient_email,
            subject=log.subject,
            provider=log.provider,
            status=log.status.value,
            provider_message_id=log.provider_message_id,
            error_message=log.error_message,
            sent_by_user_id=log.sent_by_user_id,
            created_at=log.created_at,
            updated_at=log.updated_at,
        )

    async def _get_org_user(
        self,
        user_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> User:
        assert self._users is not None
        recipient = await self._users.get_by_id(user_id)
        if recipient is None or recipient.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient user not found",
            )
        return recipient

    async def _record_email_delivery(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID | None,
        recipient_email: str,
        subject: str,
        provider: str,
        send_result_success: bool,
        provider_message_id: str | None,
        error_message: str | None,
        notification_id: uuid.UUID | None,
        sent_by_user_id: uuid.UUID,
    ) -> EmailDeliveryLog:
        assert self._email_deliveries is not None
        log = EmailDeliveryLog(
            organization_id=organization_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
            recipient_email=recipient_email,
            subject=subject,
            provider=provider,
            status=(
                EmailDeliveryLogStatus.SENT
                if send_result_success
                else EmailDeliveryLogStatus.FAILED
            ),
            provider_message_id=provider_message_id,
            error_message=error_message,
            sent_by_user_id=sent_by_user_id,
        )
        return await self._email_deliveries.create(log)

    async def _send_org_user_email(
        self,
        *,
        actor: User,
        organization_id: uuid.UUID,
        recipient: User,
        subject: str,
        body: str,
        notification_id: uuid.UUID | None = None,
    ) -> EmailDeliveryLogResponse:
        self._require_create(actor)
        if not recipient.email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Recipient user does not have an email address",
            )

        try:
            delivery_status = require_email_delivery_ready()
        except EmailDeliveryNotReadyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Email delivery is not ready", "blockers": exc.blockers},
            ) from exc

        send_result = await send_email_message(
            EmailMessage(to=recipient.email, subject=subject, body_text=body),
        )
        log = await self._record_email_delivery(
            organization_id=organization_id,
            recipient_user_id=recipient.id,
            recipient_email=recipient.email,
            subject=subject,
            provider=delivery_status.provider,
            send_result_success=send_result.success,
            provider_message_id=send_result.provider_message_id,
            error_message=send_result.error,
            notification_id=notification_id,
            sent_by_user_id=actor.id,
        )
        return self._to_delivery_log_response(log)

    async def create_notification(
        self,
        actor: User,
        body: NotificationCreate,
    ) -> NotificationResponse:
        organization_id = self._require_organization(actor)
        self._require_create(actor)

        recipient = await self._get_org_user(
            body.recipient_user_id, organization_id=organization_id
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

        email_delivery: EmailDeliveryAttemptResponse | None = None
        if body.deliver_email:
            email_delivery = await self._attempt_notification_email(
                actor=actor,
                organization_id=organization_id,
                recipient=recipient,
                notification=created,
            )

        return self._to_response(created, email_delivery=email_delivery)

    async def _attempt_notification_email(
        self,
        *,
        actor: User,
        organization_id: uuid.UUID,
        recipient: User,
        notification: Notification,
    ) -> EmailDeliveryAttemptResponse:
        if not recipient.email:
            return EmailDeliveryAttemptResponse(
                attempted=True,
                status="failed",
                error="Recipient user does not have an email address",
            )

        try:
            delivery_status = require_email_delivery_ready()
        except EmailDeliveryNotReadyError as exc:
            return EmailDeliveryAttemptResponse(
                attempted=True,
                status="failed",
                error="; ".join(exc.blockers),
            )

        send_result = await send_email_message(
            EmailMessage(
                to=recipient.email,
                subject=notification.title,
                body_text=notification.body or notification.title,
            ),
        )
        log = await self._record_email_delivery(
            organization_id=organization_id,
            recipient_user_id=recipient.id,
            recipient_email=recipient.email,
            subject=notification.title,
            provider=delivery_status.provider,
            send_result_success=send_result.success,
            provider_message_id=send_result.provider_message_id,
            error_message=send_result.error,
            notification_id=notification.id,
            sent_by_user_id=actor.id,
        )
        return EmailDeliveryAttemptResponse(
            attempted=True,
            status=log.status.value,
            delivery_log_id=log.id,
            error=send_result.error,
        )

    async def send_email(
        self,
        actor: User,
        body: EmailSendRequest,
    ) -> EmailDeliveryLogResponse:
        organization_id = self._require_organization(actor)
        recipient = await self._get_org_user(
            body.recipient_user_id, organization_id=organization_id
        )

        if body.notification_id is not None:
            notification = await self._notifications.get_by_id(
                body.notification_id,
                organization_id=organization_id,
                recipient_user_id=recipient.id,
            )
            if notification is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found for recipient",
                )

        return await self._send_org_user_email(
            actor=actor,
            organization_id=organization_id,
            recipient=recipient,
            subject=body.subject,
            body=body.body,
            notification_id=body.notification_id,
        )

    async def list_email_deliveries(
        self,
        user: User,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[EmailDeliveryLogResponse]:
        organization_id = self._require_organization(user)
        self._require_create(user)
        assert self._email_deliveries is not None

        skip = (page - 1) * page_size
        filters = EmailDeliveryLogListFilters(
            organization_id=organization_id,
            skip=skip,
            limit=page_size,
        )
        items, total = await self._email_deliveries.list_and_count(filters)
        return paginate(
            [self._to_delivery_log_response(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

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
        delivery_status = get_email_delivery_status()
        return EmailDeliveryStatusResponse(
            enabled=delivery_status.enabled,
            ready=delivery_status.ready,
            provider=delivery_status.provider,
            from_address=delivery_status.from_address,
            blockers=delivery_status.blockers,
        )
