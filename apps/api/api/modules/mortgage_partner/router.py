"""Mortgage Partner Edition endpoints."""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.accounts.credit_analysis_export import (
    sanitize_content_disposition_filename as sanitize_readiness_filename,
)
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.mortgage_partner.dependencies import require_mortgage_partner_enabled
from api.modules.mortgage_partner.schemas import (
    DashboardSummaryResponse,
    MilestoneReplacePayload,
    MortgagePartnerStatusResponse,
    MortgageReadinessReportResponse,
    PartnerAccessAuditResponse,
    PartnerLoanMilestoneResponse,
    PartnerReferralCreate,
    PartnerReferralResponse,
    PartnerReferralUpdate,
    PartnerRoleMatrixResponse,
    PartnershipCreate,
    PartnershipMemberCreate,
    PartnershipMemberResponse,
    PartnershipResponse,
    PipelineCardResponse,
    ReadinessReportSummary,
)
from api.modules.mortgage_partner.service import MortgagePartnerService

router = APIRouter(prefix="/mortgage-partner", tags=["Mortgage Partner"])


def get_mortgage_partner_service(db: AsyncSession = Depends(get_db)) -> MortgagePartnerService:
    return MortgagePartnerService.from_session(db)


@router.get("/status", response_model=MortgagePartnerStatusResponse)
async def get_mortgage_partner_status(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> MortgagePartnerStatusResponse:
    return service.get_status(current_user)


@router.get("/roles", response_model=PartnerRoleMatrixResponse)
async def get_partner_role_matrix(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerRoleMatrixResponse:
    return service.get_role_matrix(current_user)


@router.get("/access-audits", response_model=list[PartnerAccessAuditResponse])
async def list_partner_access_audits(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnerAccessAuditResponse]:
    return await service.list_access_audits(current_user)


@router.post("/partnerships", response_model=PartnershipResponse, status_code=201)
async def create_partnership(
    payload: PartnershipCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnershipResponse:
    return await service.create_partnership(current_user, payload)


@router.get("/partnerships", response_model=list[PartnershipResponse])
async def list_partnerships(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnershipResponse]:
    return await service.list_partnerships(current_user)


@router.get("/partnerships/{partnership_id}", response_model=PartnershipResponse)
async def get_partnership(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnershipResponse:
    return await service.get_partnership(current_user, partnership_id)


@router.get(
    "/partnerships/{partnership_id}/pipeline",
    response_model=list[PipelineCardResponse],
)
async def get_partnership_pipeline(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PipelineCardResponse]:
    return await service.get_pipeline(current_user, partnership_id)


@router.get(
    "/partnerships/{partnership_id}/dashboard-summary",
    response_model=DashboardSummaryResponse,
)
async def get_partnership_dashboard_summary(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> DashboardSummaryResponse:
    return await service.get_dashboard_summary(current_user, partnership_id)


@router.post(
    "/partnerships/{partnership_id}/members",
    response_model=PartnershipMemberResponse,
    status_code=201,
)
async def add_partnership_member(
    partnership_id: uuid.UUID,
    payload: PartnershipMemberCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnershipMemberResponse:
    return await service.add_member(current_user, partnership_id, payload)


@router.get(
    "/partnerships/{partnership_id}/members",
    response_model=list[PartnershipMemberResponse],
)
async def list_partnership_members(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnershipMemberResponse]:
    return await service.list_members(current_user, partnership_id)


@router.post(
    "/partnerships/{partnership_id}/referrals",
    response_model=PartnerReferralResponse,
    status_code=201,
)
async def create_partner_referral(
    partnership_id: uuid.UUID,
    payload: PartnerReferralCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerReferralResponse:
    return await service.create_referral(current_user, partnership_id, payload)


@router.get(
    "/partnerships/{partnership_id}/referrals",
    response_model=list[PartnerReferralResponse],
)
async def list_partner_referrals(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnerReferralResponse]:
    return await service.list_referrals(current_user, partnership_id)


@router.get(
    "/partnerships/{partnership_id}/referrals/{referral_id}",
    response_model=PartnerReferralResponse,
)
async def get_partner_referral(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerReferralResponse:
    return await service.get_referral(current_user, partnership_id, referral_id)


@router.patch(
    "/partnerships/{partnership_id}/referrals/{referral_id}",
    response_model=PartnerReferralResponse,
)
async def update_partner_referral(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    payload: PartnerReferralUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerReferralResponse:
    return await service.update_referral(current_user, partnership_id, referral_id, payload)


@router.get(
    "/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
    response_model=list[PartnerLoanMilestoneResponse],
)
async def list_referral_milestones(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnerLoanMilestoneResponse]:
    return await service.list_milestones(current_user, partnership_id, referral_id)


@router.put(
    "/partnerships/{partnership_id}/referrals/{referral_id}/milestones",
    response_model=list[PartnerLoanMilestoneResponse],
)
async def replace_referral_milestones(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    payload: MilestoneReplacePayload,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnerLoanMilestoneResponse]:
    return await service.replace_milestones(current_user, partnership_id, referral_id, payload)


# ---------------------------------------------------------------------------
# Readiness reports (slice 4)
# ---------------------------------------------------------------------------


@router.get(
    "/partnerships/{partnership_id}/readiness-reports",
    response_model=list[ReadinessReportSummary],
)
async def list_partnership_readiness_reports(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[ReadinessReportSummary]:
    """List advisory readiness-report summaries for all referrals with published runs."""
    return await service.list_readiness_reports(current_user, partnership_id)


@router.get(
    "/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
    response_model=MortgageReadinessReportResponse,
)
async def get_referral_readiness_report(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> MortgageReadinessReportResponse:
    """Get the advisory mortgage readiness report for a referral.

    Lending Readiness Score™ is an advisory tool for organizing credit and
    documentation work toward a mortgage conversation. It is not a credit score
    from a consumer reporting agency, not an underwriting decision, and not a
    guarantee of loan approval or terms.
    """
    return await service.get_readiness_report(current_user, partnership_id, referral_id)


@router.get(
    "/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report/export",
)
async def export_referral_readiness_report(
    partnership_id: uuid.UUID,
    referral_id: uuid.UUID,
    format: Literal["text", "pdf"] = Query("text", alias="format"),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> Response:
    """Operator-gated export of the advisory readiness report (text/pdf).

    Disclaimer is reproduced at the top of every export.
    The platform never auto-transmits this document.
    """
    content, file_name, media_type = await service.export_readiness_report(
        current_user,
        partnership_id,
        referral_id,
        export_format=format,
    )
    safe_name = sanitize_readiness_filename(file_name)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
