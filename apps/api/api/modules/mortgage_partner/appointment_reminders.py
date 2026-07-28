"""Appointment reminder processor (LRP-205)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.mortgage_partner.appointment_models import (
    AppointmentReminderOffset,
    AppointmentReminderRun,
    CrmAppointment,
    CrmAppointmentStatus,
)
from api.modules.notifications.notification_matrix import (
    NotificationMatrixEvent,
    advisory_footer,
)
from api.modules.notifications.notification_matrix_service import (
    MatrixDispatchContext,
    NotificationMatrixDispatcher,
)

SCHEMA_VERSION = "appointment-reminders.v1"

_OFFSET_TO_EVENT = {
    AppointmentReminderOffset.T24H: NotificationMatrixEvent.APPOINTMENT_REMINDER_T24H,
    AppointmentReminderOffset.T1H: NotificationMatrixEvent.APPOINTMENT_REMINDER_T1H,
}

_OFFSET_WINDOWS = {
    AppointmentReminderOffset.T24H: timedelta(hours=24),
    AppointmentReminderOffset.T1H: timedelta(hours=1),
}


class AppointmentReminderProcessor:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._matrix = NotificationMatrixDispatcher(session)

    async def process_due(
        self,
        *,
        organization_id: uuid.UUID,
        now: datetime | None = None,
        triggered_by_user_id: uuid.UUID | None = None,
    ) -> list[AppointmentReminderRun]:
        clock = now or datetime.now(UTC)
        if clock.tzinfo is None:
            clock = clock.replace(tzinfo=UTC)

        result = await self._session.execute(
            select(CrmAppointment).where(
                CrmAppointment.organization_id == organization_id,
                CrmAppointment.deleted_at.is_(None),
                CrmAppointment.status == CrmAppointmentStatus.SCHEDULED,
                CrmAppointment.starts_at > clock,
            )
        )
        appointments = list(result.scalars().all())
        runs: list[AppointmentReminderRun] = []
        for appointment in appointments:
            for offset in (AppointmentReminderOffset.T24H, AppointmentReminderOffset.T1H):
                if not self._is_due(appointment, offset=offset, now=clock):
                    continue
                existing = await self._find_run(appointment.id, offset)
                if existing is not None:
                    runs.append(existing)
                    continue
                runs.append(
                    await self._dispatch_reminder(
                        appointment,
                        offset=offset,
                        now=clock,
                        triggered_by_user_id=triggered_by_user_id,
                    )
                )
        return runs

    def _is_due(
        self,
        appointment: CrmAppointment,
        *,
        offset: AppointmentReminderOffset,
        now: datetime,
    ) -> bool:
        window = _OFFSET_WINDOWS[offset]
        due_at = appointment.starts_at - window
        return due_at <= now < appointment.starts_at

    async def _find_run(
        self,
        appointment_id: uuid.UUID,
        offset: AppointmentReminderOffset,
    ) -> AppointmentReminderRun | None:
        result = await self._session.execute(
            select(AppointmentReminderRun).where(
                AppointmentReminderRun.appointment_id == appointment_id,
                AppointmentReminderRun.offset_key == offset.value,
            )
        )
        return result.scalar_one_or_none()

    async def _dispatch_reminder(
        self,
        appointment: CrmAppointment,
        *,
        offset: AppointmentReminderOffset,
        now: datetime,
        triggered_by_user_id: uuid.UUID | None,
    ) -> AppointmentReminderRun:
        footer = advisory_footer()
        when_label = appointment.starts_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")
        title = f"Reminder — {appointment.title}"
        body = (
            f"Your consultation with Lending Readiness Partners is scheduled for {when_label}. "
            "We'll review education and next steps toward your next financing conversation. "
            f"{footer}"
        )
        if appointment.meeting_url:
            body = f"{body}\nJoin: {appointment.meeting_url}"

        event = _OFFSET_TO_EVENT[offset]
        # Unique entity_type per offset so matrix idempotency does not collide.
        entity_type = f"appointment_reminder_{offset.value}"
        dispatch = await self._matrix.dispatch(
            event,
            MatrixDispatchContext(
                organization_id=appointment.organization_id,
                entity_type=entity_type,
                entity_id=appointment.id,
                title=title,
                body=body,
                action_url="/crm/calendar",
                case_id=appointment.case_id,
                assigned_user_id=appointment.owner_user_id,
                referring_lo_email=appointment.referring_lo_email,
                referring_lo_name=appointment.referring_lo_name,
                borrower_email=appointment.borrower_email,
                borrower_name=appointment.borrower_name,
                tcpa_consent=appointment.tcpa_consent,
                sms_phone=appointment.borrower_phone,
                triggered_by_user_id=triggered_by_user_id,
                source_module="mortgage_partner.appointment_reminders",
                create_crm_tasks=False,
            ),
        )

        run = AppointmentReminderRun(
            id=uuid.uuid4(),
            organization_id=appointment.organization_id,
            appointment_id=appointment.id,
            offset_key=offset.value,
            status="completed",
            schema_version=SCHEMA_VERSION,
            matrix_dispatch_id=dispatch.id,
            started_at=now,
            completed_at=datetime.now(UTC),
            payload={
                "title": title,
                "offset": offset.value,
                "appointment_starts_at": appointment.starts_at.isoformat(),
                "tcpa_consent": appointment.tcpa_consent,
                "matrix_event": event.value,
                "matrix_dispatch_id": str(dispatch.id),
                "claim_safety": {
                    "auto_filing": False,
                    "underwriting_decision": False,
                    "advisory_footer": footer,
                },
            },
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def list_runs(
        self,
        *,
        organization_id: uuid.UUID,
        appointment_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[AppointmentReminderRun]:
        stmt = (
            select(AppointmentReminderRun)
            .where(AppointmentReminderRun.organization_id == organization_id)
            .order_by(AppointmentReminderRun.started_at.desc())
            .limit(limit)
        )
        if appointment_id is not None:
            stmt = stmt.where(AppointmentReminderRun.appointment_id == appointment_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
