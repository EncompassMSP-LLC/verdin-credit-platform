"""Repository for SAML federation metadata uploads."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.enterprise.federation_metadata_models import (
    SamlFederationMetadataUpload,
    SamlMetadataValidationStatus,
)


class SamlFederationMetadataUploadListFilters:
    def __init__(self, *, skip: int, limit: int) -> None:
        self.skip = skip
        self.limit = limit


class SamlFederationMetadataUploadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def utcnow(self) -> datetime:
        return datetime.now(UTC)

    async def create_upload(
        self,
        *,
        organization_id: uuid.UUID,
        metadata_xml: str,
        provider_key: str | None,
        entity_id: str | None,
        validation_status: SamlMetadataValidationStatus,
        validation_message: str | None,
        uploaded_by_user_id: uuid.UUID | None,
        uploaded_at: datetime,
    ) -> SamlFederationMetadataUpload:
        upload = SamlFederationMetadataUpload(
            organization_id=organization_id,
            metadata_xml=metadata_xml,
            provider_key=provider_key,
            entity_id=entity_id,
            validation_status=validation_status,
            validation_message=validation_message,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_at=uploaded_at,
        )
        self._session.add(upload)
        await self._session.flush()
        await self._session.refresh(upload)
        return upload

    async def list_uploads(
        self,
        organization_id: uuid.UUID,
        filters: SamlFederationMetadataUploadListFilters,
    ) -> tuple[list[SamlFederationMetadataUpload], int]:
        base = (
            select(SamlFederationMetadataUpload)
            .where(SamlFederationMetadataUpload.organization_id == organization_id)
            .order_by(SamlFederationMetadataUpload.uploaded_at.desc().nullslast())
        )
        count_result = await self._session.execute(
            select(func.count())
            .select_from(SamlFederationMetadataUpload)
            .where(SamlFederationMetadataUpload.organization_id == organization_id)
        )
        total = int(count_result.scalar_one())
        result = await self._session.execute(base.offset(filters.skip).limit(filters.limit))
        return list(result.scalars().all()), total
