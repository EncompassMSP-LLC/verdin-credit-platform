"""Document repository — owns all Document database access."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from api.modules.documents.constants import (
    DocumentProcessingStatus,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.documents.schemas import DocumentSortField, DocumentSortOrder


@dataclass(frozen=True, slots=True)
class DocumentListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    is_duplicate: bool | None = None
    processing_status: DocumentProcessingStatus | None = None
    metadata_status: MetadataStatus | None = None
    resolution_status: ResolutionStatus | None = None
    skip: int = 0
    limit: int = 20
    sort_by: DocumentSortField = "created_at"
    sort_order: DocumentSortOrder = "desc"


_SORT_COLUMNS: dict[DocumentSortField, InstrumentedAttribute[Any]] = {
    "created_at": Document.created_at,
    "title": Document.title,
    "file_name": Document.file_name,
    "file_size": Document.file_size,
}


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        document_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
        include_versions: bool = False,
        include_metadata: bool = True,
    ) -> Document | None:
        uid = uuid.UUID(str(document_id))
        query = select(Document).where(Document.id == uid, Document.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Document.organization_id == organization_id)
        load_options = []
        if include_versions:
            load_options.append(selectinload(Document.versions))
        if include_metadata:
            load_options.append(selectinload(Document.extracted_metadata))
        if load_options:
            query = query.options(*load_options)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_hash(
        self,
        organization_id: uuid.UUID,
        file_hash: str,
    ) -> Document | None:
        result = await self._session.execute(
            select(Document).where(
                Document.organization_id == organization_id,
                Document.file_hash == file_hash,
                Document.deleted_at.is_(None),
                Document.is_duplicate.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_duplicate_group(
        self,
        organization_id: uuid.UUID,
        canonical_document_id: uuid.UUID,
    ) -> list[Document]:
        result = await self._session.execute(
            select(Document)
            .where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                or_(
                    Document.id == canonical_document_id,
                    Document.duplicate_of_id == canonical_document_id,
                ),
            )
            .order_by(Document.is_duplicate.asc(), Document.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_documents(self, filters: DocumentListFilters) -> tuple[list[Document], int]:
        base = select(Document).where(
            Document.organization_id == filters.organization_id,
            Document.deleted_at.is_(None),
        )

        if filters.case_id is not None:
            base = base.where(Document.case_id == filters.case_id)
        if filters.account_id is not None:
            base = base.where(Document.account_id == filters.account_id)
        if filters.is_duplicate is not None:
            base = base.where(Document.is_duplicate == filters.is_duplicate)
        if filters.processing_status is not None:
            base = base.where(Document.processing_status == filters.processing_status.value)
        if filters.metadata_status is not None:
            base = base.join(
                DocumentMetadata,
                DocumentMetadata.document_id == Document.id,
            ).where(DocumentMetadata.metadata_status == filters.metadata_status.value)
        if filters.resolution_status is not None:
            base = base.where(
                exists().where(
                    DocumentEntityResolution.document_id == Document.id,
                    DocumentEntityResolution.resolution_status == filters.resolution_status.value,
                )
            )
        if filters.search:
            term = f"%{filters.search.strip()}%"
            base = base.where(
                or_(
                    Document.title.ilike(term),
                    Document.file_name.ilike(term),
                    Document.description.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()

        result = await self._session.execute(
            base.options(selectinload(Document.extracted_metadata))
            .order_by(order)
            .offset(filters.skip)
            .limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def list_case_document_dates(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[tuple[uuid.UUID | None, datetime]]:
        """(account_id, created_at) for every non-deleted document in a case.

        Lightweight projection used by the §611 reinvestigation clock to detect
        consumer documents supplied during the initial window (the 45-day
        extension signal). Avoids loading full Document rows / metadata.
        """
        result = await self._session.execute(
            select(Document.account_id, Document.created_at).where(
                Document.organization_id == organization_id,
                Document.case_id == case_id,
                Document.deleted_at.is_(None),
            )
        )
        return [(row[0], row[1]) for row in result.all()]

    async def create(self, document: Document) -> Document:
        self._session.add(document)
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self._session.add(version)
        await self._session.flush()
        await self._session.refresh(version)
        return version

    async def update(self, document: Document) -> Document:
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def list_versions(self, document_id: uuid.UUID) -> list[DocumentVersion]:
        result = await self._session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def get_parsed_credit_report(
        self,
        document_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> DocumentParsedCreditReport | None:
        result = await self._session.execute(
            select(DocumentParsedCreditReport).where(
                DocumentParsedCreditReport.document_id == document_id,
                DocumentParsedCreditReport.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_previous_parsed_credit_report(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        bureau: str,
        before_document_id: uuid.UUID,
        before_parsed_at: datetime,
    ) -> DocumentParsedCreditReport | None:
        result = await self._session.execute(
            select(DocumentParsedCreditReport)
            .join(Document, Document.id == DocumentParsedCreditReport.document_id)
            .where(
                DocumentParsedCreditReport.organization_id == organization_id,
                DocumentParsedCreditReport.bureau == bureau,
                DocumentParsedCreditReport.document_id != before_document_id,
                DocumentParsedCreditReport.parsed_at < before_parsed_at,
                Document.case_id == case_id,
                Document.deleted_at.is_(None),
            )
            .order_by(DocumentParsedCreditReport.parsed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_case_parsed_credit_reports(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[DocumentParsedCreditReport]:
        result = await self._session.execute(
            select(DocumentParsedCreditReport)
            .join(Document, Document.id == DocumentParsedCreditReport.document_id)
            .where(
                DocumentParsedCreditReport.organization_id == organization_id,
                Document.case_id == case_id,
                Document.deleted_at.is_(None),
            )
            .order_by(DocumentParsedCreditReport.parsed_at.desc())
        )
        return list(result.scalars().all())

    async def update_tradeline_page_map(
        self,
        document_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        page_map: dict[str, object],
    ) -> DocumentParsedCreditReport | None:
        parsed = await self.get_parsed_credit_report(
            document_id,
            organization_id=organization_id,
        )
        if parsed is None:
            return None
        parsed.tradeline_page_map = page_map
        await self._session.flush()
        await self._session.refresh(parsed)
        return parsed
