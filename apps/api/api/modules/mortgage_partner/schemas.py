"""Mortgage partner API schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from api.modules.mortgage_partner.models import (
    LoanPipelineStage,
    PartnerAccessAction,
    PartnerContactRole,
    PartnerOrgType,
    PartnerRole,
    PartnershipStatus,
    ReferralStatus,
)


class MortgagePartnerStatusResponse(BaseModel):
    mortgage_partner_enabled: bool
    capabilities: list[str]
    deferred_capabilities: list[str]


class PartnershipCreate(BaseModel):
    partner_organization_id: uuid.UUID
    display_name: str = Field(min_length=1, max_length=255)
    partner_type: PartnerOrgType = PartnerOrgType.LENDER
    status: PartnershipStatus = PartnershipStatus.ACTIVE
    notes: str | None = None


class PartnershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cro_organization_id: uuid.UUID
    partner_organization_id: uuid.UUID
    partner_type: PartnerOrgType
    status: PartnershipStatus
    display_name: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    # CRM enrichment (LRP-101) — not ORM columns
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    active_referral_count: int = 0


class PartnerContactCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    job_title: str | None = Field(default=None, max_length=120)
    contact_role: PartnerContactRole = PartnerContactRole.OTHER
    is_primary: bool = False
    is_active: bool = True
    user_id: uuid.UUID | None = None
    notes: str | None = None


class PartnerContactUpdate(BaseModel):
    """Staff-mediated contact update — at least one field required."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    job_title: str | None = Field(default=None, max_length=120)
    contact_role: PartnerContactRole | None = None
    is_primary: bool | None = None
    is_active: bool | None = None
    user_id: uuid.UUID | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PartnerContactUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class PartnerContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partnership_id: uuid.UUID
    cro_organization_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    job_title: str | None
    contact_role: PartnerContactRole
    is_primary: bool
    is_active: bool
    user_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PartnershipMemberCreate(BaseModel):
    user_id: uuid.UUID
    partner_role: PartnerRole = PartnerRole.LOAN_OFFICER
    is_active: bool = True


class PartnershipMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partnership_id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    partner_role: PartnerRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PartnerLoanMilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    referral_id: uuid.UUID
    organization_id: uuid.UUID
    label: str
    sort_order: int
    complete: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MilestoneReplaceItem(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    sort_order: int = 0
    complete: bool = False


class MilestoneReplacePayload(BaseModel):
    milestones: list[MilestoneReplaceItem] = Field(default_factory=list)


class PartnerReferralCreate(BaseModel):
    client_id: uuid.UUID
    case_id: uuid.UUID | None = None
    status: ReferralStatus = ReferralStatus.NEW
    pipeline_stage: LoanPipelineStage = LoanPipelineStage.REFERRED
    source_label: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class PartnerReferralUpdate(BaseModel):
    """Staff-mediated referral update — at least one field required."""

    status: ReferralStatus | None = None
    pipeline_stage: LoanPipelineStage | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PartnerReferralUpdate":
        if self.status is None and self.pipeline_stage is None and self.notes is None:
            raise ValueError("At least one of status, pipeline_stage, or notes must be provided")
        return self


class PartnerReferralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partnership_id: uuid.UUID
    cro_organization_id: uuid.UUID
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    status: ReferralStatus
    pipeline_stage: LoanPipelineStage
    pipeline_stage_changed_at: datetime | None
    source_label: str | None
    notes: str | None
    referred_by_user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    client_display_name: str | None = None
    milestones: list[PartnerLoanMilestoneResponse] = Field(default_factory=list)


class PipelineCardResponse(BaseModel):
    """Lightweight card for the pipeline board view."""

    referral_id: uuid.UUID
    client_id: uuid.UUID
    client_display_name: str | None
    pipeline_stage: LoanPipelineStage
    referral_status: ReferralStatus
    days_in_stage: int
    stage_changed_at: datetime | None
    notes: str | None
    source_label: str | None


class DashboardSummaryResponse(BaseModel):
    """Aggregate counts for the lender dashboard."""

    total_referrals: int
    counts_by_stage: dict[str, int]
    near_ready_count: int
    mortgage_ready_count: int
    in_underwriting_count: int
    funded_count: int
    declined_count: int


class PartnerAccessAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cro_organization_id: uuid.UUID
    partnership_id: uuid.UUID | None
    actor_user_id: uuid.UUID
    action: PartnerAccessAction
    resource_type: str
    resource_id: uuid.UUID | None
    detail: str | None
    occurred_at: datetime
    created_at: datetime


class PartnerRoleMatrixItem(BaseModel):
    role: PartnerRole
    permissions: list[str]


class PartnerRoleMatrixResponse(BaseModel):
    roles: list[PartnerRoleMatrixItem]


# ---------------------------------------------------------------------------
# Readiness report (slice 4) — reuses credit_analysis_runs payload
# ---------------------------------------------------------------------------


class ReadinessDimension(BaseModel):
    key: str
    label: str
    score: int
    weight: float


class ReadinessBlocker(BaseModel):
    id: str
    title: str
    impact: str
    action: str


class ReadinessPriorityTask(BaseModel):
    """Derived from the referral's milestone checklist."""

    id: str
    label: str
    complete: bool
    completed_at: datetime | None


class MortgageReadinessReportResponse(BaseModel):
    """Advisory readiness report for a partner referral.

    Disclaimer: Lending Readiness Score™ is an advisory tool for organizing
    credit and documentation work toward a mortgage conversation. It is not a
    credit score from a consumer reporting agency, not an underwriting decision,
    and not a guarantee of loan approval or terms.
    """

    referral_id: uuid.UUID
    case_id: uuid.UUID
    credit_analysis_run_id: uuid.UUID
    client_display_name: str | None
    mortgage_readiness_score: int
    band: str
    generated_at: datetime
    dimensions: list[ReadinessDimension]
    blockers: list[ReadinessBlocker]
    priority_tasks: list[ReadinessPriorityTask]
    docs_status: str
    partner_notes: str | None
    formula_version: str
    score_version: str
    disclaimer: str


class ReadinessReportSummary(BaseModel):
    """Lightweight summary for the list endpoint."""

    referral_id: uuid.UUID
    case_id: uuid.UUID
    credit_analysis_run_id: uuid.UUID
    client_display_name: str | None
    mortgage_readiness_score: int
    band: str
    generated_at: datetime
    formula_version: str
    score_version: str
    disclaimer: str


class ReferralIntakeCreate(BaseModel):
    """Public web-form referral intake payload (LRP-103)."""

    partner_org_name: str = Field(min_length=1, max_length=255)
    lo_name: str = Field(min_length=1, max_length=255)
    lo_email: EmailStr
    lo_phone: str | None = Field(default=None, max_length=50)
    borrower_name: str = Field(min_length=1, max_length=255)
    borrower_email: EmailStr | None = None
    borrower_phone: str | None = Field(default=None, max_length=50)
    product_intent: str | None = Field(default=None, max_length=255)
    known_gaps: str | None = None
    notes: str | None = None
    consent_attested: bool
    partnership_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def require_borrower_contact_and_consent(self) -> "ReferralIntakeCreate":
        if not self.consent_attested:
            raise ValueError("Borrower consent attestation is required")
        if not self.borrower_email and not (self.borrower_phone and self.borrower_phone.strip()):
            raise ValueError("Borrower email or phone is required")
        return self


class ReferralIntakeResponse(BaseModel):
    intake_id: uuid.UUID
    status: str
    partnership_id: uuid.UUID | None
    referral_id: uuid.UUID | None
    client_id: uuid.UUID | None
    case_id: uuid.UUID | None
    task_id: uuid.UUID | None
    message: str
    quarantine_reason: str | None = None
    orchestrator_run_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None


class ReferralIntakeOrchestratorResponse(BaseModel):
    id: uuid.UUID
    intake_run_id: uuid.UUID
    case_id: uuid.UUID | None
    referral_id: uuid.UUID | None
    assigned_user_id: uuid.UUID | None
    status: str
    schema_version: str
    started_at: datetime
    completed_at: datetime | None
    payload: dict[str, Any]


class ReferralIntakeStatusResponse(BaseModel):
    referral_intake_enabled: bool
    organization_slug: str | None
    blockers: list[str] = Field(default_factory=list)


class CrmAutomationRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    enabled: bool
    trigger: str
    action: str
    channel: str
    last_fired_at: datetime | None
    fire_count: int
    created_at: datetime
    updated_at: datetime


class CrmAutomationRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    enabled: bool = True
    trigger: Literal[
        "stage_enter",
        "referral_created",
        "task_overdue",
        "score_band_change",
        "document_uploaded",
        "manual",
    ]
    action: str = Field(min_length=1, max_length=500)
    channel: Literal["task", "email", "sms", "notification", "stage"]


class CrmAutomationRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    enabled: bool | None = None
    trigger: (
        Literal[
            "stage_enter",
            "referral_created",
            "task_overdue",
            "score_band_change",
            "document_uploaded",
            "manual",
        ]
        | None
    ) = None
    action: str | None = Field(default=None, min_length=1, max_length=500)
    channel: Literal["task", "email", "sms", "notification", "stage"] | None = None


class CrmAppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID | None
    title: str
    appointment_type: str
    status: str
    starts_at: datetime
    ends_at: datetime
    location: str | None
    meeting_url: str | None
    related_name: str | None
    owner_user_id: uuid.UUID | None
    borrower_name: str | None
    borrower_email: str | None
    borrower_phone: str | None
    referring_lo_email: str | None
    referring_lo_name: str | None
    tcpa_consent: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CrmAppointmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    appointment_type: Literal["consultation", "call", "meeting", "follow_up", "review"] = (
        "consultation"
    )
    starts_at: datetime
    ends_at: datetime
    case_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    meeting_url: str | None = Field(default=None, max_length=500)
    related_name: str | None = Field(default=None, max_length=255)
    owner_user_id: uuid.UUID | None = None
    borrower_name: str | None = Field(default=None, max_length=255)
    borrower_email: EmailStr | None = None
    borrower_phone: str | None = Field(default=None, max_length=50)
    referring_lo_email: EmailStr | None = None
    referring_lo_name: str | None = Field(default=None, max_length=255)
    tcpa_consent: bool = False
    notes: str | None = None

    @model_validator(mode="after")
    def ends_after_starts(self) -> "CrmAppointmentCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class CrmAppointmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    appointment_type: Literal["consultation", "call", "meeting", "follow_up", "review"] | None = (
        None
    )
    status: Literal["scheduled", "completed", "cancelled", "no_show"] | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = None
    meeting_url: str | None = None
    related_name: str | None = None
    owner_user_id: uuid.UUID | None = None
    borrower_name: str | None = None
    borrower_email: EmailStr | None = None
    borrower_phone: str | None = None
    referring_lo_email: EmailStr | None = None
    referring_lo_name: str | None = None
    tcpa_consent: bool | None = None
    notes: str | None = None


class AppointmentReminderRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    appointment_id: uuid.UUID
    offset_key: str
    status: str
    schema_version: str
    matrix_dispatch_id: uuid.UUID | None
    started_at: datetime
    completed_at: datetime | None
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AppointmentReminderProcessResponse(BaseModel):
    processed_count: int
    runs: list[AppointmentReminderRunResponse]


class NurtureStepResponse(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    step_order: int
    delay_days: int
    channel: str
    template_key: str
    subject: str
    body_template: str


class NurtureProgramResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    audience: str
    enrollment_lifecycle_stage: str
    enabled: bool
    steps: list[NurtureStepResponse]
    created_at: datetime
    updated_at: datetime


class NurtureEnrollmentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    program_id: uuid.UUID
    partnership_id: uuid.UUID | None
    contact_name: str
    contact_email: str | None
    contact_phone: str | None
    status: str
    current_step_order: int
    next_run_at: datetime | None
    enrolled_at: datetime
    paused_at: datetime | None
    completed_at: datetime | None
    exited_at: datetime | None
    exit_reason: str | None
    marketing_opt_in: bool
    tcpa_consent: bool
    created_at: datetime
    updated_at: datetime


class NurtureEnrollmentCreate(BaseModel):
    program_id: uuid.UUID
    contact_name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    partnership_id: uuid.UUID | None = None
    marketing_opt_in: bool = True
    tcpa_consent: bool = False


class NurtureEnrollmentUpdate(BaseModel):
    status: Literal["active", "paused", "completed", "exited"] | None = None
    marketing_opt_in: bool | None = None
    tcpa_consent: bool | None = None
    exit_reason: str | None = Field(default=None, max_length=100)


class NurtureDeliveryRunResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    enrollment_id: uuid.UUID
    program_id: uuid.UUID
    step_id: uuid.UUID
    channel: str
    status: str
    schema_version: str
    attempted_at: datetime
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class NurtureDeliveryProcessResponse(BaseModel):
    processed_count: int
    runs: list[NurtureDeliveryRunResponse]


class WeeklyDigestSubscriptionResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    partnership_id: uuid.UUID
    recipient_name: str
    recipient_email: str
    enabled: bool
    marketing_opt_in: bool
    send_weekday: int
    created_at: datetime
    updated_at: datetime


class WeeklyDigestSubscriptionCreate(BaseModel):
    partnership_id: uuid.UUID
    recipient_name: str = Field(min_length=1, max_length=255)
    recipient_email: EmailStr
    send_weekday: int = Field(default=1, ge=1, le=7)
    marketing_opt_in: bool = True


class WeeklyDigestSubscriptionUpdate(BaseModel):
    enabled: bool | None = None
    marketing_opt_in: bool | None = None
    recipient_name: str | None = Field(default=None, min_length=1, max_length=255)
    send_weekday: int | None = Field(default=None, ge=1, le=7)


class WeeklyDigestRunResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    partnership_id: uuid.UUID
    subscription_id: uuid.UUID
    week_key: str
    status: str
    schema_version: str
    attempted_at: datetime
    payload: dict[str, Any]
    body_text: str | None
    created_at: datetime
    updated_at: datetime


class WeeklyDigestProcessResponse(BaseModel):
    processed_count: int
    week_key: str
    runs: list[WeeklyDigestRunResponse]


# --- Realtor partner role + login (LRP-301) ---


class RealtorInviteCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    notes: str | None = None


class RealtorInviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    partnership_id: uuid.UUID
    partner_organization_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    expires_at: datetime
    accepted_at: datetime | None
    revoked_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    # Returned once on create for operator handoff (not stored plaintext)
    invite_token: str | None = None


class RealtorInvitePreviewResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    partnership_display_name: str
    partner_organization_name: str
    expires_at: datetime
    already_accepted: bool


class RealtorInviteAcceptRequest(BaseModel):
    token: str = Field(min_length=16, max_length=512)
    password: str = Field(min_length=8, max_length=128)


class RealtorPasswordResetRequest(BaseModel):
    email: EmailStr


class RealtorPasswordResetConfirm(BaseModel):
    token: str = Field(min_length=16, max_length=512)
    password: str = Field(min_length=8, max_length=128)


class RealtorPasswordResetRequestResponse(BaseModel):
    detail: str
    # Present only in non-production for test/operator DX — never email the raw token in prod
    reset_token: str | None = None


class RealtorSessionResponse(BaseModel):
    """Authenticated realtor workspace context (LRP-301)."""

    user_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    display_name: str
    partner_role: PartnerRole
    permissions: list[str]
    membership_id: uuid.UUID
    membership_active: bool
    partnership_id: uuid.UUID
    partnership_display_name: str
    cro_organization_id: uuid.UUID
    partner_organization_id: uuid.UUID
    partner_organization_name: str
    partner_type: PartnerOrgType


class RealtorTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    realtor: RealtorSessionResponse


# --- Realtor portal MVP (LRP-302) ---


class RealtorReferralCardResponse(BaseModel):
    """PII-minimized referral card for realtor workspace (no tradelines / notes dumps)."""

    referral_id: uuid.UUID
    borrower_initials: str
    pipeline_stage: LoanPipelineStage
    referral_status: ReferralStatus
    days_in_stage: int
    stage_changed_at: datetime | None
    source_label: str | None
    is_own_referral: bool
    created_at: datetime


class RealtorPipelineBoardResponse(BaseModel):
    partnership_id: uuid.UUID
    partnership_display_name: str
    cards: list[RealtorReferralCardResponse]


class RealtorPortalDashboardResponse(BaseModel):
    partnership_id: uuid.UUID
    partnership_display_name: str
    total_referrals: int
    own_referral_count: int
    counts_by_stage: dict[str, int]
    near_ready_count: int
    mortgage_ready_count: int
    in_underwriting_count: int
    funded_count: int
    declined_count: int
    recent: list[RealtorReferralCardResponse]
    advisory_disclaimer: str = (
        "Lending Readiness Score™ and pipeline status are advisory organizing tools. "
        "They are not credit scores from a consumer reporting agency, not underwriting "
        "decisions, and not guarantees of loan approval or terms."
    )
