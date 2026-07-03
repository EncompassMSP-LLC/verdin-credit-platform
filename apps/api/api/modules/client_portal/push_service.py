"""Portal push notification service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.portal_push import (
    PortalPushMessage,
    get_portal_push_settings,
    get_portal_push_status,
    send_portal_push_message,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.push_models import PortalPushSubscription
from api.modules.client_portal.push_repository import PortalPushSubscriptionRepository
from api.modules.client_portal.schemas import (
    PortalPushStatusResponse,
    PortalPushSubscribeRequest,
    PortalPushSubscriptionResponse,
)


class ClientPortalPushService:
    def __init__(
        self,
        subscription_repo: PortalPushSubscriptionRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._subscriptions = subscription_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalPushService:
        return cls(PortalPushSubscriptionRepository(session), session=session)

    async def get_status(self, portal_user: ClientPortalUser) -> PortalPushStatusResponse:
        status_payload = get_portal_push_status()
        active_count = await self._subscriptions.count_active_for_portal_user(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
        )
        return PortalPushStatusResponse(
            enabled=status_payload.enabled,
            ready=status_payload.ready,
            provider=status_payload.provider,
            vapid_public_key=status_payload.vapid_public_key,
            blockers=status_payload.blockers,
            active_subscription_count=active_count,
        )

    async def subscribe(
        self,
        portal_user: ClientPortalUser,
        data: PortalPushSubscribeRequest,
    ) -> PortalPushSubscriptionResponse:
        push_status = get_portal_push_status()
        if not push_status.enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal push is not enabled",
            )

        existing = await self._subscriptions.get_by_endpoint(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
            endpoint=data.endpoint,
        )
        if existing is not None:
            existing.p256dh_key = data.p256dh_key
            existing.auth_key = data.auth_key
            existing.user_agent = data.user_agent
            existing.is_active = True
            subscription = await self._subscriptions.save(existing)
        else:
            subscription = PortalPushSubscription(
                organization_id=portal_user.organization_id,
                portal_user_id=portal_user.id,
                endpoint=data.endpoint,
                p256dh_key=data.p256dh_key,
                auth_key=data.auth_key,
                user_agent=data.user_agent,
                is_active=True,
            )
            subscription = await self._subscriptions.create(subscription)

        if self._session is not None:
            await self._session.commit()

        return PortalPushSubscriptionResponse.from_model(subscription)

    async def unsubscribe(
        self,
        portal_user: ClientPortalUser,
        subscription_id: uuid.UUID,
    ) -> None:
        deactivated = await self._subscriptions.deactivate(
            subscription_id,
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
        )
        if not deactivated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Push subscription not found",
            )
        if self._session is not None:
            await self._session.commit()

    async def send_test_push(self, portal_user: ClientPortalUser) -> PortalPushSubscriptionResponse:
        push_status = get_portal_push_status()
        if not push_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"blockers": push_status.blockers},
            )

        subscriptions = await self._subscriptions.list_active_for_portal_user(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
        )
        if not subscriptions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active push subscriptions found",
            )

        subscription = subscriptions[0]
        settings = get_portal_push_settings()
        await send_portal_push_message(
            endpoint=subscription.endpoint,
            p256dh_key=subscription.p256dh_key,
            auth_key=subscription.auth_key,
            message=PortalPushMessage(
                title="Portal push test",
                body="Push notification scaffold is configured.",
                action_url=None,
            ),
            settings=settings,
        )
        return PortalPushSubscriptionResponse.from_model(subscription)
