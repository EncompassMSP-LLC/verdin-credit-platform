"""Repository for admin-gated native mobile passkey client runs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.native_mobile_passkey_client_models import (
    NativeMobilePasskeyClientRun,
    NativeMobilePasskeyClientRunStatus,
)


class NativeMobilePasskeyClientRunListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class NativeMobilePasskeyClientRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def get_run_by_id(self, run_id: uuid.UUID) -> NativeMobilePasskeyClientRun | None:
        result = await self._session.execute(
            select(NativeMobilePasskeyClientRun).where(NativeMobilePasskeyClientRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def create_run(
        self,
        *,
        organization_id: uuid.UUID,
        mobile_passkey_readiness_run_id: uuid.UUID,
        entity_id: str,
        status: NativeMobilePasskeyClientRunStatus,
        client_summary: str,
        platform: str,
        requested_by_user_id: uuid.UUID | None,
        requested_at: datetime | None = None,
        error_message: str | None = None,
    ) -> NativeMobilePasskeyClientRun:
        run = NativeMobilePasskeyClientRun(
            organization_id=organization_id,
            mobile_passkey_readiness_run_id=mobile_passkey_readiness_run_id,
            entity_id=entity_id,
            status=status,
            client_summary=client_summary,
            platform=platform,
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
        filters: NativeMobilePasskeyClientRunListFilters,
    ) -> tuple[list[NativeMobilePasskeyClientRun], int]:
        base = (
            select(NativeMobilePasskeyClientRun)
            .where(NativeMobilePasskeyClientRun.organization_id == organization_id)
            .order_by(NativeMobilePasskeyClientRun.requested_at.desc().nullslast())
        )
        count_query = (
            select(func.count())
            .select_from(NativeMobilePasskeyClientRun)
            .where(NativeMobilePasskeyClientRun.organization_id == organization_id)
        )
        total = int((await self._session.execute(count_query)).scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
