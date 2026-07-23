"""Case management endpoints."""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.credit_analysis_schemas import (
    CreditAnalysisRunListResponse,
    CreditAnalysisRunResponse,
)
from api.modules.accounts.credit_analysis_service import CreditAnalysisService
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
    CaseBulkEntityReresolveResponse,
    CaseBulkOcrRetryResponse,
    CaseBulkReclassifyResponse,
    CaseCfpbChecklistResponse,
    CaseComplianceEvidenceLinksResponse,
    CaseCreditReportBulkReparseResponse,
    CaseCreditReportDiscrepanciesResponse,
    CaseDisputeStrategyResponse,
    CaseFcraFindingsResponse,
    CaseIdentityTheftFindingsResponse,
    CaseLitigationStrengthResponse,
    CaseMetadataBulkReextractResponse,
    CaseMetro2FindingsResponse,
    CaseTradelineChronologyResponse,
    ConfirmIdentityTheftAccountRequest,
    DisputeStrategyRunListParams,
    DisputeStrategyRunResponse,
    DisputeStrategyRunSummaryResponse,
    DocumentResponse,
    Fcra605bReadinessRunResponse,
    IdentityTheftAccountReviewResponse,
    IdentityTheftCaseCenterResponse,
    IdentityTheftIncidentResponse,
    IdentityTheftProtectionResponse,
    PrepareCreditReportDisputesRequest,
    PrepareCreditReportDisputesResponse,
    PrepareDisputeStrategyStageRequest,
    PrepareDisputeStrategyStageResponse,
    UpdateIdentityTheftIncidentRequest,
    UpsertChecklistOverrideRequest,
    UpsertIdentityTheftProtectionRequest,
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


def get_credit_analysis_service(db: AsyncSession = Depends(get_db)) -> CreditAnalysisService:
    return CreditAnalysisService.from_session(db)


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


