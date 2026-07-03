"""Dispatch portal push notifications for secure messaging events."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.portal_push import (
    PortalPushMessage,
    PortalPushNotReadyError,
    get_portal_push_settings,
    get_portal_push_status,
    send_portal_push_message,
)
from api.modules.client_portal.push_models import PortalPushDeliveryLog, PortalPushDeliveryStatus
from api.modules.client_portal.push_repository import (
    PortalPushDeliveryLogRepository,
    PortalPushSubscriptionRepository,
)
from api.modules.client_portal.repository import ClientPortalUserRepository


async def dispatch_staff_message_push(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    case_id: uuid.UUID,
    client_id: uuid.UUID,
    thread_message_id: uuid.UUID,
    title: str,
    body_preview: str,
) -> int:
    """Notify portal client devices when staff posts a secure message."""
    if not is_feature_enabled(FeatureFlag.ENABLE_PORTAL_PUSH):
        return 0

    push_status = get_portal_push_status()
    if not push_status.enabled:
        return 0

    portal_users = ClientPortalUserRepository(session)
    portal_user = await portal_users.get_by_client_id(
        client_id,
        organization_id=organization_id,
    )
    if portal_user is None or not portal_user.is_active:
        return 0

    subscription_repo = PortalPushSubscriptionRepository(session)
    delivery_repo = PortalPushDeliveryLogRepository(session)
    subscriptions = await subscription_repo.list_active_for_portal_user(
        organization_id=organization_id,
        portal_user_id=portal_user.id,
    )
    if not subscriptions:
        await delivery_repo.create(
            PortalPushDeliveryLog(
                organization_id=organization_id,
                portal_user_id=portal_user.id,
                subscription_id=None,
                thread_message_id=thread_message_id,
                title=title,
                body=body_preview,
                provider=push_status.provider,
                status=PortalPushDeliveryStatus.SKIPPED,
                error_message="No active push subscriptions",
            )
        )
        return 0

    settings = get_portal_push_settings()
    message = PortalPushMessage(
        title=title,
        body=body_preview,
        action_url=f"/portal/cases/{case_id}",
    )

    delivered = 0
    for subscription in subscriptions:
        if push_status.ready:
            try:
                result = await send_portal_push_message(
                    endpoint=subscription.endpoint,
                    p256dh_key=subscription.p256dh_key,
                    auth_key=subscription.auth_key,
                    message=message,
                    settings=settings,
                )
                status_value = (
                    PortalPushDeliveryStatus.SENT
                    if result.success
                    else PortalPushDeliveryStatus.FAILED
                )
                await delivery_repo.create(
                    PortalPushDeliveryLog(
                        organization_id=organization_id,
                        portal_user_id=portal_user.id,
                        subscription_id=subscription.id,
                        thread_message_id=thread_message_id,
                        title=title,
                        body=body_preview,
                        provider=push_status.provider,
                        status=status_value,
                        provider_message_id=result.provider_message_id,
                        error_message=result.error,
                    )
                )
                if result.success:
                    delivered += 1
            except PortalPushNotReadyError as exc:
                await delivery_repo.create(
                    PortalPushDeliveryLog(
                        organization_id=organization_id,
                        portal_user_id=portal_user.id,
                        subscription_id=subscription.id,
                        thread_message_id=thread_message_id,
                        title=title,
                        body=body_preview,
                        provider=push_status.provider,
                        status=PortalPushDeliveryStatus.SKIPPED,
                        error_message="; ".join(exc.blockers),
                    )
                )
        else:
            await delivery_repo.create(
                PortalPushDeliveryLog(
                    organization_id=organization_id,
                    portal_user_id=portal_user.id,
                    subscription_id=subscription.id,
                    thread_message_id=thread_message_id,
                    title=title,
                    body=body_preview,
                    provider=push_status.provider,
                    status=PortalPushDeliveryStatus.SKIPPED,
                    error_message="; ".join(push_status.blockers),
                )
            )

    return delivered
