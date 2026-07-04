"""SCIM provisioning repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.models import ScimProvisionLog, ScimResourceType


class ScimProvisioningRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_provision_log(
        self,
        organization_id: uuid.UUID,
        *,
        resource_type: ScimResourceType,
        external_id: str,
    ) -> ScimProvisionLog | None:
        result = await self._session.execute(
            select(ScimProvisionLog).where(
                ScimProvisionLog.organization_id == organization_id,
                ScimProvisionLog.resource_type == resource_type,
                ScimProvisionLog.external_id == external_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_provision_log(self, log: ScimProvisionLog) -> ScimProvisionLog:
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def list_provision_logs(
        self,
        organization_id: uuid.UUID,
        *,
        resource_type: ScimResourceType,
    ) -> list[ScimProvisionLog]:
        result = await self._session.execute(
            select(ScimProvisionLog)
            .where(
                ScimProvisionLog.organization_id == organization_id,
                ScimProvisionLog.resource_type == resource_type,
            )
            .order_by(ScimProvisionLog.created_at.desc())
        )
        return list(result.scalars().all())
