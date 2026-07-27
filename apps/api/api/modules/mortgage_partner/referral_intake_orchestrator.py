"""Referral intake orchestrator — post-accept assignment + notify drafts (LRP-201)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.mortgage_partner.models import PartnerReferralIntakeRun
from api.modules.mortgage_partner.referral_intake_orchestrator_models import (
    PartnerReferralIntakeOrchestratorRun,
)
from api.modules.notifications.notification_matrix import (
    NotificationMatrixEvent,
    advisory_footer,
)
from api.modules.notifications.notification_matrix_service import (
    MatrixDispatchContext,
    NotificationMatrixDispatcher,
)
from api.modules.tasks.models import Task, TaskPriority, TaskStatus

SCHEMA_VERSION = "referral-intake-orchestrator.v1"

_ASSIGNABLE_ROLES = frozenset(
    {
        UserRole.CASE_MANAGER,
        UserRole.ADMIN,
        UserRole.OWNER,
    }
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

        matrix = NotificationMatrixDispatcher(self._session)
        footer = advisory_footer()
        matrix_context = MatrixDispatchContext(
            organization_id=intake.cro_organization_id,
            entity_type="referral_intake",
            entity_id=intake.id,
            title=f"Referral received — {intake.borrower_name}",
            body=(
                f"{intake.borrower_name} referred by {intake.lo_name} "
                f"({intake.partner_org_name}). Schedule consultation / assign specialist. "
                f"{footer}"
            ),
            action_url=f"/cases/{case.id}",
            case_id=case.id,
            assigned_user_id=assigned.id if assigned else None,
            referring_lo_email=intake.lo_email,
            referring_lo_name=intake.lo_name,
            borrower_email=intake.borrower_email,
            borrower_name=intake.borrower_name,
            source_module="mortgage_partner.referral_intake_orchestrator",
            create_crm_tasks=False,
        )
        submitted = await matrix.dispatch(
            NotificationMatrixEvent.REFERRAL_SUBMITTED,
            matrix_context,
        )
        steps.append(
            _step(
                key="matrix_referral_submitted",
                status=submitted.status,
                detail="Notification matrix v1 fan-out for referral_submitted.",
                dispatch_id=str(submitted.id),
            )
        )
        if assigned is not None:
            assigned_ctx = MatrixDispatchContext(
                organization_id=intake.cro_organization_id,
                entity_type="referral_intake",
                entity_id=intake.id,
                title=f"Referral assigned — {intake.borrower_name}",
                body=(
                    f"Case assigned to {assigned.email}. "
                    f"Borrower: {intake.borrower_name}. {footer}"
                ),
                action_url=f"/cases/{case.id}",
                case_id=case.id,
                assigned_user_id=assigned.id,
                referring_lo_email=intake.lo_email,
                referring_lo_name=intake.lo_name,
                source_module="mortgage_partner.referral_intake_orchestrator",
                create_crm_tasks=False,
            )
            assigned_run = await matrix.dispatch(
                NotificationMatrixEvent.REFERRAL_ASSIGNED,
                assigned_ctx,
            )
            steps.append(
                _step(
                    key="matrix_referral_assigned",
                    status=assigned_run.status,
                    detail="Notification matrix v1 fan-out for referral_assigned.",
                    dispatch_id=str(assigned_run.id),
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
