"""Enterprise identity enrollment repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.models import UserSsoEnrollment, UserTotpEnrollment


class EnterpriseEnrollmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_totp_enrollment(self, user_id: uuid.UUID) -> UserTotpEnrollment | None:
        return await self._session.get(UserTotpEnrollment, user_id)

    async def save_totp_enrollment(self, enrollment: UserTotpEnrollment) -> UserTotpEnrollment:
        self._session.add(enrollment)
        await self._session.flush()
        await self._session.refresh(enrollment)
        return enrollment

    async def get_sso_enrollment(
        self,
        user_id: uuid.UUID,
        *,
        provider: str,
    ) -> UserSsoEnrollment | None:
        result = await self._session.execute(
            select(UserSsoEnrollment).where(
                UserSsoEnrollment.user_id == user_id,
                UserSsoEnrollment.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def get_sso_enrollment_by_subject(
        self,
        *,
        provider: str,
        issuer_url: str,
        idp_subject: str,
    ) -> UserSsoEnrollment | None:
        result = await self._session.execute(
            select(UserSsoEnrollment).where(
                UserSsoEnrollment.provider == provider,
                UserSsoEnrollment.issuer_url == issuer_url,
                UserSsoEnrollment.idp_subject == idp_subject,
            )
        )
        return result.scalar_one_or_none()

    async def create_sso_enrollment(
        self,
        *,
        user_id: uuid.UUID,
        provider: str,
        issuer_url: str,
        idp_subject: str,
    ) -> UserSsoEnrollment:
        enrollment = UserSsoEnrollment(
            user_id=user_id,
            provider=provider,
            issuer_url=issuer_url,
            idp_subject=idp_subject,
            linked_at=datetime.now(UTC),
        )
        self._session.add(enrollment)
        await self._session.flush()
        await self._session.refresh(enrollment)
        return enrollment
