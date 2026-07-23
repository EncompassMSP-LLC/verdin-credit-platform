"""Mortgage partner service — partnerships, members, referrals, access audits."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.mortgage_partner.models import (
    OrgPartnership,
    OrgPartnershipMember,
    PartnerAccessAction,
    PartnerAccessAudit,
    PartnerReferral,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_READ_ROLE,
    MORTGAGE_PARTNER_WRITE_ROLE,
    PARTNER_ROLE_PERMISSIONS,
)
from api.modules.mortgage_partner.repository import MortgagePartnerRepository
from api.modules.mortgage_partner.schemas import (
    MortgagePartnerStatusResponse,
    PartnerAccessAuditResponse,
    PartnerReferralCreate,
    PartnerReferralResponse,
    PartnerRoleMatrixItem,
    PartnerRoleMatrixResponse,
    PartnershipCreate,
    PartnershipMemberCreate,
    PartnershipMemberResponse,
    PartnershipResponse,
)


class MortgagePartnerService:
    def __init__(self, repo: MortgagePartnerRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "MortgagePartnerService":
        return cls(MortgagePartnerRepository(session), session)

    def _referral_response(
        self,
        row: PartnerReferral,
        *,
        client_display_name: str | None,
    ) -> PartnerReferralResponse:
        return PartnerReferralResponse(
            id=row.id,
            partnership_id=row.partnership_id,
            cro_organization_id=row.cro_organization_id,
            client_id=row.client_id,
            case_id=row.case_id,
            status=row.status,
            source_label=row.source_label,
            notes=row.notes,
            referred_by_user_id=row.referred_by_user_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
            client_display_name=client_display_name,
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
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
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
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )

        target = await self._repo.get_user_in_org(payload.user_id, cro_org_id)
        if target is None:
            # Allow members from partner org as well (same platform user table)
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
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
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
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )

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

        referral = PartnerReferral(
            id=uuid.uuid4(),
            partnership_id=partnership_id,
            cro_organization_id=cro_org_id,
            client_id=payload.client_id,
            case_id=payload.case_id,
            status=payload.status,
            source_label=payload.source_label,
            notes=payload.notes,
            referred_by_user_id=user.id,
        )
        apply_audit_on_create(referral, user.id)
        created = await self._repo.create_referral(referral)
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_CREATE,
            resource_type="partner_referral",
            resource_id=created.id,
            partnership_id=partnership_id,
            detail=f"client_id={payload.client_id}",
        )
        await self._session.commit()
        return self._referral_response(created, client_display_name=client.display_name)

    async def list_referrals(
        self, user: User, partnership_id: uuid.UUID
    ) -> list[PartnerReferralResponse]:
        self._require_read(user)
        cro_org_id = self._require_organization(user)
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
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
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
        referral = await self._repo.get_referral(referral_id, partnership_id, cro_org_id)
        if referral is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral not found",
            )
        names = await self._repo.map_client_display_names(cro_org_id, [referral.client_id])
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
        )

    async def list_access_audits(self, user: User) -> list[PartnerAccessAuditResponse]:
        self._require_write(user)  # admin-only evidence export surface
        cro_org_id = self._require_organization(user)
        rows = await self._repo.list_access_audits(cro_org_id)
        return [PartnerAccessAuditResponse.model_validate(row) for row in rows]
