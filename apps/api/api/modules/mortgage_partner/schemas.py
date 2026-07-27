"""Mortgage partner API schemas."""

import uuid
from datetime import datetime

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


class ReferralIntakeStatusResponse(BaseModel):
    referral_intake_enabled: bool
    organization_slug: str | None
    blockers: list[str] = Field(default_factory=list)
