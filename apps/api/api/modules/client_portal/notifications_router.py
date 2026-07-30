"""Client portal notification endpoints (LRP-302A)."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.notification_service import ClientPortalNotificationService
from api.modules.client_portal.schemas import (
    PortalNotificationListParams,
    PortalNotificationResponse,
    PortalUnreadCountResponse,
)
from api.modules.notifications.models import NotificationCategory
from api.modules.notifications.schemas import NotificationSortField, NotificationSortOrder

router = APIRouter(prefix="/portal/notifications", tags=["Client Portal"])


def get_portal_notification_service(
    db: AsyncSession = Depends(get_db),
) -> ClientPortalNotificationService:
    return ClientPortalNotificationService.from_session(db)


def get_portal_notification_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool | None = None,
    category: NotificationCategory | None = None,
    sort_by: NotificationSortField = "created_at",
    sort_order: NotificationSortOrder = "desc",
) -> PortalNotificationListParams:
    return PortalNotificationListParams(
        page=page,
        page_size=page_size,
        unread_only=unread_only,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("", response_model=PaginatedResponse[PortalNotificationResponse])
async def list_portal_notifications(
    params: PortalNotificationListParams = Depends(get_portal_notification_list_params),
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalNotificationService = Depends(get_portal_notification_service),
) -> PaginatedResponse[PortalNotificationResponse]:
    return await service.list_notifications(portal_user, params)


@router.get("/unread-count", response_model=PortalUnreadCountResponse)
async def get_portal_unread_count(
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalNotificationService = Depends(get_portal_notification_service),
) -> PortalUnreadCountResponse:
    return await service.get_unread_count(portal_user)


@router.post("/mark-all-read", response_model=PortalUnreadCountResponse)
async def mark_all_portal_notifications_read(
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalNotificationService = Depends(get_portal_notification_service),
) -> PortalUnreadCountResponse:
    return await service.mark_all_read(portal_user)


@router.post("/{notification_id}/read", response_model=PortalNotificationResponse)
async def mark_portal_notification_read(
    notification_id: uuid.UUID,
    _: None = Depends(require_client_portal_enabled),
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    service: ClientPortalNotificationService = Depends(get_portal_notification_service),
) -> PortalNotificationResponse:
    return await service.mark_read(portal_user, notification_id)
