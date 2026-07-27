"""Referral intake orchestrator — post-accept assignment + notify drafts (LRP-201)."""

from __future__ import annotations

import uuid
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
from api.modules.cases.models import Case
from api.modules.mortgage_partner.models import PartnerReferralIntakeRun
from api.modules.mortgage_partner.referral_intake_orchestrator_models import (
    PartnerReferralIntakeOrchestratorRun,
)
from api.modules.notifications.models import Notification, NotificationCategory
from api.modules.tasks.models import Task, TaskPriority, TaskStatus

SCHEMA_VERSION = "referral-intake-orchestrator.v1"

_ASSIGNABLE_ROLES = frozenset(
    {
        UserRole.CASE_MANAGER,
        UserRole.ADMIN,
        UserRole.OWNER,
    }
)

_ADVISORY_FOOTER = (
    "This message is operational only — not an underwriting decision, loan approval, "
    "or guarantee of funding."
)


def _step(
    *,
    key: str,
    status: str,
    detail: str,
    **extra: Any,
) -> dict[str, Any]:
    return {"key": key, "status": status, "detail": detail, **extra}


class ReferralIntakeOrchestrator:
    """Runs after accepted/duplicate_review web intake (not quarantined)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _list_assignable_users(self, organization_id: uuid.UUID) -> list[User]:
        result = await self._session.execute(
            select(User)
            .where(
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
                User.role.in_(tuple(_ASSIGNABLE_ROLES)),
            )
            .order_by(User.created_at.asc(), User.id.asc())
        )
        return list(result.scalars().all())

    async def _last_assigned_user_id(self, organization_id: uuid.UUID) -> uuid.UUID | None:
        result = await self._session.execute(
            select(PartnerReferralIntakeOrchestratorRun.assigned_user_id)
            .where(
                PartnerReferralIntakeOrchestratorRun.organization_id == organization_id,
                PartnerReferralIntakeOrchestratorRun.assigned_user_id.is_not(None),
            )
            .order_by(PartnerReferralIntakeOrchestratorRun.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    def _pick_assignee(
        self,
        candidates: list[User],
        *,
        last_assigned_id: uuid.UUID | None,
    ) -> User | None:
        if not candidates:
            return None
        if last_assigned_id is None:
            return candidates[0]
        ids = [user.id for user in candidates]
        try:
            index = ids.index(last_assigned_id)
            return candidates[(index + 1) % len(candidates)]
        except ValueError:
            return candidates[0]

    async def _maybe_send_email(
        self,
        *,
        to_email: str,
        subject: str,
        body: str,
    ) -> dict[str, Any]:
        draft = {
            "to": to_email,
            "subject": subject,
            "body": body,
        }
        try:
            require_email_delivery_ready()
        except EmailDeliveryNotReadyError as exc:
            return {
                **draft,
                "delivery_status": "deferred_email_not_ready",
                "blockers": list(exc.blockers),
            }

        result = await send_email_message(
            EmailMessage(to=to_email, subject=subject, body_text=body),
        )
        return {
            **draft,
            "delivery_status": "sent" if result.success else "failed",
            "provider_message_id": result.provider_message_id,
            "error": result.error,
        }

    async def run_for_intake(
        self,
        *,
        intake: PartnerReferralIntakeRun,
        case: Case,
        intake_task: Task | None,
    ) -> PartnerReferralIntakeOrchestratorRun:
        now = datetime.now(UTC)
        steps: list[dict[str, Any]] = []
        assigned: User | None = None

        candidates = await self._list_assignable_users(intake.cro_organization_id)
        last_id = await self._last_assigned_user_id(intake.cro_organization_id)
        assigned = self._pick_assignee(candidates, last_assigned_id=last_id)

        if assigned is None:
            steps.append(
                _step(
                    key="assign_case_manager",
                    status="skipped_no_assignees",
                    detail=(
                        "No case_manager/admin/owner users available — "
                        "create an Unassigned referral ops task."
                    ),
                )
            )
            unassigned = Task(
                id=uuid.uuid4(),
                organization_id=intake.cro_organization_id,
                case_id=case.id,
                title="Unassigned referral — configure assignment pool",
                description=(
                    f"Web intake {intake.id} could not round-robin assign a case manager. "
                    "Add staff with case_manager/admin/owner roles."
                ),
                status=TaskStatus.OPEN,
                priority=TaskPriority.HIGH,
                source_module="mortgage_partner.referral_intake_orchestrator",
                source_event_id=intake.id,
            )
            self._session.add(unassigned)
            await self._session.flush()
            steps.append(
                _step(
                    key="unassigned_ops_task",
                    status="created",
                    detail="Created high-priority ops task for missing assignees.",
                    task_id=str(unassigned.id),
                )
            )
        else:
            case.assigned_to_id = assigned.id
            if intake_task is not None:
                intake_task.assigned_user_id = assigned.id
            steps.append(
                _step(
                    key="assign_case_manager",
                    status="assigned",
                    detail=f"Round-robin assigned to {assigned.email}",
                    assigned_user_id=str(assigned.id),
                    assigned_email=assigned.email,
                )
            )

            notification = Notification(
                organization_id=intake.cro_organization_id,
                recipient_user_id=assigned.id,
                title="New partner web referral",
                body=(
                    f"{intake.borrower_name} referred by {intake.lo_name} "
                    f"({intake.partner_org_name}). Assign specialist / schedule consultation. "
                    f"{_ADVISORY_FOOTER}"
                ),
                category=NotificationCategory.WORKFLOW,
                entity_type="case",
                entity_id=case.id,
                source_module="mortgage_partner.referral_intake_orchestrator",
                action_url=f"/cases/{case.id}",
            )
            self._session.add(notification)
            await self._session.flush()
            steps.append(
                _step(
                    key="notify_assignee",
                    status="created",
                    detail="In-app workflow notification created for assignee.",
                    notification_id=str(notification.id),
                )
            )

        consult_task = Task(
            id=uuid.uuid4(),
            organization_id=intake.cro_organization_id,
            case_id=case.id,
            title="Offer / schedule consultation",
            description=(
                f"Follow up with {intake.borrower_name} to schedule a consultation. "
                f"Referrer LO: {intake.lo_name} <{intake.lo_email}>."
            ),
            status=TaskStatus.OPEN,
            priority=TaskPriority.MEDIUM,
            assigned_user_id=assigned.id if assigned else None,
            source_module="mortgage_partner.referral_intake_orchestrator",
            source_event_id=intake.id,
        )
        self._session.add(consult_task)
        await self._session.flush()
        steps.append(
            _step(
                key="schedule_consultation_task",
                status="created",
                detail="Created consultation scheduling task.",
                task_id=str(consult_task.id),
            )
        )

        referrer_body = (
            f"Hello {intake.lo_name},\n\n"
            f"Thank you for referring {intake.borrower_name}. We received the referral "
            f"and our team will follow up.\n\n"
            f"{_ADVISORY_FOOTER}\n"
        )
        referrer_email = await self._maybe_send_email(
            to_email=intake.lo_email,
            subject=f"Referral received — {intake.borrower_name}",
            body=referrer_body,
        )
        steps.append(
            _step(
                key="thank_you_referrer",
                status=str(referrer_email["delivery_status"]),
                detail="Thank-you email to referring LO (claim-safe).",
                email=referrer_email,
            )
        )

        if intake.borrower_email:
            borrower_body = (
                f"Hello {intake.borrower_name},\n\n"
                "Thank you — we received your referral and will be in touch with next "
                "steps for your lending-readiness consultation.\n\n"
                f"{_ADVISORY_FOOTER}\n"
            )
            borrower_email = await self._maybe_send_email(
                to_email=intake.borrower_email,
                subject="We received your referral",
                body=borrower_body,
            )
            steps.append(
                _step(
                    key="thank_you_borrower",
                    status=str(borrower_email["delivery_status"]),
                    detail="Thank-you / expectations email to borrower (claim-safe).",
                    email=borrower_email,
                )
            )
        else:
            steps.append(
                _step(
                    key="thank_you_borrower",
                    status="skipped_no_email",
                    detail="Borrower email not provided — skipped thank-you email.",
                )
            )

        steps.append(
            _step(
                key="ack_sla_timer",
                status="started",
                detail="Acknowledgement SLA timer started at orchestrator completion.",
                started_at=now.isoformat(),
            )
        )

        run = PartnerReferralIntakeOrchestratorRun(
            id=uuid.uuid4(),
            organization_id=intake.cro_organization_id,
            intake_run_id=intake.id,
            case_id=case.id,
            referral_id=intake.referral_id,
            assigned_user_id=assigned.id if assigned else None,
            status="completed",
            schema_version=SCHEMA_VERSION,
            started_at=now,
            completed_at=datetime.now(UTC),
            payload={
                "schema_version": SCHEMA_VERSION,
                "steps": steps,
                "claim_safety": {
                    "auto_filing": False,
                    "underwriting_decision": False,
                },
            },
        )
        self._session.add(run)
        await self._session.flush()
        return run
