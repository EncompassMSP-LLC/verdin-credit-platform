"""Client portal push notification endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.client_portal.dependencies import (
    get_current_portal_user,
    require_client_portal_enabled,
    require_portal_push_enabled,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.push_service import ClientPortalPushService
from api.modules.client_portal.schemas import (
    PortalPushStatusResponse,
    PortalPushSubscribeRequest,
    PortalPushSubscriptionResponse,
)

router = APIRouter(prefix="/portal/push", tags=["Client Portal"])


def get_portal_push_service(db: AsyncSession = Depends(get_db)) -> ClientPortalPushService:
    return ClientPortalPushService.from_session(db)


@router.get(
    "/status",
    response_model=PortalPushStatusResponse,
    dependencies=[Depends(require_portal_push_enabled)],
)
async def get_portal_push_status_endpoint(
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalPushService = Depends(get_portal_push_service),
) -> PortalPushStatusResponse:
    return await service.get_status(portal_user)


@router.post(
    "/subscribe",
    response_model=PortalPushSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_portal_push_enabled)],
)
async def subscribe_portal_push(
    body: PortalPushSubscribeRequest,
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalPushService = Depends(get_portal_push_service),
) -> PortalPushSubscriptionResponse:
    return await service.subscribe(portal_user, body)


@router.delete(
    "/subscriptions/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_portal_push_enabled)],
)
async def unsubscribe_portal_push(
    subscription_id: uuid.UUID,
    portal_user: ClientPortalUser = Depends(get_current_portal_user),
    _: None = Depends(require_client_portal_enabled),
    service: ClientPortalPushService = Depends(get_portal_push_service),
) -> None:
    await service.unsubscribe(portal_user, subscription_id)
