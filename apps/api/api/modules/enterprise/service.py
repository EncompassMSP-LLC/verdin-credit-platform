"""Enterprise identity enrollment service."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.enterprise import require_enterprise_gateway
from api.core.enterprise_identity import (
    EnterpriseFeatureDisabledError,
    EnterpriseIdentityNotReadyError,
    MfaMode,
    SsoProvider,
    get_enterprise_identity_settings,
)
from api.core.enterprise_oidc import (
    build_oidc_authorization_url,
    create_sso_enrollment_state,
    decode_sso_enrollment_state,
    exchange_oidc_authorization_code,
    fetch_oidc_discovery,
    fetch_oidc_userinfo,
)
from api.core.enterprise_totp import (
    build_totp_provisioning_uri,
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_totp_secret,
    verify_totp_code,
)
from api.modules.auth.models import User
from api.modules.enterprise.models import UserTotpEnrollment
from api.modules.enterprise.repository import EnterpriseEnrollmentRepository
from api.modules.enterprise.schemas import (
    SsoEnrollmentCompleteResponse,
    SsoEnrollmentStartResponse,
    SsoEnrollmentStatusResponse,
    TotpEnrollmentStartResponse,
    TotpEnrollmentStatusResponse,
)


class EnterpriseEnrollmentService:
    def __init__(self, repo: EnterpriseEnrollmentRepository) -> None:
        self._repo = repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> EnterpriseEnrollmentService:
        return cls(EnterpriseEnrollmentRepository(session))

    def _require_mfa_ready(self) -> None:
        try:
            require_enterprise_gateway(require_mfa=True)
        except EnterpriseFeatureDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enterprise features are not enabled",
            ) from exc
        except EnterpriseIdentityNotReadyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Enterprise MFA is not ready", "blockers": exc.blockers},
            ) from exc

    def _require_sso_ready(self) -> None:
        try:
            require_enterprise_gateway(require_sso=True)
        except EnterpriseFeatureDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enterprise features are not enabled",
            ) from exc
        except EnterpriseIdentityNotReadyError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Enterprise SSO is not ready", "blockers": exc.blockers},
            ) from exc

    async def start_totp_enrollment(self, user: User) -> TotpEnrollmentStartResponse:
        self._require_mfa_ready()
        settings = get_enterprise_identity_settings()
        if settings.enterprise_mfa_mode is not MfaMode.TOTP or not settings.enterprise_mfa_issuer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TOTP MFA is not configured",
            )

        existing = await self._repo.get_totp_enrollment(user.id)
        if existing is not None and existing.enrolled_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="TOTP is already enrolled for this user",
            )

        secret = generate_totp_secret()
        encrypted_pending = encrypt_totp_secret(secret)
        if existing is None:
            enrollment = UserTotpEnrollment(
                user_id=user.id,
                pending_encrypted_secret=encrypted_pending,
            )
        else:
            enrollment = existing
            enrollment.pending_encrypted_secret = encrypted_pending
        await self._repo.save_totp_enrollment(enrollment)

        return TotpEnrollmentStartResponse(
            secret=secret,
            otpauth_url=build_totp_provisioning_uri(
                secret=secret,
                account_name=user.email,
                issuer=settings.enterprise_mfa_issuer,
            ),
            issuer=settings.enterprise_mfa_issuer,
        )

    async def confirm_totp_enrollment(self, user: User, code: str) -> TotpEnrollmentStatusResponse:
        self._require_mfa_ready()
        enrollment = await self._repo.get_totp_enrollment(user.id)
        if enrollment is None or not enrollment.pending_encrypted_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pending TOTP enrollment found",
            )

        secret = decrypt_totp_secret(enrollment.pending_encrypted_secret)
        if not verify_totp_code(secret=secret, code=code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP verification code",
            )

        enrollment.encrypted_secret = enrollment.pending_encrypted_secret
        enrollment.pending_encrypted_secret = None
        enrollment.enrolled_at = datetime.now(UTC)
        await self._repo.save_totp_enrollment(enrollment)

        return TotpEnrollmentStatusResponse(
            enrolled=True,
            enrolled_at=enrollment.enrolled_at,
            pending=False,
        )

    async def get_totp_enrollment_status(self, user: User) -> TotpEnrollmentStatusResponse:
        self._require_mfa_ready()
        enrollment = await self._repo.get_totp_enrollment(user.id)
        if enrollment is None:
            return TotpEnrollmentStatusResponse(enrolled=False, pending=False)
        return TotpEnrollmentStatusResponse(
            enrolled=enrollment.enrolled_at is not None,
            enrolled_at=enrollment.enrolled_at,
            pending=enrollment.pending_encrypted_secret is not None,
        )

    async def disable_totp_enrollment(self, user: User) -> TotpEnrollmentStatusResponse:
        self._require_mfa_ready()
        enrollment = await self._repo.get_totp_enrollment(user.id)
        if enrollment is None or enrollment.enrolled_at is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TOTP is not enrolled for this user",
            )
        enrollment.encrypted_secret = None
        enrollment.pending_encrypted_secret = None
        enrollment.enrolled_at = None
        await self._repo.save_totp_enrollment(enrollment)
        return TotpEnrollmentStatusResponse(enrolled=False, pending=False)

    async def start_sso_enrollment(self, user: User) -> SsoEnrollmentStartResponse:
        self._require_sso_ready()
        settings = get_enterprise_identity_settings()
        if settings.enterprise_sso_provider is not SsoProvider.OIDC:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OIDC SSO enrollment is not configured",
            )
        if not settings.enterprise_sso_redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ENTERPRISE_SSO_REDIRECT_URI is not configured",
            )

        existing = await self._repo.get_sso_enrollment(user.id, provider=SsoProvider.OIDC.value)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="OIDC identity is already linked for this user",
            )

        state = create_sso_enrollment_state(user.id)
        authorization_url = build_oidc_authorization_url(
            settings,
            redirect_uri=settings.enterprise_sso_redirect_uri,
            state=state,
        )
        return SsoEnrollmentStartResponse(
            authorization_url=authorization_url,
            state=state,
            provider=SsoProvider.OIDC.value,
        )

    async def complete_sso_enrollment(
        self,
        user: User,
        *,
        code: str,
        state: str,
    ) -> SsoEnrollmentCompleteResponse:
        self._require_sso_ready()
        settings = get_enterprise_identity_settings()
        if settings.enterprise_sso_provider is not SsoProvider.OIDC:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OIDC SSO enrollment is not configured",
            )
        if not settings.enterprise_sso_redirect_uri or not settings.enterprise_sso_issuer_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OIDC SSO is not fully configured",
            )

        try:
            state_user_id = decode_sso_enrollment_state(state)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SSO enrollment state",
            ) from exc
        if state_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SSO enrollment state does not match current user",
            )

        existing = await self._repo.get_sso_enrollment(user.id, provider=SsoProvider.OIDC.value)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="OIDC identity is already linked for this user",
            )

        try:
            discovery = await fetch_oidc_discovery(settings.enterprise_sso_issuer_url)
            token_response = await exchange_oidc_authorization_code(
                settings,
                code=code,
                redirect_uri=settings.enterprise_sso_redirect_uri,
                discovery=discovery,
            )
            userinfo = await fetch_oidc_userinfo(
                discovery,
                access_token=token_response.access_token,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        issuer_url = settings.enterprise_sso_issuer_url.rstrip("/")
        conflict = await self._repo.get_sso_enrollment_by_subject(
            provider=SsoProvider.OIDC.value,
            issuer_url=issuer_url,
            idp_subject=userinfo.subject,
        )
        if conflict is not None and conflict.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="OIDC identity is already linked to another user",
            )

        enrollment = await self._repo.create_sso_enrollment(
            user_id=user.id,
            provider=SsoProvider.OIDC.value,
            issuer_url=issuer_url,
            idp_subject=userinfo.subject,
        )
        return SsoEnrollmentCompleteResponse(
            linked=True,
            provider=enrollment.provider,
            issuer_url=enrollment.issuer_url,
            idp_subject=enrollment.idp_subject,
            linked_at=enrollment.linked_at,
            user_id=enrollment.user_id,
        )

    async def get_sso_enrollment_status(self, user: User) -> SsoEnrollmentStatusResponse:
        self._require_sso_ready()
        settings = get_enterprise_identity_settings()
        enrollment = await self._repo.get_sso_enrollment(
            user.id,
            provider=settings.enterprise_sso_provider.value,
        )
        if enrollment is None:
            return SsoEnrollmentStatusResponse(linked=False)
        return SsoEnrollmentStatusResponse(
            linked=True,
            provider=enrollment.provider,
            issuer_url=enrollment.issuer_url,
            linked_at=enrollment.linked_at,
            idp_subject=enrollment.idp_subject,
        )
