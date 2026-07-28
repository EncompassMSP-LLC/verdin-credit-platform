"""Mortgage partner service — partnerships, members, referrals, milestones, access audits."""

import re
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.config import get_settings
from api.core.permissions import has_permission
from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_export import (
    CreditAnalysisExportFormat,
    build_credit_analysis_export,
)
from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun
from api.modules.accounts.credit_analysis_schemas import (
    CreditAnalysisRunResponse,
)
from api.modules.auth.models import User
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.clients.models import Client, ClientStatus
from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    OrgPartnership,
    OrgPartnershipMember,
    PartnerAccessAction,
    PartnerAccessAudit,
    PartnerContact,
    PartnerLoanMilestone,
    PartnerReferral,
    PartnerReferralIntakeRun,
    ReferralIntakeStatus,
    ReferralStatus,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_READ_ROLE,
    MORTGAGE_PARTNER_WRITE_ROLE,
    PARTNER_ROLE_PERMISSIONS,
)
from api.modules.mortgage_partner.referral_intake_orchestrator import ReferralIntakeOrchestrator
from api.modules.mortgage_partner.repository import MortgagePartnerRepository
from api.modules.mortgage_partner.schemas import (
    AppointmentReminderProcessResponse,
    AppointmentReminderRunResponse,
    CrmAppointmentCreate,
    CrmAppointmentResponse,
    CrmAppointmentUpdate,
    CrmAutomationRuleCreate,
    CrmAutomationRuleResponse,
    CrmAutomationRuleUpdate,
    DashboardSummaryResponse,
    MilestoneReplacePayload,
    MortgagePartnerStatusResponse,
    MortgageReadinessReportResponse,
    PartnerAccessAuditResponse,
    PartnerContactCreate,
    PartnerContactResponse,
    PartnerContactUpdate,
    PartnerLoanMilestoneResponse,
    PartnerReferralCreate,
    PartnerReferralResponse,
    PartnerReferralUpdate,
    PartnerRoleMatrixItem,
    PartnerRoleMatrixResponse,
    PartnershipCreate,
    PartnershipMemberCreate,
    PartnershipMemberResponse,
    PartnershipResponse,
    PipelineCardResponse,
    ReadinessBlocker,
    ReadinessDimension,
    ReadinessPriorityTask,
    ReadinessReportSummary,
    ReferralIntakeCreate,
    ReferralIntakeOrchestratorResponse,
    ReferralIntakeResponse,
    ReferralIntakeStatusResponse,
)
from api.modules.tasks.models import Task, TaskPriority, TaskStatus

_SSN_PATTERN = re.compile(r"\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b")

# Default milestone labels seeded on every new referral
_DEFAULT_MILESTONES = [
    ("Referral received", True),
    ("Intake complete", False),
    ("Readiness plan active", False),
    ("Docs package ready", False),
    ("Partner update cadence set", False),
]