@router.post(
    "/{case_id}/parsed-credit-reports/reparse",
    response_model=CaseCreditReportBulkReparseResponse,
)
async def bulk_reparse_case_credit_reports(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseCreditReportBulkReparseResponse:
    return await service.bulk_reparse_case_credit_reports(current_user, case_id)


@router.post(
    "/{case_id}/metadata/reextract",
    response_model=CaseMetadataBulkReextractResponse,
)
async def bulk_reextract_case_metadata(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseMetadataBulkReextractResponse:
    return await service.bulk_reextract_case_metadata(current_user, case_id)


@router.post(
    "/{case_id}/classify/reclassify",
    response_model=CaseBulkReclassifyResponse,
)
async def bulk_reclassify_case_documents(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseBulkReclassifyResponse:
    return await service.bulk_reclassify_case_documents(current_user, case_id)


@router.post(
    "/{case_id}/resolutions/reresolve",
    response_model=CaseBulkEntityReresolveResponse,
)
async def bulk_reresolve_case_entities(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseBulkEntityReresolveResponse:
    return await service.bulk_reresolve_case_entities(current_user, case_id)


@router.post(
    "/{case_id}/ocr/retry",
    response_model=CaseBulkOcrRetryResponse,
)
async def bulk_retry_case_ocr(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseBulkOcrRetryResponse:
    return await service.bulk_retry_case_ocr(current_user, case_id)


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
    "/{case_id}/identity-theft-findings",
    response_model=CaseIdentityTheftFindingsResponse,
)
async def get_case_identity_theft_findings(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseIdentityTheftFindingsResponse:
    return await service.get_case_identity_theft_findings(current_user, case_id)


@router.get(
    "/{case_id}/identity-theft-center",
    response_model=IdentityTheftCaseCenterResponse,
)
async def get_case_identity_theft_center(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> IdentityTheftCaseCenterResponse:
    return await service.get_case_identity_theft_center(current_user, case_id)


@router.post(
    "/{case_id}/identity-theft/account-reviews",
    response_model=IdentityTheftAccountReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_identity_theft_account(
    case_id: uuid.UUID,
    body: ConfirmIdentityTheftAccountRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> IdentityTheftAccountReviewResponse:
    return await service.confirm_identity_theft_account(current_user, case_id, body)


@router.put(
    "/{case_id}/identity-theft/protections",
    response_model=IdentityTheftProtectionResponse,
)
async def upsert_identity_theft_protection(
    case_id: uuid.UUID,
    body: UpsertIdentityTheftProtectionRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> IdentityTheftProtectionResponse:
    return await service.upsert_identity_theft_protection(current_user, case_id, body)


@router.patch(
    "/{case_id}/identity-theft/incident",
    response_model=IdentityTheftIncidentResponse,
)
async def update_identity_theft_incident(
    case_id: uuid.UUID,
    body: UpdateIdentityTheftIncidentRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> IdentityTheftIncidentResponse:
    return await service.update_identity_theft_incident(current_user, case_id, body)


@router.get("/{case_id}/identity-theft/605b-packet.zip")
async def export_case_identity_theft_605b_packet(
    case_id: uuid.UUID,
    letter_format: Literal["text", "pdf"] = Query(default="pdf"),
    document_id: list[uuid.UUID] = Query(
        default=[],
        description="Optional staff-selected case document IDs to bundle as evidence exhibits",
    ),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_identity_theft_605b_packet(
        current_user,
        case_id,
        letter_format=letter_format,
        document_ids=document_id,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.post(
    "/{case_id}/credit-analysis/runs",
    response_model=CreditAnalysisRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_analysis_run(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CreditAnalysisService = Depends(get_credit_analysis_service),
) -> CreditAnalysisRunResponse:
    """Deterministic Lending Readiness compose + publish (Vol 22). Advisory only."""
    return await service.create_run(current_user, case_id)


@router.get(
    "/{case_id}/credit-analysis/runs",
    response_model=CreditAnalysisRunListResponse,
)
async def list_credit_analysis_runs(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CreditAnalysisService = Depends(get_credit_analysis_service),
) -> CreditAnalysisRunListResponse:
    return await service.list_runs(current_user, case_id)


@router.get(
    "/{case_id}/credit-analysis/runs/latest",
    response_model=CreditAnalysisRunResponse,
)
async def get_latest_credit_analysis_run(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CreditAnalysisService = Depends(get_credit_analysis_service),
) -> CreditAnalysisRunResponse:
    return await service.get_latest_run(current_user, case_id)


@router.get(
    "/{case_id}/credit-analysis/runs/{run_id}",
    response_model=CreditAnalysisRunResponse,
)
async def get_credit_analysis_run(
    case_id: uuid.UUID,
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CreditAnalysisService = Depends(get_credit_analysis_service),
) -> CreditAnalysisRunResponse:
    return await service.get_run(current_user, case_id, run_id)


@router.post(
    "/{case_id}/identity-theft/605b-readiness-runs",
    response_model=Fcra605bReadinessRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_case_identity_theft_605b_readiness_audit(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Fcra605bReadinessRunResponse:
    return await service.run_case_identity_theft_605b_readiness_audit(current_user, case_id)


@router.get(
    "/{case_id}/identity-theft/605b-readiness-runs/latest",
    response_model=Fcra605bReadinessRunResponse,
)
async def get_latest_case_identity_theft_605b_readiness_run(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Fcra605bReadinessRunResponse:
    return await service.get_latest_case_identity_theft_605b_readiness_run(current_user, case_id)


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
    include_page_scan: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseComplianceEvidenceLinksResponse:
    return await service.get_case_compliance_evidence_links(
        current_user,
        case_id,
        include_page_scan=include_page_scan,
    )


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
    return await service.get_case_dispute_strategy(current_user, case_id, persist_run=True)


@router.get(
    "/{case_id}/dispute-strategy/runs",
    response_model=PaginatedResponse[DisputeStrategyRunSummaryResponse],
)
async def list_case_dispute_strategy_runs(
    case_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> PaginatedResponse[DisputeStrategyRunSummaryResponse]:
    params = DisputeStrategyRunListParams(page=page, page_size=page_size)
    return await service.list_case_dispute_strategy_runs(current_user, case_id, params)


@router.get(
    "/{case_id}/dispute-strategy/runs/latest",
    response_model=DisputeStrategyRunResponse,
)
async def get_latest_case_dispute_strategy_run(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DisputeStrategyRunResponse:
    return await service.get_latest_case_dispute_strategy_run(current_user, case_id)


@router.get(
    "/{case_id}/dispute-strategy/runs/{run_id}",
    response_model=DisputeStrategyRunResponse,
)
async def get_case_dispute_strategy_run(
    case_id: uuid.UUID,
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DisputeStrategyRunResponse:
    return await service.get_case_dispute_strategy_run(current_user, case_id, run_id)


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


@router.put(
    "/{case_id}/dispute-strategy/checklist-overrides",
)
async def upsert_case_checklist_override(
    case_id: uuid.UUID,
    body: UpsertChecklistOverrideRequest,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> CaseCfpbChecklistResponse | CaseAttorneyChecklistResponse:
    return await service.upsert_case_checklist_override(current_user, case_id, body)


@router.get("/{case_id}/dispute-strategy/cfpb-checklist/export")
async def export_case_cfpb_checklist(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    format: Literal["md", "pdf"] = Query(default="md"),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_cfpb_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
        export_format=format,
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
    format: Literal["md", "pdf"] = Query(default="md"),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_attorney_checklist(
        current_user,
        case_id,
        recommended_only=recommended_only,
        export_format=format,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.get("/{case_id}/dispute-strategy/cfpb-checklist/packet.zip")
async def export_case_cfpb_checklist_packet(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    include_letters: bool = Query(default=True),
    letter_format: Literal["text", "pdf"] = Query(default="text"),
    include_mail_packets: bool = Query(default=False),
    include_report_excerpts: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_cfpb_checklist_packet(
        current_user,
        case_id,
        recommended_only=recommended_only,
        include_letters=include_letters,
        letter_format=letter_format,
        include_mail_packets=include_mail_packets,
        include_report_excerpts=include_report_excerpts,
    )
    safe_name = sanitize_content_disposition_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.get("/{case_id}/dispute-strategy/attorney-checklist/packet.zip")
async def export_case_attorney_checklist_packet(
    case_id: uuid.UUID,
    recommended_only: bool = Query(default=True),
    include_letters: bool = Query(default=True),
    letter_format: Literal["text", "pdf"] = Query(default="text"),
    include_mail_packets: bool = Query(default=False),
    include_report_excerpts: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    content, file_name, media_type = await service.export_case_attorney_checklist_packet(
        current_user,
        case_id,
        recommended_only=recommended_only,
        include_letters=include_letters,
        letter_format=letter_format,
        include_mail_packets=include_mail_packets,
        include_report_excerpts=include_report_excerpts,
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
