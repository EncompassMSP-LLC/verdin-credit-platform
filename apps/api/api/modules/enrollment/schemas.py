"""Client enrollment API schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from api.core.responses import BaseSchema
from api.modules.client_portal.schemas import PortalTokenResponse


class ClientEnrollmentStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    payment_required: bool
    checkout_available: bool
    organization_slug: str
    price_id: str | None
    annual_credit_report_url: str
    blockers: list[str]


class ClientEnrollmentIntakeRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    mailing_address_line1: str = Field(min_length=1, max_length=255)
    mailing_address_line2: str | None = Field(default=None, max_length=255)
    mailing_city: str = Field(min_length=1, max_length=100)
    mailing_state: str = Field(min_length=1, max_length=50)
    mailing_postal_code: str = Field(min_length=1, max_length=20)


class ClientEnrollmentCheckoutResponse(BaseSchema):
    enrollment_id: uuid.UUID
    checkout_session_id: str
    checkout_url: str


class ClientEnrollmentCompleteRequest(BaseSchema):
    session_id: str = Field(min_length=1, max_length=255)


class ClientEnrollmentSessionResponse(BaseSchema):
    enrollment_id: uuid.UUID
    status: str
    payment_status: str | None
    case_id: uuid.UUID | None
    client_id: uuid.UUID | None
    completed_at: datetime | None
    error_message: str | None


class ClientEnrollmentCompleteResponse(BaseSchema):
    enrollment: ClientEnrollmentSessionResponse
    portal: PortalTokenResponse
