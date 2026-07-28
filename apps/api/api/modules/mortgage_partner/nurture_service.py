"""Partner nurture drip service — programs, enrollments, processing (LRP-206)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.email_delivery import (
    EmailDeliveryNotReadyError,
    EmailMessage,
    require_email_delivery_ready,
    send_email_message,
)
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.mortgage_partner.nurture_models import (
    NurtureAudience,
    NurtureChannel,
    NurtureEnrollmentStatus,
    NurtureLifecycleStage,
    PartnerNurtureDeliveryRun,
    PartnerNurtureEnrollment,
    PartnerNurtureProgram,
    PartnerNurtureStep,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_READ_ROLE,
    MORTGAGE_PARTNER_WRITE_ROLE,
)
from api.modules.mortgage_partner.schemas import (
    NurtureDeliveryProcessResponse,
    NurtureDeliveryRunResponse,
    NurtureEnrollmentCreate,
    NurtureEnrollmentResponse,
    NurtureEnrollmentUpdate,
    NurtureProgramResponse,
    NurtureStepResponse,
)
from api.modules.notifications.notification_matrix import advisory_footer

SCHEMA_VERSION = "partner-nurture.v1"
_ADVISORY = advisory_footer()

DEFAULT_LENDER_STEPS: list[dict[str, Any]] = [
    {
        "step_order": 1,
        "delay_days": 0,
        "channel": "email",
        "template_key": "email.partner.lead.thanks",
        "subject": "Helping you prepare more borrowers for financing conversations",
        "body_template": (
            "Hello {contact_name},\n\n"
            "Thank you for your interest in the Lending Readiness Partners Mortgage "
            "Readiness Partnership. We help more borrowers become lending ready through "
            "a staff-mediated process — never unsupervised filing.\n\n"
            "CTA: book a briefing.\n\n{footer}"
        ),
    },
    {
        "step_order": 2,
        "delay_days": 1,
        "channel": "email",
        "template_key": "email.partner.lead.kit",
        "subject": "What happens when a borrower isn’t ready yet?",
        "body_template": (
            "Hello {contact_name},\n\n"
            "When credit work is needed, borrowers often walk away. Our partnership keeps "
            "them engaged: referral → plan → updates → advisory Lending Ready signal → "
            "return to you. No outcome guarantees.\n\n{footer}"
        ),
    },
    {
        "step_order": 3,
        "delay_days": 3,
        "channel": "email",
        "template_key": "email.partner.lead.briefing",
        "subject": "Introducing our Mortgage Readiness Partnership",
        "body_template": (
            "Hello {contact_name},\n\n"
            "Partnership benefits: dedicated specialist support, borrower portal, and "
            "progress reports. Schedule a discovery call when you are ready.\n\n{footer}"
        ),
    },
    {
        "step_order": 4,
        "delay_days": 7,
        "channel": "email",
        "template_key": "email.partner.lead.retention",
        "subject": "Keep more clients from walking away",
        "body_template": (
            "Hello {contact_name},\n\n"
            "Relationship retention matters when credit work is needed. We share partner "
            "updates on a predictable rhythm so you stay informed.\n\n{footer}"
        ),
    },
    {
        "step_order": 5,
        "delay_days": 14,
        "channel": "email",
        "template_key": "email.partner.lead.close",
        "subject": "Let’s help more families become lending ready",
        "body_template": (
            "Hello {contact_name},\n\n"
            "Helping More Borrowers Become Lending Ready. Invite a pilot or briefing when "
            "it fits your calendar — or reply to exit this sequence.\n\n{footer}"
        ),
    },
]


class PartnerNurtureService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> PartnerNurtureService:
        return cls(session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, MORTGAGE_PARTNER_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view mortgage partner resources",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, MORTGAGE_PARTNER_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage mortgage partner resources",
            )

    def _program_to_response(
        self,
        program: PartnerNurtureProgram,
        steps: list[PartnerNurtureStep],
    ) -> NurtureProgramResponse:
        return NurtureProgramResponse(
            id=program.id,
            organization_id=program.organization_id,
            name=program.name,
            description=program.description,
            audience=program.audience.value,
            enrollment_lifecycle_stage=program.enrollment_lifecycle_stage.value,
            enabled=program.enabled,
            steps=[self._step_to_response(step) for step in steps],
            created_at=program.created_at,
            updated_at=program.updated_at,
        )

    def _step_to_response(self, step: PartnerNurtureStep) -> NurtureStepResponse:
        return NurtureStepResponse(
            id=step.id,
            program_id=step.program_id,
            step_order=step.step_order,
            delay_days=step.delay_days,
            channel=step.channel.value,
            template_key=step.template_key,
            subject=step.subject,
            body_template=step.body_template,
        )

    def _enrollment_to_response(
        self,
        enrollment: PartnerNurtureEnrollment,
    ) -> NurtureEnrollmentResponse:
        return NurtureEnrollmentResponse(
            id=enrollment.id,
            organization_id=enrollment.organization_id,
            program_id=enrollment.program_id,
            partnership_id=enrollment.partnership_id,
            contact_name=enrollment.contact_name,
            contact_email=enrollment.contact_email,
            contact_phone=enrollment.contact_phone,
            status=enrollment.status.value,
            current_step_order=enrollment.current_step_order,
            next_run_at=enrollment.next_run_at,
            enrolled_at=enrollment.enrolled_at,
            paused_at=enrollment.paused_at,
            completed_at=enrollment.completed_at,
            exited_at=enrollment.exited_at,
            exit_reason=enrollment.exit_reason,
            marketing_opt_in=enrollment.marketing_opt_in,
            tcpa_consent=enrollment.tcpa_consent,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at,
        )

    def _delivery_to_response(
        self,
        run: PartnerNurtureDeliveryRun,
    ) -> NurtureDeliveryRunResponse:
        return NurtureDeliveryRunResponse(
            id=run.id,
            organization_id=run.organization_id,
            enrollment_id=run.enrollment_id,
            program_id=run.program_id,
            step_id=run.step_id,
            channel=run.channel,
            status=run.status,
            schema_version=run.schema_version,
            attempted_at=run.attempted_at,
            payload=run.payload,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

    async def ensure_default_program(self, user: User) -> NurtureProgramResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        count = await self._session.execute(
            select(func.count())
            .select_from(PartnerNurtureProgram)
            .where(
                PartnerNurtureProgram.organization_id == organization_id,
                PartnerNurtureProgram.deleted_at.is_(None),
            )
        )
        if int(count.scalar_one()) == 0:
            program = PartnerNurtureProgram(
                id=uuid.uuid4(),
                organization_id=organization_id,
                name="Lender partnership drip",
                description=(
                    "5-step claim-safe lender nurture sequence (Section 14 / partner kit)."
                ),
                audience=NurtureAudience.LENDER,
                enrollment_lifecycle_stage=NurtureLifecycleStage.LEAD,
                enabled=True,
                created_by_id=user.id,
                updated_by_id=user.id,
            )
            self._session.add(program)
            await self._session.flush()
            for spec in DEFAULT_LENDER_STEPS:
                self._session.add(
                    PartnerNurtureStep(
                        id=uuid.uuid4(),
                        organization_id=organization_id,
                        program_id=program.id,
                        step_order=int(spec["step_order"]),
                        delay_days=int(spec["delay_days"]),
                        channel=NurtureChannel(spec["channel"]),
                        template_key=str(spec["template_key"]),
                        subject=str(spec["subject"]),
                        body_template=str(spec["body_template"]),
                    )
                )
            await self._session.commit()
        programs = await self.list_programs(user)
        return programs[0]

    async def list_programs(self, user: User) -> list[NurtureProgramResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        # Auto-seed defaults for empty orgs on first list (admin write not required to view)
        count = await self._session.execute(
            select(func.count())
            .select_from(PartnerNurtureProgram)
            .where(
                PartnerNurtureProgram.organization_id == organization_id,
                PartnerNurtureProgram.deleted_at.is_(None),
            )
        )
        if int(count.scalar_one()) == 0 and has_permission(user.role, MORTGAGE_PARTNER_WRITE_ROLE):
            await self.ensure_default_program(user)

        result = await self._session.execute(
            select(PartnerNurtureProgram)
            .where(
                PartnerNurtureProgram.organization_id == organization_id,
                PartnerNurtureProgram.deleted_at.is_(None),
            )
            .order_by(PartnerNurtureProgram.created_at.asc())
        )
        programs = list(result.scalars().all())
        responses: list[NurtureProgramResponse] = []
        for program in programs:
            steps_result = await self._session.execute(
                select(PartnerNurtureStep)
                .where(
                    PartnerNurtureStep.program_id == program.id,
                    PartnerNurtureStep.organization_id == organization_id,
                )
                .order_by(PartnerNurtureStep.step_order.asc())
            )
            responses.append(self._program_to_response(program, list(steps_result.scalars().all())))
        return responses

    async def list_enrollments(self, user: User) -> list[NurtureEnrollmentResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        result = await self._session.execute(
            select(PartnerNurtureEnrollment)
            .where(
                PartnerNurtureEnrollment.organization_id == organization_id,
                PartnerNurtureEnrollment.deleted_at.is_(None),
            )
            .order_by(PartnerNurtureEnrollment.enrolled_at.desc())
        )
        return [self._enrollment_to_response(row) for row in result.scalars().all()]

    async def create_enrollment(
        self,
        user: User,
        payload: NurtureEnrollmentCreate,
    ) -> NurtureEnrollmentResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        program = await self._get_program(payload.program_id, organization_id)
        if program is None:
            raise HTTPException(status_code=404, detail="Nurture program not found")
        if not program.enabled:
            raise HTTPException(status_code=400, detail="Nurture program is disabled")
        if not payload.marketing_opt_in:
            raise HTTPException(
                status_code=400,
                detail="marketing_opt_in is required to enroll in a nurture drip",
            )
        if not payload.contact_email and not payload.contact_phone:
            raise HTTPException(
                status_code=422,
                detail="contact_email or contact_phone is required",
            )

        now = datetime.now(UTC)
        first_step = await self._get_step(program.id, organization_id, 1)
        delay = first_step.delay_days if first_step else 0
        next_run = now + timedelta(days=max(delay, 0))
        enrollment = PartnerNurtureEnrollment(
            id=uuid.uuid4(),
            organization_id=organization_id,
            program_id=program.id,
            partnership_id=payload.partnership_id,
            contact_name=payload.contact_name,
            contact_email=str(payload.contact_email) if payload.contact_email else None,
            contact_phone=payload.contact_phone,
            status=NurtureEnrollmentStatus.ACTIVE,
            current_step_order=1,
            next_run_at=next_run,
            enrolled_at=now,
            marketing_opt_in=payload.marketing_opt_in,
            tcpa_consent=payload.tcpa_consent,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        self._session.add(enrollment)
        await self._session.commit()
        await self._session.refresh(enrollment)
        return self._enrollment_to_response(enrollment)

    async def update_enrollment(
        self,
        user: User,
        enrollment_id: uuid.UUID,
        payload: NurtureEnrollmentUpdate,
    ) -> NurtureEnrollmentResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        enrollment = await self._get_enrollment(enrollment_id, organization_id)
        if enrollment is None:
            raise HTTPException(status_code=404, detail="Nurture enrollment not found")

        now = datetime.now(UTC)
        data = payload.model_dump(exclude_unset=True)
        if "marketing_opt_in" in data and data["marketing_opt_in"] is False:
            enrollment.marketing_opt_in = False
            enrollment.status = NurtureEnrollmentStatus.EXITED
            enrollment.exited_at = now
            enrollment.exit_reason = "marketing_opt_out"
            enrollment.next_run_at = None
        if "tcpa_consent" in data and data["tcpa_consent"] is not None:
            enrollment.tcpa_consent = data["tcpa_consent"]
        if "status" in data and data["status"] is not None:
            new_status = NurtureEnrollmentStatus(data["status"])
            enrollment.status = new_status
            if new_status is NurtureEnrollmentStatus.PAUSED:
                enrollment.paused_at = now
                enrollment.next_run_at = None
            elif new_status is NurtureEnrollmentStatus.ACTIVE:
                enrollment.paused_at = None
                if enrollment.next_run_at is None:
                    enrollment.next_run_at = now
            elif new_status is NurtureEnrollmentStatus.EXITED:
                enrollment.exited_at = now
                enrollment.exit_reason = data.get("exit_reason") or "manual_exit"
                enrollment.next_run_at = None
            elif new_status is NurtureEnrollmentStatus.COMPLETED:
                enrollment.completed_at = now
                enrollment.next_run_at = None
        if "exit_reason" in data and data["exit_reason"] is not None:
            enrollment.exit_reason = data["exit_reason"]
        enrollment.updated_by_id = user.id
        await self._session.commit()
        await self._session.refresh(enrollment)
        return self._enrollment_to_response(enrollment)

    async def process_due(self, user: User) -> NurtureDeliveryProcessResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        runs = await self._process_due_internal(organization_id=organization_id)
        await self._session.commit()
        return NurtureDeliveryProcessResponse(
            processed_count=len(runs),
            runs=[self._delivery_to_response(run) for run in runs],
        )

    async def list_deliveries(
        self,
        user: User,
        *,
        enrollment_id: uuid.UUID | None = None,
    ) -> list[NurtureDeliveryRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        stmt = (
            select(PartnerNurtureDeliveryRun)
            .where(PartnerNurtureDeliveryRun.organization_id == organization_id)
            .order_by(PartnerNurtureDeliveryRun.attempted_at.desc())
            .limit(100)
        )
        if enrollment_id is not None:
            stmt = stmt.where(PartnerNurtureDeliveryRun.enrollment_id == enrollment_id)
        result = await self._session.execute(stmt)
        return [self._delivery_to_response(row) for row in result.scalars().all()]

    async def _process_due_internal(
        self,
        *,
        organization_id: uuid.UUID,
        now: datetime | None = None,
    ) -> list[PartnerNurtureDeliveryRun]:
        clock = now or datetime.now(UTC)
        if clock.tzinfo is None:
            clock = clock.replace(tzinfo=UTC)
        result = await self._session.execute(
            select(PartnerNurtureEnrollment).where(
                PartnerNurtureEnrollment.organization_id == organization_id,
                PartnerNurtureEnrollment.deleted_at.is_(None),
                PartnerNurtureEnrollment.status == NurtureEnrollmentStatus.ACTIVE,
                PartnerNurtureEnrollment.next_run_at.is_not(None),
                PartnerNurtureEnrollment.next_run_at <= clock,
            )
        )
        runs: list[PartnerNurtureDeliveryRun] = []
        for enrollment in result.scalars().all():
            run = await self._process_enrollment(enrollment, now=clock)
            if run is not None:
                runs.append(run)
        return runs

    async def _process_enrollment(
        self,
        enrollment: PartnerNurtureEnrollment,
        *,
        now: datetime,
    ) -> PartnerNurtureDeliveryRun | None:
        if not enrollment.marketing_opt_in:
            enrollment.status = NurtureEnrollmentStatus.EXITED
            enrollment.exited_at = now
            enrollment.exit_reason = "marketing_opt_out"
            enrollment.next_run_at = None
            await self._session.flush()
            return None

        program = await self._get_program(enrollment.program_id, enrollment.organization_id)
        if program is None or not program.enabled:
            enrollment.status = NurtureEnrollmentStatus.PAUSED
            enrollment.paused_at = now
            enrollment.next_run_at = None
            await self._session.flush()
            return None

        step = await self._get_step(
            enrollment.program_id,
            enrollment.organization_id,
            enrollment.current_step_order,
        )
        if step is None:
            enrollment.status = NurtureEnrollmentStatus.COMPLETED
            enrollment.completed_at = now
            enrollment.next_run_at = None
            await self._session.flush()
            return None

        existing = await self._find_delivery(enrollment.id, step.id)
        if existing is not None:
            await self._advance(enrollment, now=now)
            return existing

        delivery_status, payload = await self._deliver_step(enrollment, step)
        run = PartnerNurtureDeliveryRun(
            id=uuid.uuid4(),
            organization_id=enrollment.organization_id,
            enrollment_id=enrollment.id,
            program_id=enrollment.program_id,
            step_id=step.id,
            channel=step.channel.value,
            status=delivery_status,
            schema_version=SCHEMA_VERSION,
            attempted_at=now,
            payload={
                **payload,
                "template_key": step.template_key,
                "step_order": step.step_order,
                "claim_safety": {
                    "auto_filing": False,
                    "underwriting_decision": False,
                    "advisory_footer": _ADVISORY,
                },
            },
        )
        self._session.add(run)
        await self._session.flush()
        await self._advance(enrollment, now=now)
        return run

    async def _deliver_step(
        self,
        enrollment: PartnerNurtureEnrollment,
        step: PartnerNurtureStep,
    ) -> tuple[str, dict[str, Any]]:
        body = step.body_template.format(
            contact_name=enrollment.contact_name,
            footer=_ADVISORY,
        )
        if step.channel is NurtureChannel.EMAIL:
            if not enrollment.contact_email:
                return "skipped_no_email", {"detail": "Enrollment has no contact_email"}
            if not enrollment.marketing_opt_in:
                return "skipped_opt_out", {"detail": "Marketing opt-in is false"}
            try:
                require_email_delivery_ready()
            except EmailDeliveryNotReadyError as exc:
                return "deferred_email_not_ready", {"blockers": list(exc.blockers)}
            send_result = await send_email_message(
                EmailMessage(
                    to=enrollment.contact_email,
                    subject=step.subject,
                    body_text=body,
                )
            )
            return (
                "sent" if send_result.success else "failed",
                {
                    "to": enrollment.contact_email,
                    "subject": step.subject,
                    "provider_message_id": send_result.provider_message_id,
                    "error": send_result.error,
                },
            )
        if step.channel is NurtureChannel.SMS:
            if not enrollment.tcpa_consent:
                return "deferred_tcpa_consent", {
                    "detail": "SMS requires TCPA consent on the enrollment."
                }
            if not enrollment.contact_phone:
                return "skipped_no_phone", {"detail": "Enrollment has no contact_phone"}
            return "deferred_sms_not_wired", {
                "detail": (
                    "Nurture v1 records SMS intent only; live SMS stays on dedicated "
                    "delivery paths."
                ),
                "phone": enrollment.contact_phone,
            }
        return "skipped_unsupported_channel", {"channel": step.channel.value}

    async def _advance(
        self,
        enrollment: PartnerNurtureEnrollment,
        *,
        now: datetime,
    ) -> None:
        next_order = enrollment.current_step_order + 1
        next_step = await self._get_step(
            enrollment.program_id,
            enrollment.organization_id,
            next_order,
        )
        if next_step is None:
            enrollment.status = NurtureEnrollmentStatus.COMPLETED
            enrollment.completed_at = now
            enrollment.next_run_at = None
        else:
            enrollment.current_step_order = next_order
            # delay_days is relative to enrollment start (partner-kit cadence).
            scheduled = enrollment.enrolled_at + timedelta(days=max(next_step.delay_days, 0))
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=UTC)
            enrollment.next_run_at = scheduled if scheduled > now else now
        await self._session.flush()

    async def _get_program(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> PartnerNurtureProgram | None:
        result = await self._session.execute(
            select(PartnerNurtureProgram).where(
                PartnerNurtureProgram.id == program_id,
                PartnerNurtureProgram.organization_id == organization_id,
                PartnerNurtureProgram.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def _get_step(
        self,
        program_id: uuid.UUID,
        organization_id: uuid.UUID,
        step_order: int,
    ) -> PartnerNurtureStep | None:
        result = await self._session.execute(
            select(PartnerNurtureStep).where(
                PartnerNurtureStep.program_id == program_id,
                PartnerNurtureStep.organization_id == organization_id,
                PartnerNurtureStep.step_order == step_order,
            )
        )
        return result.scalar_one_or_none()

    async def _get_enrollment(
        self,
        enrollment_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> PartnerNurtureEnrollment | None:
        result = await self._session.execute(
            select(PartnerNurtureEnrollment).where(
                PartnerNurtureEnrollment.id == enrollment_id,
                PartnerNurtureEnrollment.organization_id == organization_id,
                PartnerNurtureEnrollment.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def _find_delivery(
        self,
        enrollment_id: uuid.UUID,
        step_id: uuid.UUID,
    ) -> PartnerNurtureDeliveryRun | None:
        result = await self._session.execute(
            select(PartnerNurtureDeliveryRun).where(
                PartnerNurtureDeliveryRun.enrollment_id == enrollment_id,
                PartnerNurtureDeliveryRun.step_id == step_id,
            )
        )
        return result.scalar_one_or_none()
