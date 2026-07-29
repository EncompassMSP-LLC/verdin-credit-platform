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
from api.modules.mortgage_partner.nurture_service import PartnerNurtureService
from api.modules.mortgage_partner.realtor_service import RealtorPartnerService
from api.modules.mortgage_partner.schemas import (
    AppointmentReminderProcessResponse,
    AppointmentReminderRunResponse,
    CrmAppointmentCreate,
    CrmAppointmentResponse,
    CrmAppointmentUpdate,
    CrmAutomationAuditEventResponse,
    CrmAutomationFireRequest,
    CrmAutomationRuleCreate,
    CrmAutomationRuleResponse,
    CrmAutomationRuleUpdate,
    DashboardSummaryResponse,
    MilestoneReplacePayload,
    MortgagePartnerStatusResponse,
    MortgageReadinessReportResponse,
    NurtureDeliveryProcessResponse,
    NurtureDeliveryRunResponse,
    NurtureEnrollmentCreate,
    NurtureEnrollmentResponse,
    NurtureEnrollmentUpdate,
    NurtureProgramResponse,
    PartnerAccessAuditResponse,
    PartnerContactCreate,
    PartnerContactResponse,
    PartnerContactUpdate,
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
    RealtorInviteAcceptRequest,
    RealtorInviteCreate,
    RealtorInvitePreviewResponse,
    RealtorInviteResponse,
    RealtorPasswordResetConfirm,
    RealtorPasswordResetRequest,
    RealtorPasswordResetRequestResponse,
    RealtorPipelineBoardResponse,
    RealtorPortalDashboardResponse,
    RealtorReferralCardResponse,
    RealtorSessionResponse,
    RealtorTokenResponse,
    ReferralIntakeCreate,
    ReferralIntakeOrchestratorResponse,
    ReferralIntakeResponse,
    ReferralIntakeStatusResponse,
    WeeklyDigestProcessResponse,
    WeeklyDigestRunResponse,
    WeeklyDigestSubscriptionCreate,
    WeeklyDigestSubscriptionResponse,
    WeeklyDigestSubscriptionUpdate,
)
from api.modules.mortgage_partner.service import MortgagePartnerService
from api.modules.mortgage_partner.weekly_digest_service import PartnerWeeklyDigestService

router = APIRouter(prefix="/mortgage-partner", tags=["Mortgage Partner"])


def get_mortgage_partner_service(db: AsyncSession = Depends(get_db)) -> MortgagePartnerService:
    return MortgagePartnerService.from_session(db)


def get_nurture_service(db: AsyncSession = Depends(get_db)) -> PartnerNurtureService:
    return PartnerNurtureService.from_session(db)


def get_weekly_digest_service(db: AsyncSession = Depends(get_db)) -> PartnerWeeklyDigestService:
    return PartnerWeeklyDigestService.from_session(db)


def get_realtor_service(db: AsyncSession = Depends(get_db)) -> RealtorPartnerService:
    return RealtorPartnerService.from_session(db)


