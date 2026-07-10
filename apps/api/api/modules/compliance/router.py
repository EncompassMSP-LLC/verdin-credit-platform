"""Compliance center endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.accounts.autonomous_bureau_filing_router import autonomous_bureau_filing_router
from api.modules.accounts.bureau_live_api_router import bureau_live_api_router
from api.modules.accounts.bureau_refiling_router import bureau_refiling_router
from api.modules.accounts.bureau_unsupervised_refiling_router import (
    bureau_unsupervised_refiling_router,
)
from api.modules.accounts.dispute_bureau_submission_router import dispute_bureau_submission_router
from api.modules.accounts.dispute_filing_prep_router import dispute_filing_prep_router
from api.modules.accounts.fully_autonomous_bureau_api_filing_router import (
    fully_autonomous_bureau_api_filing_router,
)
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.dependencies import require_compliance_enforcement_enabled
from api.modules.compliance.models import ConsentStatus, ConsentType, RetentionScope
from api.modules.compliance.schemas import (
    ClientConsentGapsResponse,
    ComplianceCenterStatusResponse,
    ConsentDocumentTemplateResponse,
    ConsentDocumentTemplateUpdate,
    ConsentRecordCreate,
    ConsentRecordListParams,
    ConsentRecordResponse,
    ConsentSortField,
    ConsentSortOrder,
    RetentionEnforcementRunListParams,
    RetentionEnforcementRunResponse,
    RetentionEnforcementRunResultResponse,
    RetentionEnforcementStatusResponse,
    RetentionPolicyCreate,
    RetentionPolicyListParams,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
    RetentionSortField,
    RetentionSortOrder,
)
from api.modules.compliance.service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance"])
router.include_router(dispute_filing_prep_router)
router.include_router(dispute_bureau_submission_router)
router.include_router(bureau_live_api_router)
router.include_router(autonomous_bureau_filing_router)
router.include_router(fully_autonomous_bureau_api_filing_router)
router.include_router(bureau_refiling_router)
router.include_router(bureau_unsupervised_refiling_router)


def get_compliance_service(db: AsyncSession = Depends(get_db)) -> ComplianceService:
    return ComplianceService.from_session(db)


def get_consent_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: uuid.UUID | None = None,
    case_id: uuid.UUID | None = None,
    consent_type: ConsentType | None = None,
    status: ConsentStatus | None = None,
    sort_by: ConsentSortField = "granted_at",
    sort_order: ConsentSortOrder = "desc",
) -> ConsentRecordListParams:
    return ConsentRecordListParams(
        page=page,
        page_size=page_size,
        client_id=client_id,
        case_id=case_id,
        consent_type=consent_type,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def get_retention_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    scope: RetentionScope | None = None,
    is_active: bool | None = None,
    sort_by: RetentionSortField = "created_at",
    sort_order: RetentionSortOrder = "desc",
) -> RetentionPolicyListParams:
    return RetentionPolicyListParams(
        page=page,
        page_size=page_size,
        scope=scope,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/status", response_model=ComplianceCenterStatusResponse)
async def get_compliance_status(
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ComplianceCenterStatusResponse:
    return await service.get_status(current_user)


@router.get("/consents", response_model=PaginatedResponse[ConsentRecordResponse])
async def list_consent_records(
    params: ConsentRecordListParams = Depends(get_consent_list_params),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> PaginatedResponse[ConsentRecordResponse]:
    return await service.list_consents(current_user, params)


@router.get("/consents/gaps", response_model=ClientConsentGapsResponse)
async def get_client_consent_gaps(
    client_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ClientConsentGapsResponse:
    return await service.get_client_consent_gaps(current_user, client_id)


@router.get("/consent-templates", response_model=list[ConsentDocumentTemplateResponse])
async def list_consent_templates(
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> list[ConsentDocumentTemplateResponse]:
    return await service.list_consent_templates(current_user)


@router.put(
    "/consent-templates/{template_key}",
    response_model=ConsentDocumentTemplateResponse,
)
async def update_consent_template(
    template_key: ConsentDocumentTemplateKey,
    body: ConsentDocumentTemplateUpdate,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ConsentDocumentTemplateResponse:
    return await service.update_consent_template(current_user, template_key, body)


@router.get("/consent-templates/{template_key}/preview")
async def preview_consent_template(
    template_key: ConsentDocumentTemplateKey,
    client_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> Response:
    pdf_bytes, filename = await service.preview_consent_template_pdf(
        current_user,
        template_key=template_key,
        client_id=client_id,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/consents", response_model=ConsentRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_consent_record(
    body: ConsentRecordCreate,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ConsentRecordResponse:
    return await service.create_consent(current_user, body)


@router.get("/consents/{consent_id}", response_model=ConsentRecordResponse)
async def get_consent_record(
    consent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ConsentRecordResponse:
    return await service.get_consent(current_user, consent_id)


@router.post("/consents/{consent_id}/withdraw", response_model=ConsentRecordResponse)
async def withdraw_consent_record(
    consent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ConsentRecordResponse:
    return await service.withdraw_consent(current_user, consent_id)


@router.post(
    "/consents/upload",
    response_model=ConsentRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_signed_consent_record(
    client_id: uuid.UUID = Form(...),
    case_id: uuid.UUID = Form(...),
    consent_type: ConsentType = Form(...),
    file: UploadFile = File(...),
    signer_name: str | None = Form(None),
    notes: str | None = Form(None),
    document_template_key: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> ConsentRecordResponse:
    return await service.upload_signed_consent(
        current_user,
        client_id=client_id,
        case_id=case_id,
        consent_type=consent_type,
        file=file,
        signer_name=signer_name,
        notes=notes,
        document_template_key=document_template_key,
    )


@router.get("/retention-policies", response_model=PaginatedResponse[RetentionPolicyResponse])
async def list_retention_policies(
    params: RetentionPolicyListParams = Depends(get_retention_list_params),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> PaginatedResponse[RetentionPolicyResponse]:
    return await service.list_retention_policies(current_user, params)


@router.post(
    "/retention-policies",
    response_model=RetentionPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_retention_policy(
    body: RetentionPolicyCreate,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> RetentionPolicyResponse:
    return await service.create_retention_policy(current_user, body)


@router.get("/retention-policies/{policy_id}", response_model=RetentionPolicyResponse)
async def get_retention_policy(
    policy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> RetentionPolicyResponse:
    return await service.get_retention_policy(current_user, policy_id)


@router.patch("/retention-policies/{policy_id}", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    policy_id: uuid.UUID,
    body: RetentionPolicyUpdate,
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> RetentionPolicyResponse:
    return await service.update_retention_policy(current_user, policy_id, body)


@router.get(
    "/enforcement/status",
    response_model=RetentionEnforcementStatusResponse,
    dependencies=[Depends(require_compliance_enforcement_enabled)],
)
async def get_enforcement_status(
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> RetentionEnforcementStatusResponse:
    return await service.get_enforcement_status(current_user)


@router.get(
    "/enforcement/runs",
    response_model=PaginatedResponse[RetentionEnforcementRunResponse],
    dependencies=[Depends(require_compliance_enforcement_enabled)],
)
async def list_enforcement_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> PaginatedResponse[RetentionEnforcementRunResponse]:
    params = RetentionEnforcementRunListParams(page=page, page_size=page_size)
    return await service.list_enforcement_runs(current_user, params)


@router.post(
    "/enforcement/run",
    response_model=RetentionEnforcementRunResultResponse,
    dependencies=[Depends(require_compliance_enforcement_enabled)],
)
async def run_retention_enforcement(
    current_user: User = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
) -> RetentionEnforcementRunResultResponse:
    return await service.run_enforcement(current_user)
