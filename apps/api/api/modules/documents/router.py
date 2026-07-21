"""Document management endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.documents.batch_summary_dependencies import require_batch_llm_summaries_enabled
from api.modules.documents.batch_summary_schemas import (
    BatchDocumentSummaryEnqueueResponse,
    BatchDocumentSummaryRunListParams,
    BatchDocumentSummaryRunRequest,
    BatchDocumentSummaryRunResponse,
    BatchLlmSummaryStatusResponse,
)
from api.modules.documents.batch_summary_service import BatchDocumentSummaryService
from api.modules.documents.constants import (
    DocumentProcessingStatus,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.llm_summary import DocumentLlmSummaryService
from api.modules.documents.metadata_schemas import (
    DocumentMetadataResponse,
    DocumentResolutionsResponse,
    ResolutionConfirmRequest,
    ResolutionRejectRequest,
)
from api.modules.documents.schemas import (
    DocumentClassificationResponse,
    DocumentCreditReportReparseResponse,
    DocumentDuplicateGroupResponse,
    DocumentFcraFindingsResponse,
    DocumentIdentityTheftFindingsResponse,
    DocumentListParams,
    DocumentLlmSummaryResponse,
    DocumentMetro2FindingsResponse,
    DocumentOcrResponse,
    DocumentParsedCreditReportAccountCandidatesResponse,
    DocumentParsedCreditReportComparisonResponse,
    DocumentParsedCreditReportResponse,
    DocumentResponse,
    DocumentSortField,
    DocumentSortOrder,
    DocumentUpdate,
    DocumentVersionResponse,
    ImportParsedReportAccountsRequest,
    ImportParsedReportAccountsResponse,
)
from api.modules.documents.service import DocumentService
from api.modules.documents.storage import DocumentStorage, get_document_storage
from api.modules.tasks.schemas import TaskResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_storage() -> DocumentStorage:
    return get_document_storage()


def get_document_service(
    db: AsyncSession = Depends(get_db),
    storage: DocumentStorage = Depends(get_storage),
) -> DocumentService:
    return DocumentService.from_session(db, storage)


def get_document_llm_summary_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentLlmSummaryService:
    return DocumentLlmSummaryService.from_session(db)


def get_batch_document_summary_service(
    db: AsyncSession = Depends(get_db),
) -> BatchDocumentSummaryService:
    return BatchDocumentSummaryService.from_session(db)


def get_document_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    is_duplicate: bool | None = None,
    processing_status: DocumentProcessingStatus | None = None,
    metadata_status: MetadataStatus | None = None,
    resolution_status: ResolutionStatus | None = None,
    sort_by: DocumentSortField = "created_at",
    sort_order: DocumentSortOrder = "desc",
) -> DocumentListParams:
    return DocumentListParams(
        page=page,
        page_size=page_size,
        search=search,
        case_id=case_id,
        account_id=account_id,
        is_duplicate=is_duplicate,
        processing_status=processing_status,
        metadata_status=metadata_status,
        resolution_status=resolution_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    case_id: uuid.UUID = Form(...),
    description: str | None = Form(None),
    account_id: uuid.UUID | None = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.upload_document(
        current_user,
        file=file,
        title=title,
        case_id=case_id,
        description=description,
        account_id=account_id,
    )


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    params: DocumentListParams = Depends(get_document_list_params),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> PaginatedResponse[DocumentResponse]:
    return await service.list_documents(current_user, params)


@router.get(
    "/batch-llm-summaries/status",
    response_model=BatchLlmSummaryStatusResponse,
    dependencies=[Depends(require_batch_llm_summaries_enabled)],
)
async def get_batch_llm_summary_status(
    current_user: User = Depends(get_current_user),
    service: BatchDocumentSummaryService = Depends(get_batch_document_summary_service),
) -> BatchLlmSummaryStatusResponse:
    return await service.get_status(current_user)


@router.get(
    "/batch-llm-summaries/runs",
    response_model=PaginatedResponse[BatchDocumentSummaryRunResponse],
    dependencies=[Depends(require_batch_llm_summaries_enabled)],
)
async def list_batch_document_summary_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: BatchDocumentSummaryService = Depends(get_batch_document_summary_service),
) -> PaginatedResponse[BatchDocumentSummaryRunResponse]:
    params = BatchDocumentSummaryRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@router.post(
    "/batch-llm-summaries/run",
    response_model=BatchDocumentSummaryEnqueueResponse,
    dependencies=[Depends(require_batch_llm_summaries_enabled)],
)
async def enqueue_batch_document_summary_run(
    body: BatchDocumentSummaryRunRequest,
    current_user: User = Depends(get_current_user),
    service: BatchDocumentSummaryService = Depends(get_batch_document_summary_service),
) -> BatchDocumentSummaryEnqueueResponse:
    return await service.enqueue_batch_run(current_user, body)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.get_document(current_user, document_id)


@router.get("/{document_id}/duplicates", response_model=DocumentDuplicateGroupResponse)
async def get_document_duplicate_group(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentDuplicateGroupResponse:
    return await service.get_duplicate_group(current_user, document_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    body: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.update_document(current_user, document_id, body)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> None:
    await service.delete_document(current_user, document_id)


@router.get("/{document_id}/classification", response_model=DocumentClassificationResponse)
async def get_document_classification(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentClassificationResponse:
    return await service.get_classification(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report",
    response_model=DocumentParsedCreditReportResponse,
)
async def get_document_parsed_credit_report(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentParsedCreditReportResponse:
    return await service.get_parsed_credit_report(current_user, document_id)


@router.post(
    "/{document_id}/parsed-credit-report/reparse",
    response_model=DocumentCreditReportReparseResponse,
)
async def reparse_document_credit_report(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentCreditReportReparseResponse:
    return await service.reparse_credit_report(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report/comparison",
    response_model=DocumentParsedCreditReportComparisonResponse,
)
async def compare_document_parsed_credit_report(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentParsedCreditReportComparisonResponse:
    return await service.compare_parsed_credit_report(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report/metro2-findings",
    response_model=DocumentMetro2FindingsResponse,
)
async def get_document_metro2_findings(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentMetro2FindingsResponse:
    return await service.get_metro2_findings(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report/fcra-findings",
    response_model=DocumentFcraFindingsResponse,
)
async def get_document_fcra_findings(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentFcraFindingsResponse:
    return await service.get_fcra_findings(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report/identity-theft-findings",
    response_model=DocumentIdentityTheftFindingsResponse,
)
async def get_document_identity_theft_findings(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentIdentityTheftFindingsResponse:
    return await service.get_identity_theft_findings(current_user, document_id)


@router.get(
    "/{document_id}/parsed-credit-report/account-candidates",
    response_model=DocumentParsedCreditReportAccountCandidatesResponse,
)
async def get_document_parsed_credit_report_account_candidates(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentParsedCreditReportAccountCandidatesResponse:
    return await service.get_parsed_credit_report_account_candidates(current_user, document_id)


@router.post(
    "/{document_id}/parsed-credit-report/import-accounts",
    response_model=ImportParsedReportAccountsResponse,
)
async def import_document_parsed_credit_report_accounts(
    document_id: uuid.UUID,
    body: ImportParsedReportAccountsRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ImportParsedReportAccountsResponse:
    return await service.import_parsed_credit_report_accounts(current_user, document_id, body)


@router.post(
    "/{document_id}/parsed-credit-report/review-task",
    response_model=TaskResponse,
)
async def create_document_parsed_credit_report_review_task(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> TaskResponse:
    return await service.create_parsed_credit_report_review_task(current_user, document_id)


@router.post("/{document_id}/classify", response_model=DocumentClassificationResponse)
async def classify_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentClassificationResponse:
    return await service.classify_document(current_user, document_id)


@router.get("/{document_id}/metadata", response_model=DocumentMetadataResponse)
async def get_document_metadata(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentMetadataResponse:
    return await service.get_metadata(current_user, document_id)


@router.post("/{document_id}/metadata/extract", response_model=DocumentMetadataResponse)
async def extract_document_metadata(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentMetadataResponse:
    return await service.extract_metadata(current_user, document_id)


@router.get("/{document_id}/resolutions", response_model=DocumentResolutionsResponse)
async def get_document_resolutions(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResolutionsResponse:
    return await service.get_resolutions(current_user, document_id)


@router.post("/{document_id}/resolutions/resolve", response_model=DocumentResolutionsResponse)
async def resolve_document_entities(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResolutionsResponse:
    return await service.resolve_entities(current_user, document_id)


@router.post(
    "/{document_id}/resolutions/{resolution_id}/confirm",
    response_model=DocumentResolutionsResponse,
)
async def confirm_document_resolution(
    document_id: uuid.UUID,
    resolution_id: uuid.UUID,
    body: ResolutionConfirmRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResolutionsResponse:
    return await service.confirm_resolution(
        current_user,
        document_id,
        resolution_id,
        body,
    )


@router.post(
    "/{document_id}/resolutions/{resolution_id}/reject",
    response_model=DocumentResolutionsResponse,
)
async def reject_document_resolution(
    document_id: uuid.UUID,
    resolution_id: uuid.UUID,
    body: ResolutionRejectRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResolutionsResponse:
    return await service.reject_resolution(
        current_user,
        document_id,
        resolution_id,
        body,
    )


@router.get("/{document_id}/ocr", response_model=DocumentOcrResponse)
async def get_document_ocr(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentOcrResponse:
    return await service.get_ocr_result(current_user, document_id)


@router.post("/{document_id}/ocr/retry", response_model=DocumentOcrResponse)
async def retry_document_ocr(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentOcrResponse:
    return await service.retry_ocr(current_user, document_id)


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    version: int | None = Query(None, ge=1),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    data, file_name, mime_type = await service.download_document(
        current_user,
        document_id,
        version_number=version,
    )
    return Response(
        content=data,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/{document_id}/versions", response_model=DocumentResponse)
async def upload_document_version(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.upload_version(current_user, document_id, file)


@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentVersionResponse]:
    return await service.list_versions(current_user, document_id)


@router.post("/{document_id}/llm-summary", response_model=DocumentLlmSummaryResponse)
async def generate_document_llm_summary(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentLlmSummaryService = Depends(get_document_llm_summary_service),
) -> DocumentLlmSummaryResponse:
    return await service.generate_summary(current_user, document_id)