@router.get("/status", response_model=MortgagePartnerStatusResponse)
async def get_mortgage_partner_status(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> MortgagePartnerStatusResponse:
    return service.get_status(current_user)


@router.get("/automation-rules", response_model=list[CrmAutomationRuleResponse])
async def list_automation_rules(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[CrmAutomationRuleResponse]:
    """List persisted CRM automation rules; seeds defaults when empty (LRP-203)."""
    return await service.list_automation_rules(current_user)


@router.post(
    "/automation-rules",
    response_model=CrmAutomationRuleResponse,
    status_code=201,
)
async def create_automation_rule(
    payload: CrmAutomationRuleCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAutomationRuleResponse:
    return await service.create_automation_rule(current_user, payload)


@router.patch(
    "/automation-rules/{rule_id}",
    response_model=CrmAutomationRuleResponse,
)
async def update_automation_rule(
    rule_id: uuid.UUID,
    payload: CrmAutomationRuleUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAutomationRuleResponse:
    return await service.update_automation_rule(current_user, rule_id, payload)


@router.post(
    "/automation-rules/{rule_id}/fire",
    response_model=CrmAutomationAuditEventResponse,
    status_code=201,
)
async def fire_automation_rule(
    rule_id: uuid.UUID,
    payload: CrmAutomationFireRequest,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAutomationAuditEventResponse:
    """Staff-mediated fire/dry-run for a CRM automation rule (LRP-502)."""
    return await service.fire_automation_rule(current_user, rule_id, payload)


@router.get(
    "/automation-events",
    response_model=list[CrmAutomationAuditEventResponse],
)
async def list_automation_audit_events(
    rule_id: uuid.UUID | None = Query(default=None),
    event_kind: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[CrmAutomationAuditEventResponse]:
    """List durable CRM automation config/fire audit events (LRP-502)."""
    return await service.list_automation_audit_events(
        current_user,
        rule_id=rule_id,
        event_kind=event_kind,
        limit=limit,
    )


@router.get(
    "/automation-events/{event_id}",
    response_model=CrmAutomationAuditEventResponse,
)
async def get_automation_audit_event(
    event_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAutomationAuditEventResponse:
    return await service.get_automation_audit_event(current_user, event_id)


@router.get("/appointments", response_model=list[CrmAppointmentResponse])
async def list_appointments(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[CrmAppointmentResponse]:
    """List CRM appointments for calendar + reminder scheduling (LRP-205)."""
    return await service.list_appointments(current_user)


@router.post(
    "/appointments",
    response_model=CrmAppointmentResponse,
    status_code=201,
)
async def create_appointment(
    payload: CrmAppointmentCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAppointmentResponse:
    return await service.create_appointment(current_user, payload)


@router.patch(
    "/appointments/{appointment_id}",
    response_model=CrmAppointmentResponse,
)
async def update_appointment(
    appointment_id: uuid.UUID,
    payload: CrmAppointmentUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> CrmAppointmentResponse:
    return await service.update_appointment(current_user, appointment_id, payload)


@router.post(
    "/appointments/reminders/process",
    response_model=AppointmentReminderProcessResponse,
)
async def process_appointment_reminders(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> AppointmentReminderProcessResponse:
    """Process due T-24h / T-1h appointment reminders (idempotent; LRP-205)."""
    return await service.process_appointment_reminders(current_user)


@router.get(
    "/appointments/reminders",
    response_model=list[AppointmentReminderRunResponse],
)
async def list_appointment_reminders(
    appointment_id: uuid.UUID | None = Query(None),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[AppointmentReminderRunResponse]:
    return await service.list_appointment_reminders(current_user, appointment_id=appointment_id)


@router.get("/nurture/programs", response_model=list[NurtureProgramResponse])
async def list_nurture_programs(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> list[NurtureProgramResponse]:
    """List partner nurture programs (seeds lender drip defaults when empty; LRP-206)."""
    return await nurture.list_programs(current_user)


@router.get("/nurture/enrollments", response_model=list[NurtureEnrollmentResponse])
async def list_nurture_enrollments(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> list[NurtureEnrollmentResponse]:
    return await nurture.list_enrollments(current_user)


@router.post(
    "/nurture/enrollments",
    response_model=NurtureEnrollmentResponse,
    status_code=201,
)
async def create_nurture_enrollment(
    payload: NurtureEnrollmentCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> NurtureEnrollmentResponse:
    return await nurture.create_enrollment(current_user, payload)


@router.patch(
    "/nurture/enrollments/{enrollment_id}",
    response_model=NurtureEnrollmentResponse,
)
async def update_nurture_enrollment(
    enrollment_id: uuid.UUID,
    payload: NurtureEnrollmentUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> NurtureEnrollmentResponse:
    return await nurture.update_enrollment(current_user, enrollment_id, payload)


@router.post(
    "/nurture/process",
    response_model=NurtureDeliveryProcessResponse,
)
async def process_nurture_due(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> NurtureDeliveryProcessResponse:
    """Process due nurture steps (idempotent; consent-gated; LRP-206)."""
    return await nurture.process_due(current_user)


@router.get("/nurture/deliveries", response_model=list[NurtureDeliveryRunResponse])
async def list_nurture_deliveries(
    enrollment_id: uuid.UUID | None = Query(None),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    nurture: PartnerNurtureService = Depends(get_nurture_service),
) -> list[NurtureDeliveryRunResponse]:
    return await nurture.list_deliveries(current_user, enrollment_id=enrollment_id)


@router.get(
    "/weekly-digests/subscriptions",
    response_model=list[WeeklyDigestSubscriptionResponse],
)
async def list_weekly_digest_subscriptions(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    digests: PartnerWeeklyDigestService = Depends(get_weekly_digest_service),
) -> list[WeeklyDigestSubscriptionResponse]:
    """List opt-in weekly partner digest subscriptions (LRP-207)."""
    return await digests.list_subscriptions(current_user)


@router.post(
    "/weekly-digests/subscriptions",
    response_model=WeeklyDigestSubscriptionResponse,
    status_code=201,
)
async def create_weekly_digest_subscription(
    payload: WeeklyDigestSubscriptionCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    digests: PartnerWeeklyDigestService = Depends(get_weekly_digest_service),
) -> WeeklyDigestSubscriptionResponse:
    return await digests.create_subscription(current_user, payload)


@router.patch(
    "/weekly-digests/subscriptions/{subscription_id}",
    response_model=WeeklyDigestSubscriptionResponse,
)
async def update_weekly_digest_subscription(
    subscription_id: uuid.UUID,
    payload: WeeklyDigestSubscriptionUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    digests: PartnerWeeklyDigestService = Depends(get_weekly_digest_service),
) -> WeeklyDigestSubscriptionResponse:
    return await digests.update_subscription(current_user, subscription_id, payload)


@router.post(
    "/weekly-digests/process",
    response_model=WeeklyDigestProcessResponse,
)
async def process_weekly_digests(
    week_key: str | None = Query(None),
    force: bool = Query(True),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    digests: PartnerWeeklyDigestService = Depends(get_weekly_digest_service),
) -> WeeklyDigestProcessResponse:
    """Process weekly digests for opt-in subscriptions (idempotent; LRP-207)."""
    return await digests.process_due(current_user, week_key=week_key, force=force)


@router.get("/weekly-digests/runs", response_model=list[WeeklyDigestRunResponse])
async def list_weekly_digest_runs(
    partnership_id: uuid.UUID | None = Query(None),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    digests: PartnerWeeklyDigestService = Depends(get_weekly_digest_service),
) -> list[WeeklyDigestRunResponse]:
    return await digests.list_runs(current_user, partnership_id=partnership_id)


@router.get("/referral-intake/status", response_model=ReferralIntakeStatusResponse)
async def get_referral_intake_status(
    _: None = Depends(require_mortgage_partner_enabled),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> ReferralIntakeStatusResponse:
    """Public readiness check for the partner web referral form (LRP-103)."""
    return service.get_referral_intake_status()


@router.post(
    "/referral-intake",
    response_model=ReferralIntakeResponse,
    status_code=201,
)
async def submit_referral_intake(
    payload: ReferralIntakeCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> ReferralIntakeResponse:
    """Public web-form referral intake — creates client, case, referral, and ops task."""
    return await service.submit_referral_intake(payload)


@router.get(
    "/referral-intake/{intake_id}/orchestrator",
    response_model=ReferralIntakeOrchestratorResponse,
)
async def get_referral_intake_orchestrator(
    intake_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> ReferralIntakeOrchestratorResponse:
    """Staff read of post-accept orchestrator audit (assignment + notify drafts; LRP-201)."""
    return await service.get_referral_intake_orchestrator_run(current_user, intake_id)


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


@router.get(
    "/partnerships/{partnership_id}/contacts",
    response_model=list[PartnerContactResponse],
)
async def list_partner_contacts(
    partnership_id: uuid.UUID,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> list[PartnerContactResponse]:
    return await service.list_contacts(current_user, partnership_id)


@router.post(
    "/partnerships/{partnership_id}/contacts",
    response_model=PartnerContactResponse,
    status_code=201,
)
async def create_partner_contact(
    partnership_id: uuid.UUID,
    payload: PartnerContactCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerContactResponse:
    return await service.create_contact(current_user, partnership_id, payload)


@router.patch(
    "/partnerships/{partnership_id}/contacts/{contact_id}",
    response_model=PartnerContactResponse,
)
async def update_partner_contact(
    partnership_id: uuid.UUID,
    contact_id: uuid.UUID,
    payload: PartnerContactUpdate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: MortgagePartnerService = Depends(get_mortgage_partner_service),
) -> PartnerContactResponse:
    return await service.update_contact(current_user, partnership_id, contact_id, payload)


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


# --- Realtor partner role + login (LRP-301) ---


@router.post(
    "/partnerships/{partnership_id}/realtor-invites",
    response_model=RealtorInviteResponse,
    status_code=201,
)
async def create_realtor_invite(
    partnership_id: uuid.UUID,
    payload: RealtorInviteCreate,
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorInviteResponse:
    """Staff-issued realtor workspace invitation (token returned once)."""
    return await service.create_invite(current_user, partnership_id, payload)


@router.post(
    "/partnerships/{partnership_id}/realtor-members/{member_id}/disable",
    response_model=RealtorSessionResponse,
)
async def disable_realtor_membership(
    partnership_id: uuid.UUID,
    member_id: uuid.UUID,
    disable_user: bool = Query(default=False),
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorSessionResponse:
    """Disable realtor partnership membership (optional account disable)."""
    return await service.disable_membership(
        current_user,
        partnership_id,
        member_id,
        disable_user=disable_user,
    )


@router.get("/realtor/me", response_model=RealtorSessionResponse)
async def get_realtor_me(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorSessionResponse:
    """Authenticated realtor session context (org + partnership isolation)."""
    return await service.get_me(current_user)


@router.get("/realtor/dashboard", response_model=RealtorPortalDashboardResponse)
async def get_realtor_portal_dashboard(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorPortalDashboardResponse:
    """Coarse stage summary for the realtor partnership (LRP-302)."""
    return await service.get_portal_dashboard(current_user)


@router.get("/realtor/referrals", response_model=list[RealtorReferralCardResponse])
async def list_realtor_referrals(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> list[RealtorReferralCardResponse]:
    """PII-minimized partnership referrals for realtor workspace (LRP-302)."""
    return await service.list_own_referrals(current_user)


@router.get("/realtor/pipeline", response_model=RealtorPipelineBoardResponse)
async def get_realtor_pipeline(
    _: None = Depends(require_mortgage_partner_enabled),
    current_user: User = Depends(get_current_user),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorPipelineBoardResponse:
    """Coarse pipeline board for realtor partnership (LRP-302)."""
    return await service.get_pipeline_board(current_user)


@router.get("/realtor/invites/preview", response_model=RealtorInvitePreviewResponse)
async def preview_realtor_invite(
    token: str = Query(min_length=16, max_length=512),
    _: None = Depends(require_mortgage_partner_enabled),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorInvitePreviewResponse:
    """Public invite preview for activation UI (no auth)."""
    return await service.preview_invite(token)


@router.post("/realtor/invites/accept", response_model=RealtorTokenResponse)
async def accept_realtor_invite(
    payload: RealtorInviteAcceptRequest,
    _: None = Depends(require_mortgage_partner_enabled),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorTokenResponse:
    """Accept invite, activate password, return staff JWT + realtor session."""
    return await service.accept_invite(payload)


@router.post(
    "/realtor/password-reset/request",
    response_model=RealtorPasswordResetRequestResponse,
)
async def request_realtor_password_reset(
    payload: RealtorPasswordResetRequest,
    _: None = Depends(require_mortgage_partner_enabled),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorPasswordResetRequestResponse:
    """Request realtor password reset (generic response; token in dev/test only)."""
    return await service.request_password_reset(payload)


@router.post("/realtor/password-reset/confirm", response_model=RealtorTokenResponse)
async def confirm_realtor_password_reset(
    payload: RealtorPasswordResetConfirm,
    _: None = Depends(require_mortgage_partner_enabled),
    service: RealtorPartnerService = Depends(get_realtor_service),
) -> RealtorTokenResponse:
    """Confirm realtor password reset and return JWT + realtor session."""
    return await service.confirm_password_reset(payload)
