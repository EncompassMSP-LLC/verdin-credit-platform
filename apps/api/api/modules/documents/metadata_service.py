"""Document metadata extraction and entity resolution operations."""

import uuid
from datetime import UTC, datetime

from verdin_document_metadata import ExtractionContext, extract_metadata
from verdin_document_metadata.base import ExtractedMetadata
from verdin_entity_resolution import (
    AccountCandidate,
    CaseCandidate,
    EntityResolutionResult,
    ResolutionContext,
    resolve_entities,
)

from api.modules.accounts.repository import AccountRepository
from api.modules.cases.repository import CaseListFilters, CaseRepository
from api.modules.documents.constants import (
    ExtractionMethod,
    MatchedEntityType,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata
from api.modules.documents.metadata_repository import (
    DocumentMetadataRepository,
    parse_optional_date,
)
from api.modules.documents.metadata_schemas import (
    DocumentEntityResolutionResponse,
    DocumentMetadataResponse,
    DocumentResolutionsResponse,
)
from api.modules.documents.models import Document


def _build_extraction_context(document: Document) -> ExtractionContext:
    return ExtractionContext(
        ocr_text=document.ocr_text,
        file_name=document.file_name,
        title=document.title,
        document_type=document.document_type,
    )


def _metadata_from_extraction(document: Document, extracted: ExtractedMetadata) -> DocumentMetadata:
    return DocumentMetadata(
        id=uuid.uuid4(),
        document_id=document.id,
        organization_id=document.organization_id,
        consumer_name=extracted.consumer_name,
        bureau=extracted.bureau,
        creditor=extracted.creditor,
        collection_agency=extracted.collection_agency,
        account_number_masked=extracted.account_number_masked,
        report_date=parse_optional_date(extracted.report_date),
        open_date=parse_optional_date(extracted.open_date),
        balance=extracted.balance,
        payment_status=extracted.payment_status,
        addresses=list(extracted.addresses),
        phone_numbers=list(extracted.phone_numbers),
        ssn_masked=extracted.ssn_masked,
        confidence_score=extracted.confidence_score,
        extraction_method=ExtractionMethod.RULES.value,
        metadata_status=MetadataStatus.EXTRACTED.value,
        extracted_at=datetime.now(UTC),
        extraction_error=None,
    )


def _resolution_rows(
    document: Document,
    results: list[EntityResolutionResult],
) -> list[DocumentEntityResolution]:
    rows: list[DocumentEntityResolution] = []
    for result in results:
        matched_id = uuid.UUID(result.matched_entity_id) if result.matched_entity_id else None
        rows.append(
            DocumentEntityResolution(
                id=uuid.uuid4(),
                document_id=document.id,
                organization_id=document.organization_id,
                entity_type=result.entity_type.value,
                matched_entity_id=matched_id,
                confidence_score=result.confidence_score,
                resolution_status=result.resolution_status.value,
                resolution_method=result.resolution_method.value,
                reasoning=result.reasoning,
                candidate_entity_ids=list(result.candidate_entity_ids),
            )
        )
    return rows


async def run_metadata_extraction(
    document: Document,
    metadata_repo: DocumentMetadataRepository,
) -> DocumentMetadataResponse:
    extracted = extract_metadata(_build_extraction_context(document))
    metadata = await metadata_repo.upsert_metadata(_metadata_from_extraction(document, extracted))
    return DocumentMetadataResponse.from_model(metadata)


async def run_entity_resolution(
    document: Document,
    metadata_repo: DocumentMetadataRepository,
    case_repo: CaseRepository,
    account_repo: AccountRepository,
) -> DocumentResolutionsResponse:
    metadata = await metadata_repo.get_metadata_by_document(
        document.id,
        organization_id=document.organization_id,
    )
    if metadata is None or metadata.metadata_status != MetadataStatus.EXTRACTED.value:
        raise ValueError("Metadata must be extracted before entity resolution")

    cases, _ = await case_repo.list_cases(
        CaseListFilters(organization_id=document.organization_id, limit=200)
    )
    accounts, _ = await account_repo.list_by_case(
        document.case_id,
        document.organization_id,
        limit=200,
    )

    context = ResolutionContext(
        organization_id=str(document.organization_id),
        document_case_id=str(document.case_id),
        metadata=metadata.as_resolution_metadata(),
        cases=tuple(
            CaseCandidate(
                id=str(case.id),
                client_name=case.client_name,
                case_number=case.case_number,
            )
            for case in cases
        ),
        accounts=tuple(
            AccountCandidate(
                id=str(account.id),
                creditor_name=account.creditor_name,
                account_number_masked=account.account_number_masked,
                bureau=account.bureau.value,
                balance=float(account.balance) if account.balance is not None else None,
            )
            for account in accounts
        ),
    )

    results = resolve_entities(context)
    saved = await metadata_repo.replace_resolutions(
        document.id,
        document.organization_id,
        _resolution_rows(document, results),
    )

    account_resolution = next(
        (row for row in saved if row.entity_type == MatchedEntityType.ACCOUNT.value),
        None,
    )
    if (
        account_resolution is not None
        and account_resolution.resolution_status == ResolutionStatus.MATCHED.value
        and account_resolution.matched_entity_id is not None
    ):
        document.account_id = account_resolution.matched_entity_id

    return DocumentResolutionsResponse(
        document_id=document.id,
        resolutions=[DocumentEntityResolutionResponse.from_model(row) for row in saved],
    )
