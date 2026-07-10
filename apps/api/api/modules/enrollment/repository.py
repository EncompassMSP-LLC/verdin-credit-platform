"""Client enrollment repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enrollment.models import ClientEnrollment, ClientEnrollmentStatus


class ClientEnrollmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, enrollment_id: uuid.UUID) -> ClientEnrollment | None:
        result = await self._session.execute(
            select(ClientEnrollment).where(ClientEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_checkout_session_id(self, session_id: str) -> ClientEnrollment | None:
        result = await self._session.execute(
            select(ClientEnrollment).where(
                ClientEnrollment.stripe_checkout_session_id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_email(self, email: str) -> ClientEnrollment | None:
        result = await self._session.execute(
            select(ClientEnrollment)
            .where(
                ClientEnrollment.email == email.lower(),
                ClientEnrollment.status.in_(
                    [
                        ClientEnrollmentStatus.PENDING_PAYMENT,
                        ClientEnrollmentStatus.COMPLETED,
                    ]
                ),
            )
            .order_by(ClientEnrollment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def add(self, enrollment: ClientEnrollment) -> ClientEnrollment:
        self._session.add(enrollment)
        await self._session.flush()
        return enrollment

    async def save(self, enrollment: ClientEnrollment) -> ClientEnrollment:
        await self._session.flush()
        return enrollment
