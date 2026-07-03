"""In-app notification endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.notifications.models import NotificationCategory
from api.modules.notifications.schemas import (
    EmailDeliveryLogResponse,
    EmailDeliveryStatusResponse,
    EmailSendRequest,
    NotificationCreate,
    NotificationListParams,
    NotificationResponse,
    NotificationSortField,
    NotificationSortOrder,
    SmsDeliveryLogResponse,
    SmsDeliveryStatusResponse,
    SmsSendRequest,
    UnreadCountResponse,
)
from api.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService.from_session(db)


def get_notification_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool | None = None,
    category: NotificationCategory | None = None,
    sort_by: NotificationSortField = "created_at",
    sort_order: NotificationSortOrder = "desc",
) -> NotificationListParams:
    return NotificationListParams(
        page=page,
        page_size=page_size,
        unread_only=unread_only,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    body: NotificationCreate,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    return await service.create_notification(current_user, body)


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    params: NotificationListParams = Depends(get_notification_list_params),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> PaginatedResponse[NotificationResponse]:
    return await service.list_notifications(current_user, params)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> UnreadCountResponse:
    return await service.get_unread_count(current_user)


@router.post("/mark-all-read", response_model=UnreadCountResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> UnreadCountResponse:
    return await service.mark_all_read(current_user)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    return await service.mark_read(current_user, notification_id)


@router.get("/email/status", response_model=EmailDeliveryStatusResponse)
async def get_email_status(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> EmailDeliveryStatusResponse:
    return await service.get_email_delivery_status(current_user)


@router.post(
    "/email/send", response_model=EmailDeliveryLogResponse, status_code=status.HTTP_201_CREATED
)
async def send_notification_email(
    body: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> EmailDeliveryLogResponse:
    return await service.send_email(current_user, body)


@router.get("/email/deliveries", response_model=PaginatedResponse[EmailDeliveryLogResponse])
async def list_email_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> PaginatedResponse[EmailDeliveryLogResponse]:
    return await service.list_email_deliveries(current_user, page=page, page_size=page_size)


@router.get("/sms/status", response_model=SmsDeliveryStatusResponse)
async def get_sms_status(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> SmsDeliveryStatusResponse:
    return await service.get_sms_delivery_status(current_user)


@router.post(
    "/sms/send", response_model=SmsDeliveryLogResponse, status_code=status.HTTP_201_CREATED
)
async def send_notification_sms(
    body: SmsSendRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> SmsDeliveryLogResponse:
    return await service.send_sms(current_user, body)


@router.get("/sms/deliveries", response_model=PaginatedResponse[SmsDeliveryLogResponse])
async def list_sms_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> PaginatedResponse[SmsDeliveryLogResponse]:
    return await service.list_sms_deliveries(current_user, page=page, page_size=page_size)
