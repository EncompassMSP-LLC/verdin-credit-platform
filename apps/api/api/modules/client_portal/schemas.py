"""Client portal schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import EmailStr

from api.core.responses import BaseSchema
from api.modules.auth.schemas import LoginRequest, Password, RefreshTokenRequest, TokenResponse
from api.modules.cases.models import CaseStage, CaseStatus
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.push_models import PortalPushSubscription

PortalLoginRequest = LoginRequest
PortalRefreshTokenRequest = RefreshTokenRequest
PortalTokenResponse = TokenResponse


class ClientPortalUserProvision(BaseSchema):
    email: EmailStr
    password: Password


class ClientPortalUserUpdate(BaseSchema):
    email: EmailStr | None = None
    password: Password | None = None
    is_active: bool | None = None


class ClientPortalUserResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    email: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, portal_user: ClientPortalUser) -> "ClientPortalUserResponse":
        return cls(
            id=portal_user.id,
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
            email=portal_user.email,
            is_active=portal_user.is_active,
            last_login_at=portal_user.last_login_at,
            created_at=portal_user.created_at,
            updated_at=portal_user.updated_at,
        )


class PortalMeResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    email: str
    client_display_name: str
    is_active: bool
    last_login_at: datetime | None


class PortalCaseSummaryResponse(BaseSchema):
    id: uuid.UUID
    case_number: str | None
    title: str
    status: CaseStatus
    stage: CaseStage
    opened_at: datetime
    closed_at: datetime | None
    updated_at: datetime


class PortalCaseDetailResponse(PortalCaseSummaryResponse):
    dispute_accounts: dict[str, int]
    account_count: int


class PortalCaseProgressResponse(BaseSchema):
    items: list[PortalCaseSummaryResponse]


class PortalDocumentResponse(BaseSchema):
    id: uuid.UUID
    case_id: uuid.UUID
    title: str
    description: str | None
    file_name: str
    mime_type: str | None
    file_size: int | None
    processing_status: str
    created_at: datetime


class PortalCaseDocumentsResponse(BaseSchema):
    items: list[PortalDocumentResponse]


class PortalChecklistItemResponse(BaseSchema):
    id: str
    case_id: uuid.UUID
    title: str
    category: str
    priority: str
    status: str
    due_date: datetime | None = None
    sort_order: int
    updated_at: datetime
    description: str | None = None


class PortalChecklistResponse(BaseSchema):
    case_id: uuid.UUID
    items: list[PortalChecklistItemResponse]


class PortalChecklistUpdateRequest(BaseSchema):
    status: str


class PortalReadinessReportResponse(BaseSchema):
    """Borrower-facing readiness report (band is source of truth; LRP-106)."""

    case_id: uuid.UUID
    credit_analysis_run_id: uuid.UUID
    band: str
    updated_at: datetime
    generated_at: datetime
    reports_evaluated: int
    tradelines_evaluated: int
    formula_version: str
    score_version: str
    disclaimer: str
    dimensions: list[dict[str, Any]]
    blockers: list[dict[str, Any]]


class PortalTimelineItemResponse(BaseSchema):
    id: str
    event_at: datetime
    event_type: str
    title: str
    detail: str | None = None
    href: str | None = None


class PortalTimelineResponse(BaseSchema):
    case_id: uuid.UUID
    items: list[PortalTimelineItemResponse]


class PortalDisputeStrategyStageSuggestion(BaseSchema):
    stage_kind: str
    title: str
    objective: str
    recommended: bool


class PortalDisputeStrategyAccountSuggestion(BaseSchema):
    creditor_label: str
    account_number_masked: str | None = None
    summary: str
    recommended_stage_titles: list[str]
    stages: list[PortalDisputeStrategyStageSuggestion]


class PortalDisputeStrategySuggestionsSummary(BaseSchema):
    accounts_planned: int = 0
    issues_covered: int = 0
    high_strength_accounts: int = 0
    cfpb_recommended: int = 0
    attorney_recommended: int = 0


class PortalDisputeStrategySuggestionsResponse(BaseSchema):
    """Borrower-safe advisory dispute strategy suggestions (LRP-403).

    Never prepares or sends letters. Staff-mediated planning aid only.
    """

    case_id: uuid.UUID
    disclaimer: str
    staff_mediated: bool = True
    auto_send: bool = False
    source: str
    generated_at: datetime | None = None
    summary: PortalDisputeStrategySuggestionsSummary
    suggestions: list[PortalDisputeStrategyAccountSuggestion]


class PortalPushSubscribeRequest(BaseSchema):
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str | None = None


class PortalPushStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    provider: str
    vapid_public_key: str | None
    blockers: list[str]
    active_subscription_count: int


class PortalPushSubscriptionResponse(BaseSchema):
    id: uuid.UUID
    endpoint: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, subscription: PortalPushSubscription) -> "PortalPushSubscriptionResponse":
        return cls(
            id=subscription.id,
            endpoint=subscription.endpoint,
            is_active=subscription.is_active,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )
