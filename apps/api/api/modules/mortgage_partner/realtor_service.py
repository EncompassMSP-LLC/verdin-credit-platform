"""Realtor partner invite, activation, password reset, and session (LRP-301)."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.config import get_settings
from api.core.constants import UserRole
from api.core.permissions import has_permission
from api.core.security import create_access_token, create_refresh_token, hash_password
from api.modules.auth.models import User
from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    OrgPartnership,
    OrgPartnershipMember,
    PartnerAccessAction,
    PartnerAccessAudit,
    PartnerOrgType,
    PartnerRole,
    PartnershipStatus,
)
from api.modules.mortgage_partner.permissions import (
    MORTGAGE_PARTNER_WRITE_ROLE,
    PARTNER_ROLE_PERMISSIONS,
    partner_role_has_permission,
)
from api.modules.mortgage_partner.realtor_models import (
    PartnerRealtorCredentialToken,
    PartnerRealtorInvite,
    RealtorCredentialPurpose,
)
from api.modules.mortgage_partner.repository import MortgagePartnerRepository
from api.modules.mortgage_partner.schemas import (
    RealtorInviteAcceptRequest,
    RealtorInviteCreate,
    RealtorInvitePreviewResponse,
    RealtorInviteResponse,
    RealtorPasswordResetConfirm,
    RealtorPasswordResetRequest,
    RealtorPasswordResetRequestResponse,
    RealtorPipelineBoardResponse,
    RealtorPortalDashboardResponse,
    RealtorReferralCardResponse,
    RealtorSessionResponse,
    RealtorTokenResponse,
)
from api.modules.mortgage_partner.weekly_digest_service import borrower_initials

_INVITE_TTL = timedelta(days=7)
_RESET_TTL = timedelta(hours=1)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mint_token() -> str:
    return secrets.token_urlsafe(32)


class RealtorPartnerService:
    def __init__(self, repo: MortgagePartnerRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> RealtorPartnerService:
        return cls(MortgagePartnerRepository(session), session)

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, MORTGAGE_PARTNER_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no organization",
            )
        return user.organization_id

    async def _require_realtor_partnership(
        self, partnership_id: uuid.UUID, cro_org_id: uuid.UUID
    ) -> OrgPartnership:
        partnership = await self._repo.get_partnership(partnership_id, cro_org_id)
        if partnership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partnership not found",
            )
        if partnership.partner_type != PartnerOrgType.REALTOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partnership is not a realtor partner organization",
            )
        if partnership.status not in {PartnershipStatus.ACTIVE, PartnershipStatus.PENDING}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partnership is not active for realtor invites",
            )
        return partnership

    async def _audit(
        self,
        *,
        cro_organization_id: uuid.UUID,
        actor: User,
        action: PartnerAccessAction,
        resource_type: str,
        resource_id: uuid.UUID | None,
        partnership_id: uuid.UUID | None = None,
        detail: str | None = None,
    ) -> None:
        row = PartnerAccessAudit(
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
        self._session.add(row)
        await self._session.flush()

    async def _org_name(self, organization_id: uuid.UUID) -> str:
        org = await self._repo.get_organization(organization_id)
        return org.name if org else "Partner"

    def _session_from_membership(
        self,
        user: User,
        member: OrgPartnershipMember,
        partnership: OrgPartnership,
        partner_org_name: str,
    ) -> RealtorSessionResponse:
        perms = sorted(PARTNER_ROLE_PERMISSIONS.get(PartnerRole.REALTOR, frozenset()))
        return RealtorSessionResponse(
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=f"{user.first_name} {user.last_name}".strip(),
            partner_role=PartnerRole.REALTOR,
            permissions=perms,
            membership_id=member.id,
            membership_active=member.is_active,
            partnership_id=partnership.id,
            partnership_display_name=partnership.display_name,
            cro_organization_id=partnership.cro_organization_id,
            partner_organization_id=partnership.partner_organization_id,
            partner_organization_name=partner_org_name,
            partner_type=partnership.partner_type,
        )

    async def create_invite(
        self,
        actor: User,
        partnership_id: uuid.UUID,
        payload: RealtorInviteCreate,
    ) -> RealtorInviteResponse:
        self._require_write(actor)
        cro_org_id = self._require_organization(actor)
        partnership = await self._require_realtor_partnership(partnership_id, cro_org_id)

        email = str(payload.email).strip().lower()
        raw = _mint_token()
        invite = PartnerRealtorInvite(
            id=uuid.uuid4(),
            organization_id=cro_org_id,
            partnership_id=partnership.id,
            partner_organization_id=partnership.partner_organization_id,
            email=email,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            token_hash=_hash_token(raw),
            invited_by_id=actor.id,
            expires_at=datetime.now(UTC) + _INVITE_TTL,
            notes=payload.notes,
        )
        self._session.add(invite)
        await self._session.flush()
        await self._audit(
            cro_organization_id=cro_org_id,
            actor=actor,
            action=PartnerAccessAction.MEMBER_CREATE,
            resource_type="partner_realtor_invite",
            resource_id=invite.id,
            partnership_id=partnership.id,
            detail=f"realtor_invite email={email}",
        )
        await self._session.commit()
        await self._session.refresh(invite)
        body = RealtorInviteResponse.model_validate(invite)
        body.invite_token = raw
        return body

    async def preview_invite(self, token: str) -> RealtorInvitePreviewResponse:
        invite = await self._get_invite_by_token(token, allow_accepted=True)
        partnership = await self._session.get(OrgPartnership, invite.partnership_id)
        if partnership is None or partnership.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
        partner_name = await self._org_name(invite.partner_organization_id)
        return RealtorInvitePreviewResponse(
            email=invite.email,
            first_name=invite.first_name,
            last_name=invite.last_name,
            partnership_display_name=partnership.display_name,
            partner_organization_name=partner_name,
            expires_at=invite.expires_at,
            already_accepted=invite.accepted_at is not None,
        )

    async def accept_invite(self, payload: RealtorInviteAcceptRequest) -> RealtorTokenResponse:
        invite = await self._get_invite_by_token(payload.token, allow_accepted=False)
        if invite.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has been revoked")
        if invite.expires_at <= datetime.now(UTC):
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has expired")

        partnership = await self._session.get(OrgPartnership, invite.partnership_id)
        if partnership is None or partnership.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Partnership not found"
            )
        if partnership.partner_type != PartnerOrgType.REALTOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite is not for a realtor partnership",
            )

        user = await self._get_user_by_email(invite.email)
        if user is None:
            user = User(
                id=uuid.uuid4(),
                email=invite.email,
                hashed_password=hash_password(payload.password),
                first_name=invite.first_name,
                last_name=invite.last_name,
                role=UserRole.READ_ONLY,
                organization_id=invite.partner_organization_id,
                is_active=True,
            )
            apply_audit_on_create(user, invite.invited_by_id)
            self._session.add(user)
            await self._session.flush()
        else:
            if user.organization_id not in {
                invite.partner_organization_id,
                invite.organization_id,
            }:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already registered to another organization",
                )
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is disabled",
                )
            user.hashed_password = hash_password(payload.password)
            user.first_name = invite.first_name
            user.last_name = invite.last_name
            if user.organization_id is None:
                user.organization_id = invite.partner_organization_id
            apply_audit_on_update(user, invite.invited_by_id)

        existing = await self._repo.get_member(
            invite.partnership_id, user.id, invite.organization_id
        )
        if existing is None:
            member = OrgPartnershipMember(
                id=uuid.uuid4(),
                partnership_id=invite.partnership_id,
                organization_id=invite.organization_id,
                user_id=user.id,
                partner_role=PartnerRole.REALTOR,
                is_active=True,
            )
            apply_audit_on_create(member, invite.invited_by_id)
            await self._repo.create_member(member)
        else:
            if existing.partner_role != PartnerRole.REALTOR:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already holds a non-realtor membership on this partnership",
                )
            existing.is_active = True
            apply_audit_on_update(existing, invite.invited_by_id)
            member = existing

        invite.accepted_at = datetime.now(UTC)
        await self._audit(
            cro_organization_id=invite.organization_id,
            actor=user,
            action=PartnerAccessAction.MEMBER_CREATE,
            resource_type="org_partnership_member",
            resource_id=member.id,
            partnership_id=invite.partnership_id,
            detail="realtor_invite_accepted",
        )
        await self._session.commit()
        await self._session.refresh(user)
        await self._session.refresh(member)
        await self._session.refresh(partnership)

        partner_name = await self._org_name(partnership.partner_organization_id)
        session = self._session_from_membership(user, member, partnership, partner_name)
        return RealtorTokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
            realtor=session,
        )

    async def get_me(self, user: User) -> RealtorSessionResponse:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        member, partnership = await self._require_active_realtor_membership(user)
        partner_name = await self._org_name(partnership.partner_organization_id)
        return self._session_from_membership(user, member, partnership, partner_name)

    async def list_own_referrals(self, user: User) -> list[RealtorReferralCardResponse]:
        """Partnership-scoped referrals; marks own (referred_by) for MVP visibility."""
        if not partner_role_has_permission(PartnerRole.REALTOR, "referrals.view"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        member, partnership = await self._require_active_realtor_membership(user)
        cards = await self._build_referral_cards(user, partnership, own_only=False)
        await self._audit(
            cro_organization_id=partnership.cro_organization_id,
            actor=user,
            action=PartnerAccessAction.REFERRAL_LIST,
            resource_type="org_partnership",
            resource_id=partnership.id,
            partnership_id=partnership.id,
            detail=f"realtor_portal count={len(cards)} member={member.id}",
        )
        await self._session.commit()
        return cards

    async def get_pipeline_board(self, user: User) -> RealtorPipelineBoardResponse:
        if not partner_role_has_permission(PartnerRole.REALTOR, "pipeline.view"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        _member, partnership = await self._require_active_realtor_membership(user)
        cards = await self._build_referral_cards(user, partnership, own_only=False)
        await self._audit(
            cro_organization_id=partnership.cro_organization_id,
            actor=user,
            action=PartnerAccessAction.PIPELINE_VIEW,
            resource_type="org_partnership",
            resource_id=partnership.id,
            partnership_id=partnership.id,
            detail=f"realtor_pipeline count={len(cards)}",
        )
        await self._session.commit()
        return RealtorPipelineBoardResponse(
            partnership_id=partnership.id,
            partnership_display_name=partnership.display_name,
            cards=cards,
        )

    async def get_portal_dashboard(self, user: User) -> RealtorPortalDashboardResponse:
        if not partner_role_has_permission(PartnerRole.REALTOR, "partnership.view"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        _member, partnership = await self._require_active_realtor_membership(user)
        cards = await self._build_referral_cards(user, partnership, own_only=False)
        counts: dict[str, int] = {stage.value: 0 for stage in LoanPipelineStage}
        for card in cards:
            counts[card.pipeline_stage.value] = counts.get(card.pipeline_stage.value, 0) + 1
        own_count = sum(1 for card in cards if card.is_own_referral)
        await self._audit(
            cro_organization_id=partnership.cro_organization_id,
            actor=user,
            action=PartnerAccessAction.PIPELINE_VIEW,
            resource_type="org_partnership",
            resource_id=partnership.id,
            partnership_id=partnership.id,
            detail="realtor_dashboard",
        )
        await self._session.commit()
        return RealtorPortalDashboardResponse(
            partnership_id=partnership.id,
            partnership_display_name=partnership.display_name,
            total_referrals=len(cards),
            own_referral_count=own_count,
            counts_by_stage=counts,
            near_ready_count=counts.get(LoanPipelineStage.NEAR_READY.value, 0),
            mortgage_ready_count=counts.get(LoanPipelineStage.MORTGAGE_READY.value, 0),
            in_underwriting_count=counts.get(LoanPipelineStage.IN_UNDERWRITING.value, 0),
            funded_count=counts.get(LoanPipelineStage.FUNDED.value, 0),
            declined_count=counts.get(LoanPipelineStage.DECLINED.value, 0),
            recent=cards[:8],
        )

    async def _build_referral_cards(
        self,
        user: User,
        partnership: OrgPartnership,
        *,
        own_only: bool,
    ) -> list[RealtorReferralCardResponse]:
        referrals = await self._repo.list_referrals(partnership.id, partnership.cro_organization_id)
        if own_only:
            referrals = [r for r in referrals if r.referred_by_user_id == user.id]
        names = await self._repo.map_client_display_names(
            partnership.cro_organization_id, [r.client_id for r in referrals]
        )
        now = datetime.now(UTC)
        cards: list[RealtorReferralCardResponse] = []
        for ref in referrals:
            changed_at = ref.pipeline_stage_changed_at
            days_in_stage = (now - changed_at).days if changed_at else 0
            cards.append(
                RealtorReferralCardResponse(
                    referral_id=ref.id,
                    borrower_initials=borrower_initials(names.get(ref.client_id)),
                    pipeline_stage=ref.pipeline_stage,
                    referral_status=ref.status,
                    days_in_stage=days_in_stage,
                    stage_changed_at=changed_at,
                    source_label=ref.source_label,
                    is_own_referral=ref.referred_by_user_id == user.id,
                    created_at=ref.created_at,
                )
            )
        return cards

    async def disable_membership(
        self,
        actor: User,
        partnership_id: uuid.UUID,
        member_id: uuid.UUID,
        *,
        disable_user: bool = False,
    ) -> RealtorSessionResponse:
        self._require_write(actor)
        cro_org_id = self._require_organization(actor)
        partnership = await self._require_realtor_partnership(partnership_id, cro_org_id)

        result = await self._session.execute(
            select(OrgPartnershipMember).where(
                OrgPartnershipMember.id == member_id,
                OrgPartnershipMember.partnership_id == partnership_id,
                OrgPartnershipMember.organization_id == cro_org_id,
                OrgPartnershipMember.deleted_at.is_(None),
            )
        )
        member = result.scalar_one_or_none()
        if member is None or member.partner_role != PartnerRole.REALTOR:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Realtor membership not found",
            )

        member.is_active = False
        apply_audit_on_update(member, actor.id)

        target = await self._session.get(User, member.user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if disable_user:
            target.is_active = False
            apply_audit_on_update(target, actor.id)

        await self._audit(
            cro_organization_id=cro_org_id,
            actor=actor,
            action=PartnerAccessAction.MEMBER_CREATE,
            resource_type="org_partnership_member",
            resource_id=member.id,
            partnership_id=partnership.id,
            detail=f"realtor_membership_disabled disable_user={disable_user}",
        )
        await self._session.commit()
        await self._session.refresh(member)
        partner_name = await self._org_name(partnership.partner_organization_id)
        return self._session_from_membership(target, member, partnership, partner_name)

    async def request_password_reset(
        self, payload: RealtorPasswordResetRequest
    ) -> RealtorPasswordResetRequestResponse:
        email = str(payload.email).strip().lower()
        generic = RealtorPasswordResetRequestResponse(
            detail="If a realtor account exists for that email, a reset link was issued.",
            reset_token=None,
        )
        user = await self._get_user_by_email(email)
        if user is None or not user.is_active:
            return generic

        try:
            _member, partnership = await self._require_active_realtor_membership(user)
        except HTTPException:
            return generic

        raw = _mint_token()
        row = PartnerRealtorCredentialToken(
            id=uuid.uuid4(),
            organization_id=partnership.cro_organization_id,
            user_id=user.id,
            purpose=RealtorCredentialPurpose.PASSWORD_RESET.value,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(UTC) + _RESET_TTL,
        )
        self._session.add(row)
        await self._session.flush()
        await self._audit(
            cro_organization_id=partnership.cro_organization_id,
            actor=user,
            action=PartnerAccessAction.MEMBER_LIST,
            resource_type="partner_realtor_credential_token",
            resource_id=row.id,
            partnership_id=partnership.id,
            detail="realtor_password_reset_requested",
        )
        await self._session.commit()

        settings = get_settings()
        if settings.app_env in {"development", "test"}:
            generic.reset_token = raw
        return generic

    async def confirm_password_reset(
        self, payload: RealtorPasswordResetConfirm
    ) -> RealtorTokenResponse:
        token_hash = _hash_token(payload.token)
        result = await self._session.execute(
            select(PartnerRealtorCredentialToken).where(
                PartnerRealtorCredentialToken.token_hash == token_hash,
                PartnerRealtorCredentialToken.purpose
                == RealtorCredentialPurpose.PASSWORD_RESET.value,
            )
        )
        row = result.scalar_one_or_none()
        if row is None or row.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or used reset token",
            )
        if row.expires_at <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Reset token has expired",
            )

        user = await self._session.get(User, row.user_id)
        if user is None or user.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        member, partnership = await self._require_active_realtor_membership(user)
        user.hashed_password = hash_password(payload.password)
        apply_audit_on_update(user, user.id)
        row.used_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(user)

        partner_name = await self._org_name(partnership.partner_organization_id)
        session = self._session_from_membership(user, member, partnership, partner_name)
        return RealtorTokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
            realtor=session,
        )

    async def _get_invite_by_token(
        self, token: str, *, allow_accepted: bool
    ) -> PartnerRealtorInvite:
        result = await self._session.execute(
            select(PartnerRealtorInvite).where(
                PartnerRealtorInvite.token_hash == _hash_token(token),
                PartnerRealtorInvite.deleted_at.is_(None),
            )
        )
        invite = result.scalar_one_or_none()
        if invite is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
        if invite.accepted_at is not None and not allow_accepted:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invite has already been accepted",
            )
        return invite

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(
                User.email == email.lower(),
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def _require_active_realtor_membership(
        self, user: User
    ) -> tuple[OrgPartnershipMember, OrgPartnership]:
        result = await self._session.execute(
            select(OrgPartnershipMember, OrgPartnership)
            .join(OrgPartnership, OrgPartnership.id == OrgPartnershipMember.partnership_id)
            .where(
                OrgPartnershipMember.user_id == user.id,
                OrgPartnershipMember.partner_role == PartnerRole.REALTOR,
                OrgPartnershipMember.deleted_at.is_(None),
                OrgPartnership.deleted_at.is_(None),
            )
            .order_by(OrgPartnershipMember.created_at.desc())
        )
        row = result.first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No realtor partnership membership for this account",
            )
        member, partnership = row
        if not member.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Realtor membership is disabled",
            )
        if partnership.cro_organization_id != member.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Partnership isolation violation",
            )
        assert partner_role_has_permission(PartnerRole.REALTOR, "partnership.view")
        return member, partnership
