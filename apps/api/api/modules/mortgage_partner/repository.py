"""Mortgage partner persistence."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case
from api.modules.clients.models import Client
from api.modules.mortgage_partner.models import (
    OrgPartnership,
    OrgPartnershipMember,
    PartnerAccessAudit,
    PartnerLoanMilestone,
    PartnerReferral,
)


class MortgagePartnerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_organization(self, organization_id: uuid.UUID) -> Organization | None:
        result = await self._session.execute(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_in_org(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> User | None:
        result = await self._session.execute(
            select(User).where(
                User.id == user_id,
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_client_in_org(
        self, client_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Client | None:
        result = await self._session.execute(
            select(Client).where(
                Client.id == client_id,
                Client.organization_id == organization_id,
                Client.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def map_client_display_names(
        self,
        organization_id: uuid.UUID,
        client_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, str]:
        if not client_ids:
            return {}
        result = await self._session.execute(
            select(Client.id, Client.display_name).where(
                Client.organization_id == organization_id,
                Client.id.in_(client_ids),
                Client.deleted_at.is_(None),
            )
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_case_in_org(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case | None:
        result = await self._session.execute(
            select(Case).where(
                Case.id == case_id,
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_partnership(self, partnership: OrgPartnership) -> OrgPartnership:
        self._session.add(partnership)
        await self._session.flush()
        await self._session.refresh(partnership)
        return partnership

    async def list_partnerships(self, cro_organization_id: uuid.UUID) -> list[OrgPartnership]:
        result = await self._session.execute(
            select(OrgPartnership)
            .where(
                OrgPartnership.cro_organization_id == cro_organization_id,
                OrgPartnership.deleted_at.is_(None),
            )
            .order_by(OrgPartnership.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_partnership(
        self, partnership_id: uuid.UUID, cro_organization_id: uuid.UUID
    ) -> OrgPartnership | None:
        result = await self._session.execute(
            select(OrgPartnership).where(
                OrgPartnership.id == partnership_id,
                OrgPartnership.cro_organization_id == cro_organization_id,
                OrgPartnership.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def find_partnership_pair(
        self, cro_organization_id: uuid.UUID, partner_organization_id: uuid.UUID
    ) -> OrgPartnership | None:
        result = await self._session.execute(
            select(OrgPartnership).where(
                OrgPartnership.cro_organization_id == cro_organization_id,
                OrgPartnership.partner_organization_id == partner_organization_id,
                OrgPartnership.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_member(self, member: OrgPartnershipMember) -> OrgPartnershipMember:
        self._session.add(member)
        await self._session.flush()
        await self._session.refresh(member)
        return member

    async def list_members(
        self, partnership_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[OrgPartnershipMember]:
        result = await self._session.execute(
            select(OrgPartnershipMember)
            .where(
                OrgPartnershipMember.partnership_id == partnership_id,
                OrgPartnershipMember.organization_id == organization_id,
                OrgPartnershipMember.deleted_at.is_(None),
            )
            .order_by(OrgPartnershipMember.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_member(
        self, partnership_id: uuid.UUID, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> OrgPartnershipMember | None:
        result = await self._session.execute(
            select(OrgPartnershipMember).where(
                OrgPartnershipMember.partnership_id == partnership_id,
                OrgPartnershipMember.user_id == user_id,
                OrgPartnershipMember.organization_id == organization_id,
                OrgPartnershipMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_referral(self, referral: PartnerReferral) -> PartnerReferral:
        self._session.add(referral)
        await self._session.flush()
        await self._session.refresh(referral)
        return referral

    async def list_referrals(
        self, partnership_id: uuid.UUID, cro_organization_id: uuid.UUID
    ) -> list[PartnerReferral]:
        result = await self._session.execute(
            select(PartnerReferral)
            .where(
                PartnerReferral.partnership_id == partnership_id,
                PartnerReferral.cro_organization_id == cro_organization_id,
                PartnerReferral.deleted_at.is_(None),
            )
            .order_by(PartnerReferral.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_referral(
        self,
        referral_id: uuid.UUID,
        partnership_id: uuid.UUID,
        cro_organization_id: uuid.UUID,
    ) -> PartnerReferral | None:
        result = await self._session.execute(
            select(PartnerReferral).where(
                PartnerReferral.id == referral_id,
                PartnerReferral.partnership_id == partnership_id,
                PartnerReferral.cro_organization_id == cro_organization_id,
                PartnerReferral.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def save_referral(self, referral: PartnerReferral) -> PartnerReferral:
        await self._session.flush()
        await self._session.refresh(referral)
        return referral

    # --- Milestone persistence ---

    async def create_milestone(self, milestone: PartnerLoanMilestone) -> PartnerLoanMilestone:
        self._session.add(milestone)
        await self._session.flush()
        await self._session.refresh(milestone)
        return milestone

    async def bulk_create_milestones(
        self, milestones: list[PartnerLoanMilestone]
    ) -> list[PartnerLoanMilestone]:
        for m in milestones:
            self._session.add(m)
        await self._session.flush()
        for m in milestones:
            await self._session.refresh(m)
        return milestones

    async def list_milestones(
        self, referral_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[PartnerLoanMilestone]:
        result = await self._session.execute(
            select(PartnerLoanMilestone)
            .where(
                PartnerLoanMilestone.referral_id == referral_id,
                PartnerLoanMilestone.organization_id == organization_id,
                PartnerLoanMilestone.deleted_at.is_(None),
            )
            .order_by(PartnerLoanMilestone.sort_order, PartnerLoanMilestone.created_at)
        )
        return list(result.scalars().all())

    async def soft_delete_milestones_for_referral(
        self, referral_id: uuid.UUID, organization_id: uuid.UUID
    ) -> None:
        """Soft-delete all non-deleted milestones for a referral (replace-all pattern)."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(PartnerLoanMilestone).where(
                PartnerLoanMilestone.referral_id == referral_id,
                PartnerLoanMilestone.organization_id == organization_id,
                PartnerLoanMilestone.deleted_at.is_(None),
            )
        )
        for row in result.scalars().all():
            row.deleted_at = now
        await self._session.flush()

    # --- Pipeline / dashboard aggregation ---

    async def list_pipeline_referrals(
        self, partnership_id: uuid.UUID, cro_organization_id: uuid.UUID
    ) -> list[PartnerReferral]:
        """All non-deleted referrals ordered by pipeline_stage_changed_at desc."""
        result = await self._session.execute(
            select(PartnerReferral)
            .where(
                PartnerReferral.partnership_id == partnership_id,
                PartnerReferral.cro_organization_id == cro_organization_id,
                PartnerReferral.deleted_at.is_(None),
            )
            .order_by(
                PartnerReferral.pipeline_stage_changed_at.desc().nullslast(),
                PartnerReferral.created_at.desc(),
            )
        )
        return list(result.scalars().all())

    def compute_dashboard_summary(self, referrals: list[PartnerReferral]) -> dict[str, int]:
        """Return stage-count dict from an already-fetched referral list."""
        counts: dict[str, int] = {}
        for ref in referrals:
            key = ref.pipeline_stage.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    # --- Access audit ---

    async def create_access_audit(self, audit: PartnerAccessAudit) -> PartnerAccessAudit:
        self._session.add(audit)
        await self._session.flush()
        await self._session.refresh(audit)
        return audit

    async def get_latest_published_run_for_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> CreditAnalysisRun | None:
        """Return the most-recent published credit-analysis run for a case."""
        result = await self._session.execute(
            select(CreditAnalysisRun)
            .where(
                CreditAnalysisRun.case_id == case_id,
                CreditAnalysisRun.organization_id == organization_id,
                CreditAnalysisRun.status == "published",
            )
            .order_by(CreditAnalysisRun.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_referrals_with_case(
        self,
        partnership_id: uuid.UUID,
        cro_organization_id: uuid.UUID,
    ) -> list[PartnerReferral]:
        """All non-deleted referrals that have a case_id (needed for readiness list)."""
        result = await self._session.execute(
            select(PartnerReferral)
            .where(
                PartnerReferral.partnership_id == partnership_id,
                PartnerReferral.cro_organization_id == cro_organization_id,
                PartnerReferral.deleted_at.is_(None),
                PartnerReferral.case_id.is_not(None),
            )
            .order_by(PartnerReferral.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_access_audits(
        self, cro_organization_id: uuid.UUID, *, limit: int = 100
    ) -> list[PartnerAccessAudit]:
        result = await self._session.execute(
            select(PartnerAccessAudit)
            .where(PartnerAccessAudit.cro_organization_id == cro_organization_id)
            .order_by(PartnerAccessAudit.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
