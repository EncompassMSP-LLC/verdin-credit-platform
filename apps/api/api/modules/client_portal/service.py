"""Client portal auth and provisioning services."""

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
from api.core.constants import TOKEN_REALM_PORTAL, TOKEN_TYPE_REFRESH
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.permissions import has_permission
from api.core.security import (
    create_portal_access_token,
    create_portal_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.modules.auth.models import User
from api.modules.client_portal.credential_models import (
    ClientPortalCredentialToken,
    PortalCredentialPurpose,
)
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.repository import ClientPortalUserRepository
from api.modules.client_portal.schemas import (
    ClientPortalInviteActionResponse,
    ClientPortalUserProvision,
    ClientPortalUserResponse,
    ClientPortalUserUpdate,
    PortalAcceptInviteRequest,
    PortalLoginRequest,
    PortalMeResponse,
    PortalPasswordResetConfirm,
    PortalPasswordResetRequest,
    PortalPasswordResetRequestResponse,
    PortalTokenResponse,
)
from api.modules.clients.models import Client
from api.modules.clients.permissions import CLIENT_WRITE_ROLE
from api.modules.clients.repository import ClientRepository

_RESET_TTL = timedelta(hours=1)
_INVITE_TTL = timedelta(days=7)
_INVITE_RESEND_COOLDOWN = timedelta(minutes=2)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mint_token() -> str:
    return secrets.token_urlsafe(32)


class ClientPortalAuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._portal_users = ClientPortalUserRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalAuthService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def login(self, credentials: PortalLoginRequest) -> PortalTokenResponse:
        self._require_enabled()
        portal_user = await self._portal_users.get_by_email(credentials.email)
        if portal_user is None or not verify_password(
            credentials.password,
            portal_user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        portal_user.last_login_at = datetime.now(UTC)
        await self._portal_users.save(portal_user)
        await self._session.commit()

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def refresh(self, refresh_token: str) -> PortalTokenResponse:
        self._require_enabled()
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        if payload.get("realm") != TOKEN_REALM_PORTAL:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        portal_user = await self._portal_users.get_by_id(payload["sub"])
        if portal_user is None or not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def get_me(self, portal_user: ClientPortalUser) -> PortalMeResponse:
        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return PortalMeResponse(
            id=portal_user.id,
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
            email=portal_user.email,
            client_display_name=client.display_name,
            is_active=portal_user.is_active,
            last_login_at=portal_user.last_login_at,
        )

    async def request_password_reset(
        self,
        payload: PortalPasswordResetRequest,
    ) -> PortalPasswordResetRequestResponse:
        """Issue a one-time reset token. Always returns a generic detail (no email enumeration)."""
        self._require_enabled()
        email = str(payload.email).strip().lower()
        generic = PortalPasswordResetRequestResponse(
            detail=(
                "If a portal account exists for that email, a password reset link was issued. "
                "Check with your case manager if you do not receive instructions."
            ),
            reset_token=None,
        )
        portal_user = await self._portal_users.get_by_email(email)
        if portal_user is None or not portal_user.is_active:
            return generic

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            return generic

        raw = _mint_token()
        row = ClientPortalCredentialToken(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
            purpose=PortalCredentialPurpose.PASSWORD_RESET.value,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(UTC) + _RESET_TTL,
        )
        self._session.add(row)
        await self._session.commit()

        settings = get_settings()
        if settings.app_env in {"development", "test"}:
            generic.reset_token = raw
        return generic

    async def confirm_password_reset(
        self,
        payload: PortalPasswordResetConfirm,
    ) -> PortalTokenResponse:
        self._require_enabled()
        token_hash = _hash_token(payload.token)
        result = await self._session.execute(
            select(ClientPortalCredentialToken).where(
                ClientPortalCredentialToken.token_hash == token_hash,
                ClientPortalCredentialToken.purpose == PortalCredentialPurpose.PASSWORD_RESET.value,
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

        portal_user = await self._portal_users.get_by_id(str(row.portal_user_id))
        if portal_user is None or not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal account not found",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        portal_user.hashed_password = hash_password(payload.password)
        portal_user.last_login_at = datetime.now(UTC)
        apply_audit_on_update(portal_user, None)
        row.used_at = datetime.now(UTC)
        await self._portal_users.save(portal_user)
        await self._session.commit()

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def accept_invite(
        self,
        payload: PortalAcceptInviteRequest,
    ) -> PortalTokenResponse:
        """Complete a staff-issued portal invite by setting a password (LRP-301B)."""
        self._require_enabled()
        token_hash = _hash_token(payload.token)
        result = await self._session.execute(
            select(ClientPortalCredentialToken).where(
                ClientPortalCredentialToken.token_hash == token_hash,
                ClientPortalCredentialToken.purpose == PortalCredentialPurpose.INVITE.value,
            )
        )
        row = result.scalar_one_or_none()
        if row is None or row.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or used invite token",
            )
        if row.expires_at <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Invite token has expired",
            )

        portal_user = await self._portal_users.get_by_id(str(row.portal_user_id))
        if portal_user is None or not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal account not found",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        portal_user.hashed_password = hash_password(payload.password)
        portal_user.last_login_at = datetime.now(UTC)
        apply_audit_on_update(portal_user, None)
        row.used_at = datetime.now(UTC)
        await self._portal_users.save(portal_user)

        from api.core.events import publish_platform_event
        from api.modules.timeline.builders import portal_invite_accepted_event

        case_id = await self._resolve_primary_case_id(
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
        )
        await publish_platform_event(
            self._session,
            portal_invite_accepted_event(
                portal_user=portal_user,
                case_id=case_id,
                token_id=row.id,
            ),
        )
        await self._session.commit()

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def _resolve_primary_case_id(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> uuid.UUID | None:
        from api.modules.cases.models import Case

        result = await self._session.execute(
            select(Case.id)
            .where(
                Case.organization_id == organization_id,
                Case.client_id == client_id,
                Case.deleted_at.is_(None),
            )
            .order_by(Case.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class ClientPortalProvisioningService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._portal_users = ClientPortalUserRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> ClientPortalProvisioningService:
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage client portal access",
            )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    async def _get_client_for_user(self, client_id: uuid.UUID, user: User) -> Client:
        organization_id = self._require_organization(user)
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    async def provision_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientPortalUserProvision,
    ) -> ClientPortalInviteActionResponse:
        self._require_enabled()
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        existing_for_client = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if existing_for_client is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portal access already exists for this client",
            )

        existing_email = await self._portal_users.get_by_email(data.email)
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered for portal access",
            )

        # Never email a password. Staff may optionally set one; otherwise mint unusable random.
        initial_password = data.password or secrets.token_urlsafe(32)
        portal_user = ClientPortalUser(
            organization_id=client.organization_id,
            client_id=client.id,
            email=str(data.email).strip().lower(),
            hashed_password=hash_password(initial_password),
            is_active=True,
        )
        apply_audit_on_create(portal_user, user.id)
        await self._portal_users.add(portal_user)
        await self._session.flush()

        invite_token: str | None = None
        invitation_queued = False
        detail = "Portal access provisioned."
        if data.send_invite:
            invite_token, invitation_queued = await self._issue_invite(
                portal_user=portal_user,
                client=client,
                triggered_by=user,
            )
            detail = (
                "Portal access provisioned and invitation issued. "
                "No password was emailed — the borrower sets a password via the invite link."
            )

        await self._session.commit()
        await self._session.refresh(portal_user)
        return ClientPortalInviteActionResponse.from_provision(
            portal_user,
            detail=detail,
            invitation_queued=invitation_queued,
            invite_token=invite_token,
            invitation_pending=portal_user.last_login_at is None and data.send_invite,
        )

    async def resend_invite(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientPortalInviteActionResponse:
        self._require_enabled()
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )
        if not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portal access is inactive",
            )
        if portal_user.last_login_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portal user has already activated — use password reset instead",
            )

        recent = await self._latest_invite_token(portal_user.id)
        if (
            recent is not None
            and recent.created_at
            and datetime.now(UTC) - recent.created_at < _INVITE_RESEND_COOLDOWN
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Invite was recently sent — wait before resending",
            )

        invite_token, invitation_queued = await self._issue_invite(
            portal_user=portal_user,
            client=client,
            triggered_by=user,
        )
        await self._session.commit()
        await self._session.refresh(portal_user)
        return ClientPortalInviteActionResponse.from_provision(
            portal_user,
            detail="Portal invitation resent. No password was emailed.",
            invitation_queued=invitation_queued,
            invite_token=invite_token,
            invitation_pending=True,
        )

    async def _latest_invite_token(
        self,
        portal_user_id: uuid.UUID,
    ) -> ClientPortalCredentialToken | None:
        result = await self._session.execute(
            select(ClientPortalCredentialToken)
            .where(
                ClientPortalCredentialToken.portal_user_id == portal_user_id,
                ClientPortalCredentialToken.purpose == PortalCredentialPurpose.INVITE.value,
            )
            .order_by(ClientPortalCredentialToken.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _has_pending_invite(self, portal_user_id: uuid.UUID) -> bool:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(ClientPortalCredentialToken.id)
            .where(
                ClientPortalCredentialToken.portal_user_id == portal_user_id,
                ClientPortalCredentialToken.purpose == PortalCredentialPurpose.INVITE.value,
                ClientPortalCredentialToken.used_at.is_(None),
                ClientPortalCredentialToken.expires_at > now,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _invalidate_unused_invites(self, portal_user_id: uuid.UUID) -> None:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(ClientPortalCredentialToken).where(
                ClientPortalCredentialToken.portal_user_id == portal_user_id,
                ClientPortalCredentialToken.purpose == PortalCredentialPurpose.INVITE.value,
                ClientPortalCredentialToken.used_at.is_(None),
            )
        )
        for row in result.scalars().all():
            row.used_at = now

    async def _issue_invite(
        self,
        *,
        portal_user: ClientPortalUser,
        client: Client,
        triggered_by: User,
    ) -> tuple[str | None, bool]:
        await self._invalidate_unused_invites(portal_user.id)
        raw = _mint_token()
        row = ClientPortalCredentialToken(
            organization_id=portal_user.organization_id,
            portal_user_id=portal_user.id,
            purpose=PortalCredentialPurpose.INVITE.value,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(UTC) + _INVITE_TTL,
        )
        self._session.add(row)
        await self._session.flush()

        settings = get_settings()
        accept_url = (
            f"{settings.lrp_portal_base_url.rstrip('/')}/portal/accept-invite" f"?token={raw}"
        )
        invitation_queued = False
        try:
            from api.modules.notifications.notification_matrix import (
                NotificationMatrixEvent,
                advisory_footer,
            )
            from api.modules.notifications.notification_matrix_service import (
                MatrixDispatchContext,
                NotificationMatrixDispatcher,
            )

            matrix = NotificationMatrixDispatcher(self._session)
            footer = advisory_footer()
            await matrix.dispatch(
                NotificationMatrixEvent.PORTAL_INVITE,
                MatrixDispatchContext(
                    organization_id=portal_user.organization_id,
                    entity_type="client_portal_credential_token",
                    entity_id=row.id,
                    title="You're invited to the borrower portal",
                    body=(
                        f"Hello {client.display_name}, your readiness partner invited you to "
                        f"the secure borrower portal. Use this link to set your password "
                        f"(expires in 7 days): {accept_url}. "
                        f"No temporary password was sent. {footer}"
                    ),
                    action_url=accept_url,
                    borrower_email=portal_user.email,
                    borrower_name=client.display_name,
                    triggered_by_user_id=triggered_by.id,
                    source_module="client_portal.invite",
                    create_crm_tasks=False,
                ),
            )
            invitation_queued = True
        except Exception:
            # Provider/matrix failures must not roll back provisioning; staff can resend.
            invitation_queued = False

        from api.core.events import publish_platform_event
        from api.modules.timeline.builders import portal_user_invited_event

        case_id = await self._resolve_primary_case_id(
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
        )
        await publish_platform_event(
            self._session,
            portal_user_invited_event(
                portal_user=portal_user,
                performed_by=triggered_by.id,
                case_id=case_id,
                token_id=row.id,
                invitation_queued=invitation_queued,
            ),
        )

        expose = settings.app_env in {"development", "test"}
        return (raw if expose else None, invitation_queued)

    async def _resolve_primary_case_id(
        self,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
    ) -> uuid.UUID | None:
        from api.modules.cases.models import Case

        result = await self._session.execute(
            select(Case.id)
            .where(
                Case.organization_id == organization_id,
                Case.client_id == client_id,
                Case.deleted_at.is_(None),
            )
            .order_by(Case.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientPortalUserResponse:
        self._require_enabled()
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )
        pending = portal_user.last_login_at is None and await self._has_pending_invite(
            portal_user.id
        )
        return ClientPortalUserResponse.from_model(
            portal_user,
            invitation_pending=pending,
        )

    async def update_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientPortalUserUpdate,
    ) -> ClientPortalUserResponse:
        self._require_enabled()
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )

        updates = data.model_dump(exclude_unset=True)
        if "email" in updates and updates["email"] is not None:
            email = str(updates["email"])
            existing = await self._portal_users.get_by_email(email)
            if existing is not None and existing.id != portal_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered for portal access",
                )
            updates["email"] = email
        if "password" in updates and updates["password"] is not None:
            updates["hashed_password"] = hash_password(updates.pop("password"))

        for key, value in updates.items():
            setattr(portal_user, key, value)
        apply_audit_on_update(portal_user, user.id)
        await self._portal_users.save(portal_user)
        await self._session.commit()
        await self._session.refresh(portal_user)
        return ClientPortalUserResponse.from_model(portal_user)

    async def revoke_portal_user(self, user: User, client_id: uuid.UUID) -> None:
        self._require_write(user)
        self._require_enabled()
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )
        portal_user.soft_delete()
        apply_audit_on_update(portal_user, user.id)
        await self._portal_users.save(portal_user)
        await self._session.commit()
