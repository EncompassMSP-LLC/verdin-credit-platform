"""Repository for admin-gated SAML certificate rotation runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.saml_cert_rotation_models import (
    SamlCertificateRotationRun,
    SamlCertificateRotationStatus,
)


class SamlCertificateRotationRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class SamlCertificateRotationRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> SamlCertificateRotationRun | None:
        result = await self._session.execute(
            select(SamlCertificateRotationRun).where(SamlCertificateRotationRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        metadata_upload_id: uuid.UUID,
        entity_id: str,
        status: SamlCertificateRotationStatus,
        rotation_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> SamlCertificateRotationRun:
        run = SamlCertificateRotationRun(
            organization_id=organization_id,
            metadata_upload_id=metadata_upload_id,
            entity_id=entity_id,
            status=status,
            rotation_summary=rotation_summary,
            requested_by_user_id=requested_by_user_id,
            requested_at=requested_at,
            error_message=error_message,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def list_runs(
        self,
        organization_id: uuid.UUID,
        filters: SamlCertificateRotationRunListFilters,
    ) -> tuple[list[SamlCertificateRotationRun], int]:
        base = (
            select(SamlCertificateRotationRun)
            .where(SamlCertificateRotationRun.organization_id == organization_id)
            .order_by(SamlCertificateRotationRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(SamlCertificateRotationRun)
            .where(SamlCertificateRotationRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
