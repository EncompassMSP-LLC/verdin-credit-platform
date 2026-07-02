"""Client portal schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr

from api.core.responses import BaseSchema
from api.modules.auth.schemas import LoginRequest, Password, RefreshTokenRequest, TokenResponse
from api.modules.cases.models import CaseStage, CaseStatus
from api.modules.client_portal.models import ClientPortalUser

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
