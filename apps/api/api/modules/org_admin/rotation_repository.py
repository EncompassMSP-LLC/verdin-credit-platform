"""API key rotation audit repository."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.org_admin.rotation_models import ApiKeyRotationLog


class ApiKeyRotationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_rotation_log(
        self,
        *,
        organization_id: uuid.UUID,
        previous_api_key_id: uuid.UUID,
        new_api_key_id: uuid.UUID,
        rotated_by_user_id: uuid.UUID | None,
        rotated_at: datetime,
    ) -> ApiKeyRotationLog:
        log = ApiKeyRotationLog(
            organization_id=organization_id,
            previous_api_key_id=previous_api_key_id,
            new_api_key_id=new_api_key_id,
            rotated_by_user_id=rotated_by_user_id,
            rotated_at=rotated_at,
        )
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log
