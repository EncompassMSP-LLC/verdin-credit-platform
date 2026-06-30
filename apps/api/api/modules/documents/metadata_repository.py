"""Document metadata and entity resolution repository."""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata


class DocumentMetadataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_metadata_by_document(
        self,
        document_id: uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> DocumentMetadata | None:
        query = select(DocumentMetadata).where(DocumentMetadata.document_id == document_id)
        if organization_id is not None:
            query = query.where(DocumentMetadata.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def upsert_metadata(self, metadata: DocumentMetadata) -> DocumentMetadata:
        existing = await self.get_metadata_by_document(metadata.document_id)
        now = datetime.now(UTC)
        if existing is None:
            metadata.created_at = now
            metadata.updated_at = now
            self._session.add(metadata)
        else:
            for field in (
                "consumer_name",
                "bureau",
                "creditor",
                "collection_agency",
                "account_number_masked",
                "report_date",
                "open_date",
                "balance",
                "payment_status",
                "addresses",
                "phone_numbers",
                "ssn_masked",
                "confidence_score",
                "extraction_method",
                "metadata_status",
                "extracted_at",
                "extraction_error",
            ):
                setattr(existing, field, getattr(metadata, field))
            existing.updated_at = now
            metadata = existing
        await self._session.flush()
        await self._session.refresh(metadata)
        return metadata

    async def list_resolutions(
        self,
        document_id: uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> list[DocumentEntityResolution]:
        query = select(DocumentEntityResolution).where(
            DocumentEntityResolution.document_id == document_id
        )
        if organization_id is not None:
            query = query.where(DocumentEntityResolution.organization_id == organization_id)
        result = await self._session.execute(query.order_by(DocumentEntityResolution.entity_type))
        return list(result.scalars().all())

    async def get_resolution(
        self,
        resolution_id: uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> DocumentEntityResolution | None:
        query = select(DocumentEntityResolution).where(DocumentEntityResolution.id == resolution_id)
        if organization_id is not None:
            query = query.where(DocumentEntityResolution.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def replace_resolutions(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        resolutions: list[DocumentEntityResolution],
    ) -> list[DocumentEntityResolution]:
        existing = await self.list_resolutions(document_id, organization_id=organization_id)
        for row in existing:
            await self._session.delete(row)
        await self._session.flush()

        now = datetime.now(UTC)
        saved: list[DocumentEntityResolution] = []
        for resolution in resolutions:
            resolution.created_at = now
            resolution.updated_at = now
            self._session.add(resolution)
            saved.append(resolution)
        await self._session.flush()
        for resolution in saved:
            await self._session.refresh(resolution)
        return saved

    async def update_resolution(
        self, resolution: DocumentEntityResolution
    ) -> DocumentEntityResolution:
        resolution.updated_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(resolution)
        return resolution


def parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
