"""Repository for admin-gated multi-IdP bulk provisioning runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.bulk_idp_provisioning_models import (
    BulkIdpProvisioningRun,
    BulkIdpProvisioningRunStatus,
)


class BulkIdpProvisioningRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class BulkIdpProvisioningRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> BulkIdpProvisioningRun | None:
        result = await self._session.execute(
            select(BulkIdpProvisioningRun).where(BulkIdpProvisioningRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        hris_passwordless_ui_run_id: uuid.UUID,
        entity_id: str,
        status: BulkIdpProvisioningRunStatus,
        provisioning_summary: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> BulkIdpProvisioningRun:
        run = BulkIdpProvisioningRun(
            organization_id=organization_id,
            hris_passwordless_ui_run_id=hris_passwordless_ui_run_id,
            entity_id=entity_id,
            status=status,
            provisioning_summary=provisioning_summary,
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
        filters: BulkIdpProvisioningRunListFilters,
    ) -> tuple[list[BulkIdpProvisioningRun], int]:
        base = (
            select(BulkIdpProvisioningRun)
            .where(BulkIdpProvisioningRun.organization_id == organization_id)
            .order_by(BulkIdpProvisioningRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(BulkIdpProvisioningRun)
            .where(BulkIdpProvisioningRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
