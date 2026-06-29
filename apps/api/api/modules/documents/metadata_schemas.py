"""Document metadata and entity resolution schemas."""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.documents.constants import (
    ExtractionMethod,
    MatchedEntityType,
    MetadataStatus,
    ResolutionMethod,
    ResolutionStatus,
)
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata

MetadataSortField = Literal["created_at", "title", "file_name", "file_size"]


class DocumentMetadataResponse(BaseSchema):
    document_id: uuid.UUID
    consumer_name: str | None
    bureau: str | None
    creditor: str | None
    collection_agency: str | None
    account_number_masked: str | None
    report_date: date | None
    open_date: date | None
    balance: float | None
    payment_status: str | None
    addresses: list[str]
    phone_numbers: list[str]
    ssn_masked: str | None
    confidence_score: float | None
    extraction_method: ExtractionMethod
    metadata_status: MetadataStatus
    extracted_at: datetime | None
    extraction_error: str | None

    @classmethod
    def from_model(cls, metadata: DocumentMetadata) -> "DocumentMetadataResponse":
        return cls(
            document_id=metadata.document_id,
            consumer_name=metadata.consumer_name,
            bureau=metadata.bureau,
            creditor=metadata.creditor,
            collection_agency=metadata.collection_agency,
            account_number_masked=metadata.account_number_masked,
            report_date=metadata.report_date,
            open_date=metadata.open_date,
            balance=float(metadata.balance) if metadata.balance is not None else None,
            payment_status=metadata.payment_status,
            addresses=list(metadata.addresses or []),
            phone_numbers=list(metadata.phone_numbers or []),
            ssn_masked=metadata.ssn_masked,
            confidence_score=float(metadata.confidence_score)
            if metadata.confidence_score is not None
            else None,
            extraction_method=ExtractionMethod(metadata.extraction_method),
            metadata_status=MetadataStatus(metadata.metadata_status),
            extracted_at=metadata.extracted_at,
            extraction_error=metadata.extraction_error,
        )


class DocumentEntityResolutionResponse(BaseSchema):
    id: uuid.UUID
    document_id: uuid.UUID
    entity_type: MatchedEntityType
    matched_entity_id: uuid.UUID | None
    confidence_score: float
    resolution_status: ResolutionStatus
    resolution_method: ResolutionMethod
    reasoning: str | None
    candidate_entity_ids: list[uuid.UUID]
    reviewed_at: datetime | None
    reviewed_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, resolution: DocumentEntityResolution) -> "DocumentEntityResolutionResponse":
        return cls(
            id=resolution.id,
            document_id=resolution.document_id,
            entity_type=MatchedEntityType(resolution.entity_type),
            matched_entity_id=resolution.matched_entity_id,
            confidence_score=float(resolution.confidence_score),
            resolution_status=ResolutionStatus(resolution.resolution_status),
            resolution_method=ResolutionMethod(resolution.resolution_method),
            reasoning=resolution.reasoning,
            candidate_entity_ids=[
                uuid.UUID(value) for value in (resolution.candidate_entity_ids or [])
            ],
            reviewed_at=resolution.reviewed_at,
            reviewed_by_id=resolution.reviewed_by_id,
        )


class DocumentResolutionsResponse(BaseSchema):
    document_id: uuid.UUID
    resolutions: list[DocumentEntityResolutionResponse]


class ResolutionConfirmRequest(BaseSchema):
    matched_entity_id: uuid.UUID | None = None


class ResolutionRejectRequest(BaseSchema):
    reason: str | None = Field(default=None, max_length=500)
