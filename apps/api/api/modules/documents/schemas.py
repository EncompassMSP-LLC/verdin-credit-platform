"""Documents domain schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.documents.models import Document, DocumentVersion

DocumentSortField = Literal["created_at", "title", "file_name", "file_size"]
DocumentSortOrder = Literal["asc", "desc"]


class DocumentUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    account_id: uuid.UUID | None = None


class DocumentListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    is_duplicate: bool | None = None
    sort_by: DocumentSortField = "created_at"
    sort_order: DocumentSortOrder = "desc"


class DocumentVersionResponse(BaseSchema):
    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    file_name: str
    mime_type: str | None
    file_size: int | None
    file_hash: str
    created_at: datetime
    created_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, version: DocumentVersion) -> "DocumentVersionResponse":
        return cls(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            file_name=version.file_name,
            mime_type=version.mime_type,
            file_size=version.file_size,
            file_hash=version.file_hash,
            created_at=version.created_at,
            created_by_id=version.created_by_id,
        )


class DocumentResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID
    account_id: uuid.UUID | None
    title: str
    description: str | None
    file_name: str
    mime_type: str | None
    file_size: int | None
    file_hash: str
    version_number: int
    is_duplicate: bool
    duplicate_of_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None
    versions: list[DocumentVersionResponse] = Field(default_factory=list)

    @classmethod
    def from_model(
        cls,
        document: Document,
        *,
        include_versions: bool = False,
    ) -> "DocumentResponse":
        versions: list[DocumentVersionResponse] = []
        if include_versions and document.versions:
            versions = [DocumentVersionResponse.from_model(v) for v in document.versions]
        return cls(
            id=document.id,
            organization_id=document.organization_id,
            case_id=document.case_id,
            account_id=document.account_id,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            mime_type=document.mime_type,
            file_size=document.file_size,
            file_hash=document.file_hash,
            version_number=document.version_number,
            is_duplicate=document.is_duplicate,
            duplicate_of_id=document.duplicate_of_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            deleted_at=document.deleted_at,
            created_by_id=document.created_by_id,
            updated_by_id=document.updated_by_id,
            versions=versions,
        )
