"""Case management endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.dispute_letter_export import sanitize_content_disposition_filename
from api.modules.accounts.schemas import (
    AccountListParams,
    AccountResponse,
    AccountSortField,
    AccountSortOrder,
)
from api.modules.accounts.service import AccountService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.cases.llm_summary import CaseLlmSummaryService
from api.modules.cases.models import CasePriority, CaseStage, CaseStatus
from api.modules.cases.schemas import (
    CaseCreate,
    CaseListParams,
    CaseLlmSummaryResponse,
    CaseResponse,
    CaseSortField,
    CaseSortOrder,
    CaseUpdate,
)
from api.modules.cases.service import CaseService
from api.modules.documents.schemas import (
    CaseAttorneyChecklistResponse,
    CaseCfpbChecklistResponse,
    CaseComplianceEvidenceLinksResponse,
    CaseCreditReportDiscrepanciesResponse,
    CaseDisputeStrategyResponse,
    CaseFcraFindingsResponse,
    CaseLitigationStrengthResponse,
    CaseMetro2FindingsResponse,
    CaseTradelineChronologyResponse,
    DocumentResponse,
    PrepareCreditReportDisputesRequest,
    PrepareCreditReportDisputesResponse,
    PrepareDisputeStrategyStageRequest,
    PrepareDisputeStrategyStageResponse,
)
from api.modules.documents.service import DocumentService

router = APIRouter(prefix="/cases", tags=["Cases"])


def get_case_service(db: AsyncSession = Depends(get_db)) -> CaseService:
    return CaseService.from_session(db)


def get_case_llm_summary_service(db: AsyncSession = Depends(get_db)) -> CaseLlmSummaryService:
    return CaseLlmSummaryService.from_session(db)


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService.from_session(db)


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService.from_session(db)


def get_case_account_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: AccountSortField = "created_at",
    sort_order: AccountSortOrder = "desc",
) -> AccountListParams:
    return AccountListParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def get_case_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    status: CaseStatus | None = None,
    stage: CaseStage | None = None,
    priority: CasePriority | None = None,
    assigned_user_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    sort_by: CaseSortField = "created_at",
    sort_order: CaseSortOrder = "desc",
) -> CaseListParams:
    return CaseListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        stage=stage,
        priority=priority,
        assigned_user_id=assigned_user_id,
        client_id=client_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    body: CaseCreate,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.create_case(current_user, body)


@router.get("", response_model=PaginatedResponse[CaseResponse])
async def list_cases(
    params: CaseListParams = Depends(get_case_list_params),
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> PaginatedResponse[CaseResponse]:
    return await service.list_cases(current_user, params)


@router.post("/{case_id}/llm-summary", response_model=CaseLlmSummaryResponse)
async def generate_case_llm_summary(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseLlmSummaryService = Depends(get_case_llm_summary_service),
) -> CaseLlmSummaryResponse:
    return await service.generate_summary(current_user, case_id)


@router.get("/{case_id}/accounts", response_model=PaginatedResponse[AccountResponse])
async def list_case_accounts(
    case_id: uuid.UUID,
    params: AccountListParams = Depends(get_case_account_list_params),
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> PaginatedResponse[AccountResponse]:
    return await service.list_case_accounts(current_user, case_id, params)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.get_case(current_user, case_id)


@router.get(
    "/{case_id}/credit-report-discrepancies",
    response_model=CaseCreditReportDiscrepanciesResponse,
)
async def get_case_credit_report_discrepancies(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseCreditReportDiscrepanciesResponse:
    return await service.get_case_credit_report_discrepancies(current_user, case_id)


@router.get(
    "/{case_id}/metro2-findings",
    response_model=CaseMetro2FindingsResponse,
)
async def get_case_metro2_findings(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseMetro2FindingsResponse:
    return await service.get_case_metro2_findings(current_user, case_id)


@router.get(
    "/{case_id}/fcra-findings",
    response_model=CaseFcraFindingsResponse,
)
async def get_case_fcra_findings(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseFcraFindingsResponse:
    return await service.get_case_fcra_findings(current_user, case_id)


@router.get(
    "/{case_id}/tradeline-chronology",
    response_model=CaseTradelineChronologyResponse,
)
async def get_case_tradeline_chronology(
    case_id: uuid.UUID,
    bureau: str | None = Query(None, description="Optional bureau filter"),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseTradelineChronologyResponse:
    return await service.get_case_tradeline_chronology(
        current_user,
        case_id,
        bureau=bureau,
    )


@router.get(
    "/{case_id}/compliance-evidence-links",
    response_model=CaseComplianceEvidenceLinksResponse,
)
async def get_case_compliance_evidence_links(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseComplianceEvidenceLinksResponse:
    return await service.get_case_compliance_evidence_links(current_user, case_id)


@router.get(
    "/{case_id}/litigation-strength",
    response_model=CaseLitigationStrengthResponse,
)
async def get_case_litigation_strength(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseLitigationStrengthResponse:
    return await service.get_case_litigation_strength(current_user, case_id)


@router.get(
    "/{case_id}/dispute-strategy",
    response_model=CaseDisputeStrategyResponse,
)
async def get_case_dispute_strategy(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseDisputeStrategyResponse:
    return await service.get_case_dispute_strategy(current_user, case_id)


@router.get(
    "/{case_id}/dispute-strategy/cfpb-checklist",
    response_model=CaseCfpbChecklistResponse,
)
async def get_case_cfpb_checklist(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseCfpbChecklistResponse:
    return await service.get_case_cfpb_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
    )


@router.get(
    "/{case_id}/dispute-strategy/attorney-checklist",
    response_model=CaseAttorneyChecklistResponse,
)
async def get_case_attorney_checklist(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseAttorneyChecklistResponse:
    return await service.get_case_attorney_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
    )


@router.get("/{case_id}/dispute-strategy/cfpb-checklist/export")
async def export_case_cfpb_checklist(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_cfpb_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.get("/{case_id}/dispute-strategy/attorney-checklist/export")
async def export_case_attorney_checklist(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_attorney_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.post(
    "/{case_id}/dispute-strategy/prepare",
    response_model=PrepareDisputeStrategyStageResponse,
)
async def prepare_case_dispute_strategy_stage(
    case_id: uuid.UUID,
    body: PrepareDisputeStrategyStageRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> PrepareDisputeStrategyStageResponse:
    return await service.prepare_case_dispute_strategy_stage(current_user, case_id, body)


@router.post(
    "/{case_id}/credit-report-discrepancies/prepare-disputes",
    response_model=PrepareCreditReportDisputesResponse,
)
async def prepare_case_credit_report_disputes(
    case_id: uuid.UUID,
    body: PrepareCreditReportDisputesRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> PrepareCreditReportDisputesResponse:
    return await service.prepare_case_credit_report_disputes(current_user, case_id, body)


@router.post(
    "/{case_id}/identity-document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_case_identity_document(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await service.upload_identity_document(
        current_user,
        case_id=case_id,
        file=file,
        title=title,
    )


@router.get("/{case_id}/dispute-mail-packets/export")
async def export_case_dispute_mail_packets(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> Response:
    content, file_name, media_type = await service.export_case_dispute_mail_packets(
        current_user,
        case_id,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.get("/{case_id}/dispute-report-excerpts/export")
async def export_case_dispute_report_excerpts(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> Response:
    content, file_name, media_type = await service.export_case_dispute_report_excerpts(
        current_user,
        case_id,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    body: CaseUpdate,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    return await service.update_case(current_user, case_id, body)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CaseService = Depends(get_case_service),
) -> None:
    await service.delete_case(current_user, case_id)
