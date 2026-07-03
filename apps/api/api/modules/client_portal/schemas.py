"""Client portal schemas."""

import uuid
from datetime import datetime

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
