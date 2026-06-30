"""Documents domain schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field
from sqlalchemy import inspect as sa_inspect

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.documents.constants import (
    ClassificationMethod,
    DocumentProcessingStatus,
    DocumentType,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport

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
    processing_status: DocumentProcessingStatus | None = None
    metadata_status: MetadataStatus | None = None
    resolution_status: ResolutionStatus | None = None
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
    processing_status: DocumentProcessingStatus
    ocr_processed_at: datetime | None
    ocr_version_number: int | None
    document_type: DocumentType | None = None
    confidence_score: float | None = None
    classified_at: datetime | None = None
    metadata_status: MetadataStatus | None = None
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
        unloaded = sa_inspect(document).unloaded
        extracted_metadata = (
            document.extracted_metadata if "extracted_metadata" not in unloaded else None
        )
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
            processing_status=DocumentProcessingStatus(document.processing_status),
            ocr_processed_at=document.ocr_processed_at,
            ocr_version_number=document.ocr_version_number,
            document_type=(
                DocumentType(document.document_type) if document.document_type else None
            ),
            confidence_score=float(document.confidence_score)
            if document.confidence_score is not None
            else None,
            classified_at=document.classified_at,
            metadata_status=(
                MetadataStatus(extracted_metadata.metadata_status)
                if extracted_metadata is not None
                else None
            ),
            created_at=document.created_at,
            updated_at=document.updated_at,
            deleted_at=document.deleted_at,
            created_by_id=document.created_by_id,
            updated_by_id=document.updated_by_id,
            versions=versions,
        )


class DocumentDuplicateGroupResponse(BaseSchema):
    document_id: uuid.UUID
    canonical_document: DocumentResponse
    duplicate_documents: list[DocumentResponse]
    duplicate_count: int

    @classmethod
    def from_group(
        cls,
        *,
        document_id: uuid.UUID,
        canonical_document: Document,
        duplicate_documents: list[Document],
    ) -> "DocumentDuplicateGroupResponse":
        return cls(
            document_id=document_id,
            canonical_document=DocumentResponse.from_model(canonical_document),
            duplicate_documents=[
                DocumentResponse.from_model(document) for document in duplicate_documents
            ],
            duplicate_count=len(duplicate_documents),
        )


class DocumentOcrResponse(BaseSchema):
    document_id: uuid.UUID
    processing_status: DocumentProcessingStatus
    ocr_text: str | None
    ocr_error: str | None
    ocr_processed_at: datetime | None
    ocr_version_number: int | None

    @classmethod
    def from_model(cls, document: Document) -> "DocumentOcrResponse":
        return cls(
            document_id=document.id,
            processing_status=DocumentProcessingStatus(document.processing_status),
            ocr_text=document.ocr_text,
            ocr_error=document.ocr_error,
            ocr_processed_at=document.ocr_processed_at,
            ocr_version_number=document.ocr_version_number,
        )


class DocumentClassificationResponse(BaseSchema):
    document_id: uuid.UUID
    document_type: DocumentType | None
    confidence_score: float | None
    classification_method: ClassificationMethod | None
    classified_at: datetime | None
    classified_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, document: Document) -> "DocumentClassificationResponse":
        return cls(
            document_id=document.id,
            document_type=(
                DocumentType(document.document_type) if document.document_type else None
            ),
            confidence_score=float(document.confidence_score)
            if document.confidence_score is not None
            else None,
            classification_method=(
                ClassificationMethod(document.classification_method)
                if document.classification_method
                else None
            ),
            classified_at=document.classified_at,
            classified_by_id=document.classified_by_id,
        )


class DocumentParsedCreditReportResponse(BaseSchema):
    document_id: uuid.UUID
    schema_version: str
    bureau: str
    parser_name: str
    parser_confidence: float
    parsed_report: dict[str, Any]
    is_partial: bool
    warnings: list[str]
    parsed_at: datetime

    @classmethod
    def from_model(
        cls,
        parsed_report: DocumentParsedCreditReport,
    ) -> "DocumentParsedCreditReportResponse":
        return cls(
            document_id=parsed_report.document_id,
            schema_version=parsed_report.schema_version,
            bureau=parsed_report.bureau,
            parser_name=parsed_report.parser_name,
            parser_confidence=float(parsed_report.parser_confidence),
            parsed_report=parsed_report.parsed_report,
            is_partial=parsed_report.is_partial,
            warnings=list(parsed_report.warnings or []),
            parsed_at=parsed_report.parsed_at,
        )
