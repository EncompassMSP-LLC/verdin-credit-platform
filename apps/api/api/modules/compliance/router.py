"""Compliance center endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.compliance.dependencies import require_compliance_enforcement_enabled
from api.modules.compliance.models import ConsentStatus, ConsentType, RetentionScope
from api.modules.compliance.schemas import (
    ComplianceCenterStatusResponse,
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
