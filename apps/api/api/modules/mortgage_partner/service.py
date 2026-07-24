"""Mortgage partner service — partnerships, members, referrals, milestones, access audits."""

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
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
from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    OrgPartnership,
    OrgPartnershipMember,
    PartnerAccessAction,
    PartnerAccessAudit,
    PartnerLoanMilestone,
    PartnerReferral,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_READ_ROLE,
    MORTGAGE_PARTNER_WRITE_ROLE,
    PARTNER_ROLE_PERMISSIONS,
)
from api.modules.mortgage_partner.repository import MortgagePartnerRepository
from api.modules.mortgage_partner.schemas import (
    DashboardSummaryResponse,
    MilestoneReplacePayload,
    MortgagePartnerStatusResponse,
    MortgageReadinessReportResponse,
    PartnerAccessAuditResponse,
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
)

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
        created_by_id: uuid.UUID,
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
                "partner_referrals",
                "partner_access_audits",
                "partner_role_matrix",
                "partner_pipeline",
                "partner_milestones",
                "partner_readiness_report",
                "partner_readiness_export",
            ],
            deferred_capabilities=[
                "partner_jwt_realm",
                "cross_tenant_marketplace",
                "live_bureau_soft_pull",
                "unsupervised_filing",
                "custom_partner_domains",
            ],
        )

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
        return PartnershipResponse.model_validate(created)

    async def list_partnerships(self, user: User) -> list[PartnershipResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        rows = await self._repo.list_partnerships(cro_org_id)
        return [PartnershipResponse.model_validate(row) for row in rows]

    async def get_partnership(self, user: User, partnership_id: uuid.UUID) -> PartnershipResponse:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        partnership = await self._require_partnership(partnership_id, cro_org_id)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.PARTNERSHIP_VIEW,
            resource_type="org_partnership",
            resource_id=partnership.id,
            partnership_id=partnership.id,
        )
        await self._session.commit()
        return PartnershipResponse.model_validate(partnership)

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