class MortgagePartnerService:
    def __init__(self, repo: MortgagePartnerRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "MortgagePartnerService":
        return cls(MortgagePartnerRepository(session), session)

    # --- helpers ---

    def _partnership_response(
        self,
        row: OrgPartnership,
        *,
        primary_contact: PartnerContact | None = None,
        active_referral_count: int = 0,
    ) -> PartnershipResponse:
        primary_name = None
        primary_email = None
        if primary_contact is not None:
            primary_name = f"{primary_contact.first_name} {primary_contact.last_name}".strip()
            primary_email = primary_contact.email
        return PartnershipResponse(
            id=row.id,
            cro_organization_id=row.cro_organization_id,
            partner_organization_id=row.partner_organization_id,
            partner_type=row.partner_type,
            status=row.status,
            display_name=row.display_name,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
            primary_contact_name=primary_name,
            primary_contact_email=primary_email,
            active_referral_count=active_referral_count,
        )

    def _referral_response(
        self,
        row: PartnerReferral,
        *,
        client_display_name: str | None,
        milestones: list[PartnerLoanMilestone] | None = None,
    ) -> PartnerReferralResponse:
        milestone_responses = (
            [PartnerLoanMilestoneResponse.model_validate(m) for m in milestones]
            if milestones is not None
            else []
        )
        return PartnerReferralResponse(
            id=row.id,
            partnership_id=row.partnership_id,
            cro_organization_id=row.cro_organization_id,
            client_id=row.client_id,
            case_id=row.case_id,
            status=row.status,
            pipeline_stage=row.pipeline_stage,
            pipeline_stage_changed_at=row.pipeline_stage_changed_at,
            source_label=row.source_label,
            notes=row.notes,
            referred_by_user_id=row.referred_by_user_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
            client_display_name=client_display_name,
            milestones=milestone_responses,
        )

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

    async def _audit(
        self,
        *,
        cro_organization_id: uuid.UUID,
        actor: User,
        action: PartnerAccessAction,
        resource_type: str,
        resource_id: uuid.UUID | None = None,
        partnership_id: uuid.UUID | None = None,
        detail: str | None = None,
    ) -> None:
        await self._repo.create_access_audit(
            PartnerAccessAudit(
                id=uuid.uuid4(),
                cro_organization_id=cro_organization_id,
                partnership_id=partnership_id,
                actor_user_id=actor.id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=detail,
                occurred_at=datetime.now(UTC),
            )
        )

    async def _seed_default_milestones(
        self,
        referral_id: uuid.UUID,
        organization_id: uuid.UUID,
        created_by_id: uuid.UUID | None,
    ) -> list[PartnerLoanMilestone]:
        now = datetime.now(UTC)
        milestones = []
        for idx, (label, complete) in enumerate(_DEFAULT_MILESTONES):
            m = PartnerLoanMilestone(
                id=uuid.uuid4(),
                referral_id=referral_id,
                organization_id=organization_id,
                label=label,
                sort_order=idx,
                complete=complete,
                completed_at=now if complete else None,
            )
            if created_by_id is not None:
                apply_audit_on_create(m, created_by_id)
            milestones.append(m)
        return await self._repo.bulk_create_milestones(milestones)

    async def _require_partnership(
        self, partnership_id: uuid.UUID, cro_org_id: uuid.UUID
    ) -> OrgPartnership:
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
        return partnership

    async def _require_referral(
        self,
        referral_id: uuid.UUID,
        partnership_id: uuid.UUID,
        cro_org_id: uuid.UUID,
    ) -> PartnerReferral:
        referral = await self._repo.get_referral(referral_id, partnership_id, cro_org_id)
        if referral is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral not found",
            )
        return referral

    # --- public API ---

    def get_status(self, user: User) -> MortgagePartnerStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return MortgagePartnerStatusResponse(
            mortgage_partner_enabled=True,
            capabilities=[
                "partnerships",
                "partnership_members",
                "partner_contacts",
                "partner_referrals",
                "partner_access_audits",
                "partner_role_matrix",
                "partner_pipeline",
                "partner_milestones",
                "partner_readiness_report",
                "partner_readiness_export",
                "referral_web_intake",
                "referral_intake_orchestrator",
                "crm_automation_rules",
                "crm_appointments",
                "appointment_reminders",
                "partner_nurture_drip",
                "weekly_partner_digest",
                "realtor_partner_role",
                "realtor_portal_auth",
            ],
            deferred_capabilities=[
                "partner_jwt_realm",
                "cross_tenant_marketplace",
                "live_bureau_soft_pull",
                "unsupervised_filing",
                "custom_partner_domains",
            ],
        )

    def get_referral_intake_status(self) -> ReferralIntakeStatusResponse:
        settings = get_settings()
        blockers: list[str] = []
        if not settings.referral_intake_enabled:
            blockers.append("REFERRAL_INTAKE_ENABLED is false")
        if not settings.referral_intake_organization_slug.strip():
            blockers.append("REFERRAL_INTAKE_ORGANIZATION_SLUG is empty")
        return ReferralIntakeStatusResponse(
            referral_intake_enabled=settings.referral_intake_enabled and not blockers,
            organization_slug=settings.referral_intake_organization_slug or None,
            blockers=blockers,
        )

    async def submit_referral_intake(self, payload: ReferralIntakeCreate) -> ReferralIntakeResponse:
        """Public web-form intake — creates client/case/referral + ops task (no auth)."""
        settings = get_settings()
        status_info = self.get_referral_intake_status()
        if not status_info.referral_intake_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral intake is not enabled",
            )

        free_text = " ".join(
            part for part in (payload.known_gaps, payload.notes, payload.product_intent) if part
        )
        if _SSN_PATTERN.search(free_text):
            org = await self._repo.get_organization_by_slug(
                settings.referral_intake_organization_slug
            )
            if org is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Referral intake organization is not configured",
                )
            run = PartnerReferralIntakeRun(
                id=uuid.uuid4(),
                cro_organization_id=org.id,
                partnership_id=payload.partnership_id,
                status=ReferralIntakeStatus.QUARANTINED,
                partner_org_name=payload.partner_org_name.strip(),
                lo_name=payload.lo_name.strip(),
                lo_email=str(payload.lo_email).lower(),
                lo_phone=payload.lo_phone,
                borrower_name=payload.borrower_name.strip(),
                borrower_email=(
                    str(payload.borrower_email).lower() if payload.borrower_email else None
                ),
                borrower_phone=payload.borrower_phone,
                product_intent=payload.product_intent,
                known_gaps=payload.known_gaps,
                notes=payload.notes,
                consent_attested=payload.consent_attested,
                quarantine_reason="Possible SSN in free-text fields",
            )
            await self._repo.create_intake_run(run)
            await self._session.commit()
            return ReferralIntakeResponse(
                intake_id=run.id,
                status=run.status.value,
                partnership_id=None,
                referral_id=None,
                client_id=None,
                case_id=None,
                task_id=None,
                message=(
                    "Referral held for review — please remove sensitive identifiers "
                    "(e.g. SSN) and resubmit or contact the operations team."
                ),
                quarantine_reason=run.quarantine_reason,
            )

        org = await self._repo.get_organization_by_slug(settings.referral_intake_organization_slug)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Referral intake organization is not configured",
            )

        partnership: OrgPartnership | None = None
        if payload.partnership_id is not None:
            partnership = await self._repo.get_partnership(payload.partnership_id, org.id)
            if partnership is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Partnership not found for intake organization",
                )
        else:
            partnership = await self._repo.get_first_active_partnership(org.id)
            if partnership is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "No active partnership configured for web referral intake; "
                        "pass partnership_id or create a partnership"
                    ),
                )

        borrower_email = str(payload.borrower_email).lower() if payload.borrower_email else None
        borrower_phone = payload.borrower_phone.strip() if payload.borrower_phone else None

        existing = await self._repo.find_open_client_by_contact(
            org.id, email=borrower_email, phone=borrower_phone
        )
        duplicate = existing is not None

        client = existing
        if client is None:
            client = Client(
                id=uuid.uuid4(),
                organization_id=org.id,
                display_name=payload.borrower_name.strip(),
                email=borrower_email,
                phone=borrower_phone,
                status=ClientStatus.ACTIVE,
                notes=(
                    f"Created via partner web referral form. "
                    f"Partner: {payload.partner_org_name}; LO: {payload.lo_name}"
                ),
            )
            client = await self._repo.create_client(client)

        now = datetime.now(UTC)
        case = Case(
            id=uuid.uuid4(),
            organization_id=org.id,
            client_id=client.id,
            title=f"Partner referral — {payload.borrower_name.strip()}",
            client_name=payload.borrower_name.strip(),
            client_email=borrower_email,
            case_number=f"REF-{uuid.uuid4().hex[:8].upper()}",
            status=CaseStatus.OPEN,
            stage=CaseStage.INTAKE,
            priority=CasePriority.HIGH if duplicate else CasePriority.MEDIUM,
            summary=(
                f"Web referral from {payload.partner_org_name} / {payload.lo_name}. "
                f"Intent: {payload.product_intent or 'n/a'}. "
                "Advisory only — no underwriting decision."
            ),
            opened_at=now,
        )
        case = await self._repo.create_case(case)

        referral = PartnerReferral(
            id=uuid.uuid4(),
            partnership_id=partnership.id,
            cro_organization_id=org.id,
            client_id=client.id,
            case_id=case.id,
            status=ReferralStatus.NEW,
            pipeline_stage=LoanPipelineStage.REFERRED,
            pipeline_stage_changed_at=now,
            source_label=f"web_form:{payload.partner_org_name.strip()[:200]}",
            notes=self._format_intake_notes(payload),
            referred_by_user_id=None,
        )
        referral = await self._repo.create_referral(referral)
        await self._seed_default_milestones(referral.id, org.id, created_by_id=None)

        task = Task(
            id=uuid.uuid4(),
            organization_id=org.id,
            case_id=case.id,
            title=(
                "Review duplicate web referral"
                if duplicate
                else "New partner web referral — assign specialist"
            ),
            description=(
                f"Intake from {payload.lo_name} <{payload.lo_email}> at "
                f"{payload.partner_org_name}. Borrower: {payload.borrower_name}."
            ),
            status=TaskStatus.OPEN,
            priority=TaskPriority.HIGH if duplicate else TaskPriority.MEDIUM,
            source_module="mortgage_partner.referral_intake",
            source_event_id=referral.id,
        )
        self._session.add(task)
        await self._session.flush()

        intake_status = (
            ReferralIntakeStatus.DUPLICATE_REVIEW if duplicate else ReferralIntakeStatus.ACCEPTED
        )
        run = PartnerReferralIntakeRun(
            id=uuid.uuid4(),
            cro_organization_id=org.id,
            partnership_id=partnership.id,
            client_id=client.id,
            case_id=case.id,
            referral_id=referral.id,
            task_id=task.id,
            status=intake_status,
            partner_org_name=payload.partner_org_name.strip(),
            lo_name=payload.lo_name.strip(),
            lo_email=str(payload.lo_email).lower(),
            lo_phone=payload.lo_phone,
            borrower_name=payload.borrower_name.strip(),
            borrower_email=borrower_email,
            borrower_phone=borrower_phone,
            product_intent=payload.product_intent,
            known_gaps=payload.known_gaps,
            notes=payload.notes,
            consent_attested=payload.consent_attested,
        )
        await self._repo.create_intake_run(run)

        orchestrator = ReferralIntakeOrchestrator(self._session)
        orch_run = await orchestrator.run_for_intake(
            intake=run,
            case=case,
            intake_task=task,
        )
        await self._session.commit()

        return ReferralIntakeResponse(
            intake_id=run.id,
            status=run.status.value,
            partnership_id=partnership.id,
            referral_id=referral.id,
            client_id=client.id,
            case_id=case.id,
            task_id=task.id,
            message=(
                "Referral received. Our team will follow up — this is not an underwriting decision."
                if not duplicate
                else "Possible duplicate contact flagged for staff review."
            ),
            orchestrator_run_id=orch_run.id,
            assigned_user_id=orch_run.assigned_user_id,
        )

    async def get_referral_intake_orchestrator_run(
        self,
        user: User,
        intake_id: uuid.UUID,
    ) -> ReferralIntakeOrchestratorResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        from sqlalchemy import select

        from api.modules.mortgage_partner.referral_intake_orchestrator_models import (
            PartnerReferralIntakeOrchestratorRun,
        )

        result = await self._session.execute(
            select(PartnerReferralIntakeOrchestratorRun).where(
                PartnerReferralIntakeOrchestratorRun.intake_run_id == intake_id,
                PartnerReferralIntakeOrchestratorRun.organization_id == organization_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orchestrator run not found for this intake",
            )
        return ReferralIntakeOrchestratorResponse(
            id=row.id,
            intake_run_id=row.intake_run_id,
            case_id=row.case_id,
            referral_id=row.referral_id,
            assigned_user_id=row.assigned_user_id,
            status=row.status,
            schema_version=row.schema_version,
            started_at=row.started_at,
            completed_at=row.completed_at,
            payload=row.payload,
        )

    @staticmethod
    def _format_intake_notes(payload: ReferralIntakeCreate) -> str:
        lines = [
            f"LO: {payload.lo_name} <{payload.lo_email}>",
            f"LO phone: {payload.lo_phone or 'n/a'}",
            f"Partner org: {payload.partner_org_name}",
            f"Intent: {payload.product_intent or 'n/a'}",
            f"Known gaps: {payload.known_gaps or 'n/a'}",
            f"Notes: {payload.notes or 'n/a'}",
            "Consent attested: yes",
            "Source: public web form (LRP-103)",
        ]
        return "\n".join(lines)

    def get_role_matrix(self, user: User) -> PartnerRoleMatrixResponse:
        self._require_read(user)
        self._require_organization(user)
        return PartnerRoleMatrixResponse(
            roles=[
                PartnerRoleMatrixItem(role=role, permissions=sorted(perms))
                for role, perms in PARTNER_ROLE_PERMISSIONS.items()
            ]
        )

    async def create_partnership(
        self, user: User, payload: PartnershipCreate
    ) -> PartnershipResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)

        if payload.partner_organization_id == cro_org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partner organization must differ from the CRO organization",
            )

        partner_org = await self._repo.get_organization(payload.partner_organization_id)
        if partner_org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner organization not found",
            )

        existing = await self._repo.find_partnership_pair(
            cro_org_id, payload.partner_organization_id
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Partnership already exists for this partner organization",
            )

        partnership = OrgPartnership(
            id=uuid.uuid4(),
            cro_organization_id=cro_org_id,
            partner_organization_id=payload.partner_organization_id,
            partner_type=payload.partner_type,
            status=payload.status,
            display_name=payload.display_name.strip(),
            notes=payload.notes,
        )
        apply_audit_on_create(partnership, user.id)
        created = await self._repo.create_partnership(partnership)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.PARTNERSHIP_CREATE,
            resource_type="org_partnership",
            resource_id=created.id,
            partnership_id=created.id,
            detail=f"Linked partner org {payload.partner_organization_id}",
        )
        await self._session.commit()
        return self._partnership_response(created)

    async def list_partnerships(self, user: User) -> list[PartnershipResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        rows = await self._repo.list_partnerships(cro_org_id)
        partnership_ids = [row.id for row in rows]
        primaries = await self._repo.map_primary_contacts(cro_org_id, partnership_ids)
        counts = await self._repo.map_active_referral_counts(cro_org_id, partnership_ids)
        return [
            self._partnership_response(
                row,
                primary_contact=primaries.get(row.id),
                active_referral_count=counts.get(row.id, 0),
            )
            for row in rows
        ]

    async def get_partnership(self, user: User, partnership_id: uuid.UUID) -> PartnershipResponse:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        partnership = await self._require_partnership(partnership_id, cro_org_id)
        primaries = await self._repo.map_primary_contacts(cro_org_id, [partnership.id])
        counts = await self._repo.map_active_referral_counts(cro_org_id, [partnership.id])
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.PARTNERSHIP_VIEW,
            resource_type="org_partnership",
            resource_id=partnership.id,
            partnership_id=partnership.id,
        )
        await self._session.commit()
        return self._partnership_response(
            partnership,
            primary_contact=primaries.get(partnership.id),
            active_referral_count=counts.get(partnership.id, 0),
        )

    async def list_contacts(
        self, user: User, partnership_id: uuid.UUID
    ) -> list[PartnerContactResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        rows = await self._repo.list_contacts(partnership_id, cro_org_id)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.CONTACT_LIST,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail=f"count={len(rows)}",
        )
        await self._session.commit()
        return [PartnerContactResponse.model_validate(row) for row in rows]

    async def create_contact(
        self,
        user: User,
        partnership_id: uuid.UUID,
        payload: PartnerContactCreate,
    ) -> PartnerContactResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)

        if payload.user_id is not None:
            linked = await self._repo.get_user_in_org(payload.user_id, cro_org_id)
            if linked is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked user not found in organization",
                )

        if payload.is_primary:
            await self._repo.clear_primary_contacts(partnership_id, cro_org_id)

        contact = PartnerContact(
            id=uuid.uuid4(),
            partnership_id=partnership_id,
            cro_organization_id=cro_org_id,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=payload.email.strip() if payload.email else None,
            phone=payload.phone.strip() if payload.phone else None,
            job_title=payload.job_title.strip() if payload.job_title else None,
            contact_role=payload.contact_role,
            is_primary=payload.is_primary,
            is_active=payload.is_active,
            user_id=payload.user_id,
            notes=payload.notes,
        )
        apply_audit_on_create(contact, user.id)
        created = await self._repo.create_contact(contact)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.CONTACT_CREATE,
            resource_type="partner_contact",
            resource_id=created.id,
            partnership_id=partnership_id,
            detail=f"primary={payload.is_primary}",
        )
        await self._session.commit()
        return PartnerContactResponse.model_validate(created)

    async def update_contact(
        self,
        user: User,
        partnership_id: uuid.UUID,
        contact_id: uuid.UUID,
        payload: PartnerContactUpdate,
    ) -> PartnerContactResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        contact = await self._repo.get_contact(contact_id, partnership_id, cro_org_id)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

        fields = payload.model_fields_set
        if "user_id" in fields and payload.user_id is not None:
            linked = await self._repo.get_user_in_org(payload.user_id, cro_org_id)
            if linked is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked user not found in organization",
                )

        if "is_primary" in fields and payload.is_primary is True:
            await self._repo.clear_primary_contacts(
                partnership_id, cro_org_id, except_contact_id=contact.id
            )

        if "first_name" in fields and payload.first_name is not None:
            contact.first_name = payload.first_name.strip()
        if "last_name" in fields and payload.last_name is not None:
            contact.last_name = payload.last_name.strip()
        if "email" in fields:
            contact.email = payload.email.strip() if payload.email else None
        if "phone" in fields:
            contact.phone = payload.phone.strip() if payload.phone else None
        if "job_title" in fields:
            contact.job_title = payload.job_title.strip() if payload.job_title else None
        if "contact_role" in fields and payload.contact_role is not None:
            contact.contact_role = payload.contact_role
        if "is_primary" in fields and payload.is_primary is not None:
            contact.is_primary = payload.is_primary
        if "is_active" in fields and payload.is_active is not None:
            contact.is_active = payload.is_active
        if "user_id" in fields:
            contact.user_id = payload.user_id
        if "notes" in fields:
            contact.notes = payload.notes

        apply_audit_on_update(contact, user.id)
        updated = await self._repo.save_contact(contact)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.CONTACT_UPDATE,
            resource_type="partner_contact",
            resource_id=updated.id,
            partnership_id=partnership_id,
        )
        await self._session.commit()
        return PartnerContactResponse.model_validate(updated)

    async def add_member(
        self,
        user: User,
        partnership_id: uuid.UUID,
        payload: PartnershipMemberCreate,
    ) -> PartnershipMemberResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        partnership = await self._require_partnership(partnership_id, cro_org_id)

        target = await self._repo.get_user_in_org(payload.user_id, cro_org_id)
        if target is None:
            target = await self._repo.get_user_in_org(
                payload.user_id, partnership.partner_organization_id
            )
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in CRO or partner organization",
            )

        existing = await self._repo.get_member(partnership_id, payload.user_id, cro_org_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this partnership",
            )

        member = OrgPartnershipMember(
            id=uuid.uuid4(),
            partnership_id=partnership_id,
            organization_id=cro_org_id,
            user_id=payload.user_id,
            partner_role=payload.partner_role,
            is_active=payload.is_active,
        )
        apply_audit_on_create(member, user.id)
        created = await self._repo.create_member(member)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.MEMBER_CREATE,
            resource_type="org_partnership_member",
            resource_id=created.id,
            partnership_id=partnership_id,
            detail=f"role={payload.partner_role.value}",
        )
        await self._session.commit()
        return PartnershipMemberResponse.model_validate(created)

    async def list_members(
        self, user: User, partnership_id: uuid.UUID
    ) -> list[PartnershipMemberResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        rows = await self._repo.list_members(partnership_id, cro_org_id)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.MEMBER_LIST,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail=f"count={len(rows)}",
        )
        await self._session.commit()
        return [PartnershipMemberResponse.model_validate(row) for row in rows]

    async def create_referral(
        self,
        user: User,
        partnership_id: uuid.UUID,
        payload: PartnerReferralCreate,
    ) -> PartnerReferralResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)

        client = await self._repo.get_client_in_org(payload.client_id, cro_org_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found in organization",
            )

        if payload.case_id is not None:
            case = await self._repo.get_case_in_org(payload.case_id, cro_org_id)
            if case is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Case not found in organization",
                )
            if case.client_id != payload.client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Case does not belong to the referred client",
                )

        now = datetime.now(UTC)
        referral = PartnerReferral(
            id=uuid.uuid4(),
            partnership_id=partnership_id,
            cro_organization_id=cro_org_id,
            client_id=payload.client_id,
            case_id=payload.case_id,
            status=payload.status,
            pipeline_stage=payload.pipeline_stage,
            pipeline_stage_changed_at=now,
            source_label=payload.source_label,
            notes=payload.notes,
            referred_by_user_id=user.id,
        )
        apply_audit_on_create(referral, user.id)
        created = await self._repo.create_referral(referral)

        # Seed default milestone checklist
        milestones = await self._seed_default_milestones(created.id, cro_org_id, user.id)

        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_CREATE,
            resource_type="partner_referral",
            resource_id=created.id,
            partnership_id=partnership_id,
            detail=f"client_id={payload.client_id} stage={payload.pipeline_stage.value}",
        )
        await self._session.commit()
        return self._referral_response(
            created,
            client_display_name=client.display_name,
            milestones=milestones,
        )

    async def list_referrals(
        self, user: User, partnership_id: uuid.UUID
    ) -> list[PartnerReferralResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        rows = await self._repo.list_referrals(partnership_id, cro_org_id)
        names = await self._repo.map_client_display_names(
            cro_org_id,
            [row.client_id for row in rows],
        )
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_LIST,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail=f"count={len(rows)}",
        )
        await self._session.commit()
        return [
            self._referral_response(row, client_display_name=names.get(row.client_id))
            for row in rows
        ]

    async def get_referral(
        self,
        user: User,
        partnership_id: uuid.UUID,
        referral_id: uuid.UUID,
    ) -> PartnerReferralResponse:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referral = await self._require_referral(referral_id, partnership_id, cro_org_id)
        names = await self._repo.map_client_display_names(cro_org_id, [referral.client_id])
        milestones = await self._repo.list_milestones(referral.id, cro_org_id)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_VIEW,
            resource_type="partner_referral",
            resource_id=referral.id,
            partnership_id=partnership_id,
            detail=f"client_id={referral.client_id}",
        )
        await self._session.commit()
        return self._referral_response(
            referral,
            client_display_name=names.get(referral.client_id),
            milestones=milestones,
        )

    async def update_referral(
        self,
        user: User,
        partnership_id: uuid.UUID,
        referral_id: uuid.UUID,
        payload: PartnerReferralUpdate,
    ) -> PartnerReferralResponse:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referral = await self._require_referral(referral_id, partnership_id, cro_org_id)

        detail_parts: list[str] = []
        if payload.status is not None:
            detail_parts.append(f"status={referral.status.value}->{payload.status.value}")
            referral.status = payload.status

        if payload.pipeline_stage is not None and payload.pipeline_stage != referral.pipeline_stage:
            detail_parts.append(
                f"stage={referral.pipeline_stage.value}->{payload.pipeline_stage.value}"
            )
            referral.pipeline_stage = payload.pipeline_stage
            referral.pipeline_stage_changed_at = datetime.now(UTC)

        if payload.notes is not None:
            referral.notes = payload.notes

        apply_audit_on_update(referral, user.id)
        updated = await self._repo.save_referral(referral)
        names = await self._repo.map_client_display_names(cro_org_id, [updated.client_id])
        milestones = await self._repo.list_milestones(updated.id, cro_org_id)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_UPDATE,
            resource_type="partner_referral",
            resource_id=updated.id,
            partnership_id=partnership_id,
            detail="; ".join(detail_parts) or "no-op",
        )
        await self._session.commit()
        return self._referral_response(
            updated,
            client_display_name=names.get(updated.client_id),
            milestones=milestones,
        )

    # --- Pipeline board ---

    async def get_pipeline(
        self, user: User, partnership_id: uuid.UUID
    ) -> list[PipelineCardResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referrals = await self._repo.list_pipeline_referrals(partnership_id, cro_org_id)
        names = await self._repo.map_client_display_names(
            cro_org_id, [r.client_id for r in referrals]
        )
        now = datetime.now(UTC)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.PIPELINE_VIEW,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail=f"count={len(referrals)}",
        )
        await self._session.commit()

        cards = []
        for ref in referrals:
            changed_at = ref.pipeline_stage_changed_at
            days_in_stage = (now - changed_at).days if changed_at else 0
            cards.append(
                PipelineCardResponse(
                    referral_id=ref.id,
                    client_id=ref.client_id,
                    client_display_name=names.get(ref.client_id),
                    pipeline_stage=ref.pipeline_stage,
                    referral_status=ref.status,
                    days_in_stage=days_in_stage,
                    stage_changed_at=changed_at,
                    notes=ref.notes,
                    source_label=ref.source_label,
                )
            )
        return cards

    # --- Dashboard summary ---

    async def get_dashboard_summary(
        self, user: User, partnership_id: uuid.UUID
    ) -> DashboardSummaryResponse:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referrals = await self._repo.list_pipeline_referrals(partnership_id, cro_org_id)
        counts = self._repo.compute_dashboard_summary(referrals)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.PIPELINE_VIEW,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail="dashboard_summary",
        )
        await self._session.commit()
        return DashboardSummaryResponse(
            total_referrals=len(referrals),
            counts_by_stage=counts,
            near_ready_count=counts.get(LoanPipelineStage.NEAR_READY.value, 0),
            mortgage_ready_count=counts.get(LoanPipelineStage.MORTGAGE_READY.value, 0),
            in_underwriting_count=counts.get(LoanPipelineStage.IN_UNDERWRITING.value, 0),
            funded_count=counts.get(LoanPipelineStage.FUNDED.value, 0),
            declined_count=counts.get(LoanPipelineStage.DECLINED.value, 0),
        )

    # --- Milestones ---

    async def list_milestones(
        self, user: User, partnership_id: uuid.UUID, referral_id: uuid.UUID
    ) -> list[PartnerLoanMilestoneResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        await self._require_referral(referral_id, partnership_id, cro_org_id)
        rows = await self._repo.list_milestones(referral_id, cro_org_id)
        await self._session.commit()
        return [PartnerLoanMilestoneResponse.model_validate(m) for m in rows]

    async def replace_milestones(
        self,
        user: User,
        partnership_id: uuid.UUID,
        referral_id: uuid.UUID,
        payload: MilestoneReplacePayload,
    ) -> list[PartnerLoanMilestoneResponse]:
        self._require_write(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        await self._require_referral(referral_id, partnership_id, cro_org_id)

        await self._repo.soft_delete_milestones_for_referral(referral_id, cro_org_id)

        now = datetime.now(UTC)
        new_milestones: list[PartnerLoanMilestone] = []
        for item in payload.milestones:
            m = PartnerLoanMilestone(
                id=uuid.uuid4(),
                referral_id=referral_id,
                organization_id=cro_org_id,
                label=item.label,
                sort_order=item.sort_order,
                complete=item.complete,
                completed_at=now if item.complete else None,
            )
            apply_audit_on_create(m, user.id)
            new_milestones.append(m)

        created = await self._repo.bulk_create_milestones(new_milestones)

        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.MILESTONE_UPDATE,
            resource_type="partner_referral",
            resource_id=referral_id,
            partnership_id=partnership_id,
            detail=f"replaced={len(created)}",
        )
        await self._session.commit()
        return [PartnerLoanMilestoneResponse.model_validate(m) for m in created]

    # --- Readiness reports (slice 4) ---

    def _run_to_readiness_report(
        self,
        *,
        referral: PartnerReferral,
        run: CreditAnalysisRun,
        client_display_name: str | None,
        milestones: list[PartnerLoanMilestone],
    ) -> MortgageReadinessReportResponse:
        payload: dict[str, Any] = run.payload or {}
        disclaimer = payload.get("disclaimer") or ADVISORY_DISCLAIMER

        dimensions = [
            ReadinessDimension(
                key=d["key"],
                label=d["label"],
                score=d["score"],
                weight=d["weight"],
            )
            for d in payload.get("dimensions", [])
        ]
        blockers = [
            ReadinessBlocker(
                id=b["id"],
                title=b["title"],
                impact=b["impact"],
                action=b["action"],
            )
            for b in payload.get("blockers", [])
        ]
        priority_tasks = [
            ReadinessPriorityTask(
                id=str(m.id),
                label=m.label,
                complete=m.complete,
                completed_at=m.completed_at,
            )
            for m in milestones
        ]
        return MortgageReadinessReportResponse(
            referral_id=referral.id,
            case_id=referral.case_id,  # type: ignore[arg-type]
            credit_analysis_run_id=run.id,
            client_display_name=client_display_name,
            mortgage_readiness_score=run.mortgage_readiness_score,
            band=run.band,
            generated_at=run.generated_at,
            dimensions=dimensions,
            blockers=blockers,
            priority_tasks=priority_tasks,
            docs_status="unknown",
            partner_notes=referral.notes,
            formula_version=run.formula_version,
            score_version=run.score_version,
            disclaimer=disclaimer,
        )

    def _run_to_readiness_summary(
        self,
        *,
        referral: PartnerReferral,
        run: CreditAnalysisRun,
        client_display_name: str | None,
    ) -> ReadinessReportSummary:
        payload: dict[str, Any] = run.payload or {}
        return ReadinessReportSummary(
            referral_id=referral.id,
            case_id=referral.case_id,  # type: ignore[arg-type]
            credit_analysis_run_id=run.id,
            client_display_name=client_display_name,
            mortgage_readiness_score=run.mortgage_readiness_score,
            band=run.band,
            generated_at=run.generated_at,
            formula_version=run.formula_version,
            score_version=run.score_version,
            disclaimer=payload.get("disclaimer") or ADVISORY_DISCLAIMER,
        )

    async def get_readiness_report(
        self,
        user: User,
        partnership_id: uuid.UUID,
        referral_id: uuid.UUID,
    ) -> MortgageReadinessReportResponse:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referral = await self._require_referral(referral_id, partnership_id, cro_org_id)

        if referral.case_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral has no linked case — readiness report unavailable",
            )

        run = await self._repo.get_latest_published_run_for_case(referral.case_id, cro_org_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No published credit-analysis run found for this referral's case",
            )

        names = await self._repo.map_client_display_names(cro_org_id, [referral.client_id])
        milestones = await self._repo.list_milestones(referral.id, cro_org_id)

        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.READINESS_VIEW,
            resource_type="partner_referral",
            resource_id=referral.id,
            partnership_id=partnership_id,
            detail=f"run_id={run.id}",
        )
        await self._session.commit()
        return self._run_to_readiness_report(
            referral=referral,
            run=run,
            client_display_name=names.get(referral.client_id),
            milestones=milestones,
        )

    async def export_readiness_report(
        self,
        user: User,
        partnership_id: uuid.UUID,
        referral_id: uuid.UUID,
        *,
        export_format: CreditAnalysisExportFormat,
    ) -> tuple[bytes, str, str]:
        """Operator-gated export of the readiness report (text/pdf).

        Disclaimer is reproduced prominently. Never auto-transmitted.
        """
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)
        referral = await self._require_referral(referral_id, partnership_id, cro_org_id)

        if referral.case_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral has no linked case — readiness export unavailable",
            )

        run = await self._repo.get_latest_published_run_for_case(referral.case_id, cro_org_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No published credit-analysis run found for this referral's case",
            )

        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.READINESS_EXPORT,
            resource_type="partner_referral",
            resource_id=referral.id,
            partnership_id=partnership_id,
            detail=f"format={export_format} run_id={run.id}",
        )
        await self._session.commit()

        # Build a CreditAnalysisRunResponse to reuse the export formatter

        run_response = CreditAnalysisRunResponse(
            id=run.id,
            case_id=run.case_id,
            generated_at=run.generated_at,
            reports_evaluated=run.reports_evaluated,
            tradelines_evaluated=run.tradelines_evaluated,
            borrower_readiness_score=run.borrower_readiness_score,
            mortgage_readiness_score=run.mortgage_readiness_score,
            schema_version=run.schema_version,
            band=run.band,
            status=run.status,
            payload=run.payload,
            formula_version=run.formula_version,
            score_version=run.score_version,
            inputs_hash=run.inputs_hash,
            published_at=run.published_at,
        )
        return build_credit_analysis_export(run_response, export_format)

    async def list_readiness_reports(
        self,
        user: User,
        partnership_id: uuid.UUID,
    ) -> list[ReadinessReportSummary]:
        """List readiness-report summaries for all referrals with published runs."""
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        await self._require_partnership(partnership_id, cro_org_id)

        referrals = await self._repo.list_referrals_with_case(partnership_id, cro_org_id)
        names = await self._repo.map_client_display_names(
            cro_org_id, [r.client_id for r in referrals]
        )
        summaries: list[ReadinessReportSummary] = []
        for referral in referrals:
            if referral.case_id is None:
                continue
            run = await self._repo.get_latest_published_run_for_case(referral.case_id, cro_org_id)
            if run is None:
                continue
            summaries.append(
                self._run_to_readiness_summary(
                    referral=referral,
                    run=run,
                    client_display_name=names.get(referral.client_id),
                )
            )
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.READINESS_VIEW,
            resource_type="org_partnership",
            resource_id=partnership_id,
            partnership_id=partnership_id,
            detail=f"count={len(summaries)}",
        )
        await self._session.commit()
        return summaries

    # --- Access audits ---

    async def list_access_audits(self, user: User) -> list[PartnerAccessAuditResponse]:
        self._require_write(user)  # admin-only evidence export surface
        cro_org_id = self._require_organization(user)
        rows = await self._repo.list_access_audits(cro_org_id)
        return [PartnerAccessAuditResponse.model_validate(row) for row in rows]

    # --- CRM automation rules (LRP-203) ---

    _DEFAULT_AUTOMATION_RULES: list[dict[str, Any]] = [
        {
            "name": "New referral → intake task",
            "description": ("When a referral is accepted, enqueue document + portal setup tasks."),
            "enabled": True,
            "trigger": "referral_created",
            "action": "Create high-priority intake task for Ops",
            "channel": "task",
        },
        {
            "name": "Stage enter near_ready → LO email",
            "description": "Advisory alert only; no underwriting commitment language.",
            "enabled": True,
            "trigger": "stage_enter",
            "action": "Email assigned LO with readiness summary link",
            "channel": "email",
        },
        {
            "name": "Overdue task → SMS to assignee",
            "description": "Quiet hours respected via notifications SMS policy.",
            "enabled": True,
            "trigger": "task_overdue",
            "action": "SMS reminder to task assignee",
            "channel": "sms",
        },
        {
            "name": "Score band → partner notification",
            "description": "Disabled pending partner preference review.",
            "enabled": False,
            "trigger": "score_band_change",
            "action": "In-app notification to partner owner",
            "channel": "notification",
        },
        {
            "name": "Document uploaded → review task",
            "description": "Routes to Ops for classification before readiness refresh.",
            "enabled": True,
            "trigger": "document_uploaded",
            "action": "Create document review task",
            "channel": "task",
        },
    ]

    async def list_automation_rules(self, user: User) -> list[CrmAutomationRuleResponse]:
        from sqlalchemy import func, select

        from api.modules.mortgage_partner.automation_models import (
            CrmAutomationChannel,
            CrmAutomationRule,
            CrmAutomationTrigger,
        )

        self._require_read(user)
        organization_id = self._require_organization(user)

        count_result = await self._session.execute(
            select(func.count())
            .select_from(CrmAutomationRule)
            .where(
                CrmAutomationRule.organization_id == organization_id,
                CrmAutomationRule.deleted_at.is_(None),
            )
        )
        if int(count_result.scalar_one()) == 0:
            for spec in self._DEFAULT_AUTOMATION_RULES:
                rule = CrmAutomationRule(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    name=spec["name"],
                    description=spec["description"],
                    enabled=bool(spec["enabled"]),
                    trigger=CrmAutomationTrigger(spec["trigger"]),
                    action=spec["action"],
                    channel=CrmAutomationChannel(spec["channel"]),
                    fire_count=0,
                    created_by_id=user.id,
                    updated_by_id=user.id,
                )
                self._session.add(rule)
            await self._session.commit()

        result = await self._session.execute(
            select(CrmAutomationRule)
            .where(
                CrmAutomationRule.organization_id == organization_id,
                CrmAutomationRule.deleted_at.is_(None),
            )
            .order_by(CrmAutomationRule.created_at.asc(), CrmAutomationRule.name.asc())
        )
        rows = list(result.scalars().all())
        return [
            CrmAutomationRuleResponse(
                id=row.id,
                organization_id=row.organization_id,
                name=row.name,
                description=row.description,
                enabled=row.enabled,
                trigger=row.trigger.value,
                action=row.action,
                channel=row.channel.value,
                last_fired_at=row.last_fired_at,
                fire_count=row.fire_count,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def create_automation_rule(
        self,
        user: User,
        payload: CrmAutomationRuleCreate,
    ) -> CrmAutomationRuleResponse:
        from api.modules.mortgage_partner.automation_models import (
            CrmAutomationChannel,
            CrmAutomationRule,
            CrmAutomationTrigger,
        )

        self._require_write(user)
        organization_id = self._require_organization(user)
        rule = CrmAutomationRule(
            id=uuid.uuid4(),
            organization_id=organization_id,
            name=payload.name,
            description=payload.description,
            enabled=payload.enabled,
            trigger=CrmAutomationTrigger(payload.trigger),
            action=payload.action,
            channel=CrmAutomationChannel(payload.channel),
            fire_count=0,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        self._session.add(rule)
        await self._session.commit()
        await self._session.refresh(rule)
        return CrmAutomationRuleResponse(
            id=rule.id,
            organization_id=rule.organization_id,
            name=rule.name,
            description=rule.description,
            enabled=rule.enabled,
            trigger=rule.trigger.value,
            action=rule.action,
            channel=rule.channel.value,
            last_fired_at=rule.last_fired_at,
            fire_count=rule.fire_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    async def update_automation_rule(
        self,
        user: User,
        rule_id: uuid.UUID,
        payload: CrmAutomationRuleUpdate,
    ) -> CrmAutomationRuleResponse:
        from sqlalchemy import select

        from api.modules.mortgage_partner.automation_models import (
            CrmAutomationChannel,
            CrmAutomationRule,
            CrmAutomationTrigger,
        )

        self._require_write(user)
        organization_id = self._require_organization(user)
        result = await self._session.execute(
            select(CrmAutomationRule).where(
                CrmAutomationRule.id == rule_id,
                CrmAutomationRule.organization_id == organization_id,
                CrmAutomationRule.deleted_at.is_(None),
            )
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation rule not found",
            )
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] is not None:
            rule.name = data["name"]
        if "description" in data:
            rule.description = data["description"]
        if "enabled" in data and data["enabled"] is not None:
            rule.enabled = data["enabled"]
        if "trigger" in data and data["trigger"] is not None:
            rule.trigger = CrmAutomationTrigger(data["trigger"])
        if "action" in data and data["action"] is not None:
            rule.action = data["action"]
        if "channel" in data and data["channel"] is not None:
            rule.channel = CrmAutomationChannel(data["channel"])
        rule.updated_by_id = user.id
        await self._session.commit()
        await self._session.refresh(rule)
        return CrmAutomationRuleResponse(
            id=rule.id,
            organization_id=rule.organization_id,
            name=rule.name,
            description=rule.description,
            enabled=rule.enabled,
            trigger=rule.trigger.value,
            action=rule.action,
            channel=rule.channel.value,
            last_fired_at=rule.last_fired_at,
            fire_count=rule.fire_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    # --- CRM appointments + reminders (LRP-205) ---

    def _appointment_to_response(self, row: Any) -> CrmAppointmentResponse:
        return CrmAppointmentResponse(
            id=row.id,
            organization_id=row.organization_id,
            case_id=row.case_id,
            title=row.title,
            appointment_type=row.appointment_type.value,
            status=row.status.value,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
            location=row.location,
            meeting_url=row.meeting_url,
            related_name=row.related_name,
            owner_user_id=row.owner_user_id,
            borrower_name=row.borrower_name,
            borrower_email=row.borrower_email,
            borrower_phone=row.borrower_phone,
            referring_lo_email=row.referring_lo_email,
            referring_lo_name=row.referring_lo_name,
            tcpa_consent=row.tcpa_consent,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _reminder_to_response(self, row: Any) -> AppointmentReminderRunResponse:
        return AppointmentReminderRunResponse(
            id=row.id,
            organization_id=row.organization_id,
            appointment_id=row.appointment_id,
            offset_key=row.offset_key,
            status=row.status,
            schema_version=row.schema_version,
            matrix_dispatch_id=row.matrix_dispatch_id,
            started_at=row.started_at,
            completed_at=row.completed_at,
            payload=row.payload,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def list_appointments(self, user: User) -> list[CrmAppointmentResponse]:
        from sqlalchemy import select

        from api.modules.mortgage_partner.appointment_models import CrmAppointment

        self._require_read(user)
        organization_id = self._require_organization(user)
        result = await self._session.execute(
            select(CrmAppointment)
            .where(
                CrmAppointment.organization_id == organization_id,
                CrmAppointment.deleted_at.is_(None),
            )
            .order_by(CrmAppointment.starts_at.asc())
        )
        return [self._appointment_to_response(row) for row in result.scalars().all()]

    async def create_appointment(
        self,
        user: User,
        payload: CrmAppointmentCreate,
    ) -> CrmAppointmentResponse:
        from api.modules.mortgage_partner.appointment_models import (
            CrmAppointment,
            CrmAppointmentStatus,
            CrmAppointmentType,
        )
        from api.modules.notifications.notification_matrix import (
            NotificationMatrixEvent,
            advisory_footer,
        )
        from api.modules.notifications.notification_matrix_service import (
            MatrixDispatchContext,
            NotificationMatrixDispatcher,
        )

        self._require_write(user)
        organization_id = self._require_organization(user)
        starts = payload.starts_at
        ends = payload.ends_at
        if starts.tzinfo is None:
            starts = starts.replace(tzinfo=UTC)
        if ends.tzinfo is None:
            ends = ends.replace(tzinfo=UTC)

        appointment = CrmAppointment(
            id=uuid.uuid4(),
            organization_id=organization_id,
            case_id=payload.case_id,
            title=payload.title,
            appointment_type=CrmAppointmentType(payload.appointment_type),
            status=CrmAppointmentStatus.SCHEDULED,
            starts_at=starts,
            ends_at=ends,
            location=payload.location,
            meeting_url=payload.meeting_url,
            related_name=payload.related_name or payload.borrower_name,
            owner_user_id=payload.owner_user_id or user.id,
            borrower_name=payload.borrower_name,
            borrower_email=str(payload.borrower_email) if payload.borrower_email else None,
            borrower_phone=payload.borrower_phone,
            referring_lo_email=(
                str(payload.referring_lo_email) if payload.referring_lo_email else None
            ),
            referring_lo_name=payload.referring_lo_name,
            tcpa_consent=payload.tcpa_consent,
            notes=payload.notes,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        self._session.add(appointment)
        await self._session.flush()

        footer = advisory_footer()
        when_label = starts.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")
        matrix = NotificationMatrixDispatcher(self._session)
        await matrix.dispatch(
            NotificationMatrixEvent.CONSULTATION_SCHEDULED,
            MatrixDispatchContext(
                organization_id=organization_id,
                entity_type="appointment",
                entity_id=appointment.id,
                title=f"Consultation scheduled — {appointment.title}",
                body=(
                    f"Your consultation with Lending Readiness Partners is scheduled for "
                    f"{when_label}. We'll review education and next steps toward your next "
                    f"financing conversation. {footer}"
                ),
                action_url="/crm/calendar",
                case_id=appointment.case_id,
                assigned_user_id=appointment.owner_user_id,
                referring_lo_email=appointment.referring_lo_email,
                referring_lo_name=appointment.referring_lo_name,
                borrower_email=appointment.borrower_email,
                borrower_name=appointment.borrower_name,
                tcpa_consent=appointment.tcpa_consent,
                sms_phone=appointment.borrower_phone,
                triggered_by_user_id=user.id,
                source_module="mortgage_partner.appointments",
                create_crm_tasks=False,
            ),
        )
        await self._session.commit()
        await self._session.refresh(appointment)
        return self._appointment_to_response(appointment)

    async def update_appointment(
        self,
        user: User,
        appointment_id: uuid.UUID,
        payload: CrmAppointmentUpdate,
    ) -> CrmAppointmentResponse:
        from sqlalchemy import select

        from api.modules.mortgage_partner.appointment_models import (
            CrmAppointment,
            CrmAppointmentStatus,
            CrmAppointmentType,
        )

        self._require_write(user)
        organization_id = self._require_organization(user)
        result = await self._session.execute(
            select(CrmAppointment).where(
                CrmAppointment.id == appointment_id,
                CrmAppointment.organization_id == organization_id,
                CrmAppointment.deleted_at.is_(None),
            )
        )
        appointment = result.scalar_one_or_none()
        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )
        data = payload.model_dump(exclude_unset=True)
        if "title" in data and data["title"] is not None:
            appointment.title = data["title"]
        if "appointment_type" in data and data["appointment_type"] is not None:
            appointment.appointment_type = CrmAppointmentType(data["appointment_type"])
        if "status" in data and data["status"] is not None:
            appointment.status = CrmAppointmentStatus(data["status"])
        if "starts_at" in data and data["starts_at"] is not None:
            starts = data["starts_at"]
            if starts.tzinfo is None:
                starts = starts.replace(tzinfo=UTC)
            appointment.starts_at = starts
        if "ends_at" in data and data["ends_at"] is not None:
            ends = data["ends_at"]
            if ends.tzinfo is None:
                ends = ends.replace(tzinfo=UTC)
            appointment.ends_at = ends
        for field in (
            "location",
            "meeting_url",
            "related_name",
            "owner_user_id",
            "borrower_name",
            "borrower_phone",
            "referring_lo_name",
            "notes",
        ):
            if field in data:
                setattr(appointment, field, data[field])
        if "borrower_email" in data:
            appointment.borrower_email = (
                str(data["borrower_email"]) if data["borrower_email"] else None
            )
        if "referring_lo_email" in data:
            appointment.referring_lo_email = (
                str(data["referring_lo_email"]) if data["referring_lo_email"] else None
            )
        if "tcpa_consent" in data and data["tcpa_consent"] is not None:
            appointment.tcpa_consent = data["tcpa_consent"]
        if appointment.ends_at <= appointment.starts_at:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="ends_at must be after starts_at",
            )
        appointment.updated_by_id = user.id
        await self._session.commit()
        await self._session.refresh(appointment)
        return self._appointment_to_response(appointment)

    async def process_appointment_reminders(
        self,
        user: User,
    ) -> AppointmentReminderProcessResponse:
        from api.modules.mortgage_partner.appointment_reminders import (
            AppointmentReminderProcessor,
        )

        self._require_write(user)
        organization_id = self._require_organization(user)
        processor = AppointmentReminderProcessor(self._session)
        runs = await processor.process_due(
            organization_id=organization_id,
            triggered_by_user_id=user.id,
        )
        await self._session.commit()
        return AppointmentReminderProcessResponse(
            processed_count=len(runs),
            runs=[self._reminder_to_response(run) for run in runs],
        )

    async def list_appointment_reminders(
        self,
        user: User,
        *,
        appointment_id: uuid.UUID | None = None,
    ) -> list[AppointmentReminderRunResponse]:
        from api.modules.mortgage_partner.appointment_reminders import (
            AppointmentReminderProcessor,
        )

        self._require_read(user)
        organization_id = self._require_organization(user)
        processor = AppointmentReminderProcessor(self._session)
        runs = await processor.list_runs(
            organization_id=organization_id,
            appointment_id=appointment_id,
        )
        return [self._reminder_to_response(run) for run in runs]
