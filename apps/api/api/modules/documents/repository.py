"""Document repository — owns all Document database access."""

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from api.modules.documents.constants import (
    ClassificationStatus,
    DocumentProcessingStatus,
    DocumentType,
)
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.schemas import DocumentSortField, DocumentSortOrder


@dataclass(frozen=True, slots=True)
class DocumentListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    is_duplicate: bool | None = None
    processing_status: DocumentProcessingStatus | None = None
    document_type: DocumentType | None = None
    classification_status: ClassificationStatus | None = None
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
    ) -> Document | None:
        uid = uuid.UUID(str(document_id))
        query = select(Document).where(Document.id == uid, Document.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Document.organization_id == organization_id)
        if include_versions:
            query = query.options(selectinload(Document.versions))
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
        if filters.document_type is not None:
            base = base.where(Document.document_type == filters.document_type.value)
        if filters.classification_status == ClassificationStatus.UNCLASSIFIED:
            base = base.where(Document.document_type.is_(None))
        elif filters.classification_status == ClassificationStatus.UNKNOWN:
            base = base.where(Document.document_type == DocumentType.UNKNOWN.value)
        elif filters.classification_status == ClassificationStatus.CLASSIFIED:
            base = base.where(
                Document.document_type.is_not(None),
                Document.document_type != DocumentType.UNKNOWN.value,
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
            base.order_by(order).offset(filters.skip).limit(filters.limit)
        )
        return list(result.scalars().all()), total

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
