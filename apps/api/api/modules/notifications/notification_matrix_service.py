"""Notification matrix dispatcher — fan-out with audit + idempotency (LRP-202)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.email_delivery import (
    EmailDeliveryNotReadyError,
    EmailMessage,
    require_email_delivery_ready,
    send_email_message,
)
from api.modules.auth.models import User
from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.notifications.notification_matrix import (
    SCHEMA_VERSION,
    NotificationAudience,
    NotificationChannel,
    NotificationMatrixEvent,
    advisory_footer,
    get_matrix_event,
    list_matrix_events,
)
from api.modules.notifications.notification_matrix_models import NotificationMatrixDispatch
from api.modules.tasks.models import Task, TaskPriority, TaskStatus

_PARTNER_SUCCESS_ROLES = frozenset({UserRole.ADMIN, UserRole.OWNER})
_CREDIT_SPECIALIST_ROLES = frozenset({UserRole.CASE_MANAGER, UserRole.ADMIN, UserRole.OWNER})
_OPS_ROLES = frozenset({UserRole.ADMIN, UserRole.OWNER})


@dataclass
class MatrixDispatchContext:
    """Runtime recipients and content for a matrix event."""

    organization_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    title: str | None = None
    body: str | None = None
    action_url: str | None = None
    case_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None
    referring_lo_user_id: uuid.UUID | None = None
    referring_lo_email: str | None = None
    referring_lo_name: str | None = None
    borrower_user_id: uuid.UUID | None = None
    borrower_email: str | None = None
    borrower_name: str | None = None
    realtor_user_id: uuid.UUID | None = None
    realtor_email: str | None = None
    partner_user_ids: list[uuid.UUID] = field(default_factory=list)
    tcpa_consent: bool = False
    sms_phone: str | None = None
    triggered_by_user_id: uuid.UUID | None = None
    source_module: str = "notifications.matrix"
    create_crm_tasks: bool = True


class NotificationMatrixDispatcher:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def describe_matrix(self) -> dict[str, Any]:
        events = []
        for definition in list_matrix_events():
            events.append(
                {
                    "event": definition.event.value,
                    "title": definition.title,
                    "category": definition.category,
                    "group": definition.group,
                    "routes": [
                        {
                            "audience": route.audience.value,
                            "channels": sorted(ch.value for ch in route.channels),
                            "optional": route.optional,
                        }
                        for route in definition.routes
                    ],
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "sms_requires_tcpa_consent": True,
            "claim_safety": {
                "auto_filing": False,
                "underwriting_decision": False,
                "advisory_footer_required": True,
            },
            "events": events,
        }

    async def get_dispatch(
        self,
        *,
        organization_id: uuid.UUID,
        dispatch_id: uuid.UUID,
    ) -> NotificationMatrixDispatch | None:
        result = await self._session.execute(
            select(NotificationMatrixDispatch).where(
                NotificationMatrixDispatch.id == dispatch_id,
                NotificationMatrixDispatch.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_dispatches(
        self,
        *,
        organization_id: uuid.UUID,
        event_key: str | None = None,
        limit: int = 50,
    ) -> list[NotificationMatrixDispatch]:
        stmt = (
            select(NotificationMatrixDispatch)
            .where(NotificationMatrixDispatch.organization_id == organization_id)
            .order_by(NotificationMatrixDispatch.started_at.desc())
            .limit(limit)
        )
        if event_key:
            stmt = stmt.where(NotificationMatrixDispatch.event_key == event_key)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_existing(
        self,
        *,
        organization_id: uuid.UUID,
        event: NotificationMatrixEvent | str,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> NotificationMatrixDispatch | None:
        event_key = NotificationMatrixEvent(event).value
        result = await self._session.execute(
            select(NotificationMatrixDispatch).where(
                NotificationMatrixDispatch.organization_id == organization_id,
                NotificationMatrixDispatch.event_key == event_key,
                NotificationMatrixDispatch.entity_type == entity_type,
                NotificationMatrixDispatch.entity_id == entity_id,
            )
        )
        return result.scalar_one_or_none()

    async def dispatch(
        self,
        event: NotificationMatrixEvent | str,
        context: MatrixDispatchContext,
    ) -> NotificationMatrixDispatch:
        definition = get_matrix_event(event)
        existing = await self.find_existing(
            organization_id=context.organization_id,
            event=definition.event,
            entity_type=context.entity_type,
            entity_id=context.entity_id,
        )
        if existing is not None:
            return existing

        started = datetime.now(UTC)
        title = context.title or definition.title
        body = context.body or (f"{definition.title}. {advisory_footer()}")
        category = NotificationCategory(definition.category)

        deliveries: list[dict[str, Any]] = []
        for route in definition.routes:
            route_results = await self._deliver_route(
                route_audience=route.audience,
                channels=route.channels,
                optional=route.optional,
                context=context,
                title=title,
                body=body,
                category=category,
                event_key=definition.event.value,
            )
            deliveries.extend(route_results)

        run = NotificationMatrixDispatch(
            id=uuid.uuid4(),
            organization_id=context.organization_id,
            event_key=definition.event.value,
            entity_type=context.entity_type,
            entity_id=context.entity_id,
            status="completed",
            schema_version=SCHEMA_VERSION,
            triggered_by_user_id=context.triggered_by_user_id,
            started_at=started,
            completed_at=datetime.now(UTC),
            payload={
                "title": title,
                "deliveries": deliveries,
                "claim_safety": {
                    "auto_filing": False,
                    "underwriting_decision": False,
                    "advisory_footer": advisory_footer(),
                },
            },
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def _deliver_route(
        self,
        *,
        route_audience: NotificationAudience,
        channels: frozenset[NotificationChannel],
        optional: bool,
        context: MatrixDispatchContext,
        title: str,
        body: str,
        category: NotificationCategory,
        event_key: str,
    ) -> list[dict[str, Any]]:
        recipients = await self._resolve_audience(route_audience, context)
        if not recipients["user_ids"] and not recipients["emails"]:
            status = "skipped_optional" if optional else "skipped_no_recipients"
            return [
                {
                    "audience": route_audience.value,
                    "status": status,
                    "detail": recipients.get("detail") or "No recipients resolved.",
                    "channels": sorted(ch.value for ch in channels),
                }
            ]

        results: list[dict[str, Any]] = []
        for channel in sorted(channels, key=lambda c: c.value):
            if channel is NotificationChannel.IN_APP:
                for user_id in recipients["user_ids"]:
                    results.append(
                        await self._create_in_app(
                            organization_id=context.organization_id,
                            recipient_user_id=user_id,
                            title=title,
                            body=body,
                            category=category,
                            context=context,
                            audience=route_audience,
                        )
                    )
                if not recipients["user_ids"]:
                    results.append(
                        {
                            "audience": route_audience.value,
                            "channel": channel.value,
                            "status": "skipped_no_user",
                            "detail": "In-app requires a platform user id.",
                        }
                    )
            elif channel is NotificationChannel.EMAIL:
                emailed_users: set[uuid.UUID] = set()
                for user_id in recipients["user_ids"]:
                    user = await self._get_user(user_id)
                    if user is None or not user.email:
                        results.append(
                            {
                                "audience": route_audience.value,
                                "channel": channel.value,
                                "status": "skipped_no_email",
                                "recipient_user_id": str(user_id),
                            }
                        )
                        continue
                    results.append(
                        await self._send_or_defer_email(
                            to_email=user.email,
                            subject=title,
                            body_text=body,
                            audience=route_audience,
                            recipient_user_id=user.id,
                        )
                    )
                    emailed_users.add(user.id)
                for email in recipients["emails"]:
                    results.append(
                        await self._send_or_defer_email(
                            to_email=email,
                            subject=title,
                            body_text=body,
                            audience=route_audience,
                            recipient_user_id=None,
                        )
                    )
            elif channel is NotificationChannel.SMS:
                if not context.tcpa_consent:
                    results.append(
                        {
                            "audience": route_audience.value,
                            "channel": channel.value,
                            "status": "deferred_tcpa_consent",
                            "detail": "SMS requires TCPA consent on the dispatch context.",
                        }
                    )
                elif not context.sms_phone:
                    results.append(
                        {
                            "audience": route_audience.value,
                            "channel": channel.value,
                            "status": "skipped_no_phone",
                            "detail": "No sms_phone on dispatch context.",
                        }
                    )
                else:
                    results.append(
                        {
                            "audience": route_audience.value,
                            "channel": channel.value,
                            "status": "deferred_sms_not_wired",
                            "detail": (
                                "Matrix v1 records SMS intent only; live SMS send "
                                "remains on dedicated delivery paths."
                            ),
                            "phone": context.sms_phone,
                        }
                    )
            elif channel is NotificationChannel.CRM_TASK:
                if not context.create_crm_tasks:
                    results.append(
                        {
                            "audience": route_audience.value,
                            "channel": channel.value,
                            "status": "skipped_disabled",
                        }
                    )
                    continue
                assignee = (
                    recipients["user_ids"][0]
                    if recipients["user_ids"]
                    else context.assigned_user_id
                )
                task = Task(
                    id=uuid.uuid4(),
                    organization_id=context.organization_id,
                    case_id=context.case_id,
                    title=f"Follow up: {title}",
                    description=body,
                    status=TaskStatus.OPEN,
                    priority=TaskPriority.MEDIUM,
                    assigned_user_id=assignee,
                    source_module=context.source_module,
                    source_event_id=context.entity_id,
                )
                self._session.add(task)
                await self._session.flush()
                results.append(
                    {
                        "audience": route_audience.value,
                        "channel": channel.value,
                        "status": "created",
                        "task_id": str(task.id),
                        "event_key": event_key,
                    }
                )
        return results

    async def _create_in_app(
        self,
        *,
        organization_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        title: str,
        body: str,
        category: NotificationCategory,
        context: MatrixDispatchContext,
        audience: NotificationAudience,
    ) -> dict[str, Any]:
        notification = Notification(
            organization_id=organization_id,
            recipient_user_id=recipient_user_id,
            title=title,
            body=body,
            category=category,
            entity_type=context.entity_type,
            entity_id=context.entity_id,
            source_module=context.source_module,
            action_url=context.action_url,
        )
        self._session.add(notification)
        await self._session.flush()
        return {
            "audience": audience.value,
            "channel": NotificationChannel.IN_APP.value,
            "status": "created",
            "notification_id": str(notification.id),
            "recipient_user_id": str(recipient_user_id),
        }

    async def _send_or_defer_email(
        self,
        *,
        to_email: str,
        subject: str,
        body_text: str,
        audience: NotificationAudience,
        recipient_user_id: uuid.UUID | None,
    ) -> dict[str, Any]:
        base: dict[str, Any] = {
            "audience": audience.value,
            "channel": NotificationChannel.EMAIL.value,
            "to": to_email,
            "recipient_user_id": str(recipient_user_id) if recipient_user_id else None,
        }
        try:
            require_email_delivery_ready()
        except EmailDeliveryNotReadyError as exc:
            base["status"] = "deferred_email_not_ready"
            base["blockers"] = list(exc.blockers)
            return base

        send_result = await send_email_message(
            EmailMessage(to=to_email, subject=subject, body_text=body_text)
        )
        base["status"] = "sent" if send_result.success else "failed"
        base["provider_message_id"] = send_result.provider_message_id
        base["error"] = send_result.error
        return base

    async def _resolve_audience(
        self,
        audience: NotificationAudience,
        context: MatrixDispatchContext,
    ) -> dict[str, Any]:
        if audience is NotificationAudience.PARTNER_SUCCESS:
            users = await self._users_with_roles(context.organization_id, _PARTNER_SUCCESS_ROLES)
            return {"user_ids": [u.id for u in users], "emails": []}
        if audience is NotificationAudience.PARTNER_SUCCESS_LEAD:
            users = await self._users_with_roles(
                context.organization_id, frozenset({UserRole.OWNER, UserRole.ADMIN})
            )
            return {"user_ids": [u.id for u in users[:1]], "emails": []}
        if audience is NotificationAudience.CREDIT_SPECIALIST:
            if context.assigned_user_id:
                return {"user_ids": [context.assigned_user_id], "emails": []}
            users = await self._users_with_roles(context.organization_id, _CREDIT_SPECIALIST_ROLES)
            return {"user_ids": [u.id for u in users], "emails": []}
        if audience is NotificationAudience.CASE_OWNER:
            if context.assigned_user_id:
                return {"user_ids": [context.assigned_user_id], "emails": []}
            return {
                "user_ids": [],
                "emails": [],
                "detail": "No assigned_user_id / case owner.",
            }
        if audience is NotificationAudience.REFERRING_LO:
            user_ids = [context.referring_lo_user_id] if context.referring_lo_user_id else []
            emails = (
                [context.referring_lo_email]
                if context.referring_lo_email and not context.referring_lo_user_id
                else []
            )
            return {"user_ids": user_ids, "emails": emails}
        if audience is NotificationAudience.BORROWER:
            user_ids = [context.borrower_user_id] if context.borrower_user_id else []
            emails = (
                [context.borrower_email]
                if context.borrower_email and not context.borrower_user_id
                else []
            )
            return {"user_ids": user_ids, "emails": emails}
        if audience is NotificationAudience.REALTOR:
            if context.realtor_user_id:
                return {"user_ids": [context.realtor_user_id], "emails": []}
            if context.realtor_email:
                return {"user_ids": [], "emails": [context.realtor_email]}
            return {
                "user_ids": [],
                "emails": [],
                "detail": "Realtor audience deferred until partner realm (LRP-301).",
            }
        if audience is NotificationAudience.PARTNER_AUTHORIZED:
            return {"user_ids": list(context.partner_user_ids), "emails": []}
        if audience in {NotificationAudience.ENG_ONCALL, NotificationAudience.OPS}:
            users = await self._users_with_roles(context.organization_id, _OPS_ROLES)
            return {"user_ids": [u.id for u in users], "emails": []}
        return {"user_ids": [], "emails": [], "detail": f"Unknown audience {audience}"}

    async def _users_with_roles(
        self,
        organization_id: uuid.UUID,
        roles: frozenset[UserRole],
    ) -> list[User]:
        result = await self._session.execute(
            select(User)
            .where(
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
                User.role.in_(tuple(roles)),
            )
            .order_by(User.created_at.asc(), User.id.asc())
        )
        return list(result.scalars().all())

    async def _get_user(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
