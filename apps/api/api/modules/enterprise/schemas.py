"""Enterprise identity enrollment schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TotpEnrollmentStartResponse(BaseModel):
    secret: str
    otpauth_url: str
    issuer: str


class TotpEnrollmentConfirmRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)


class TotpEnrollmentStatusResponse(BaseModel):
    enrolled: bool
    enrolled_at: datetime | None = None
    pending: bool = False


class SsoEnrollmentStartResponse(BaseModel):
    authorization_url: str
    state: str
    provider: str


class SsoEnrollmentCompleteRequest(BaseModel):
    code: str = Field(min_length=1)
    state: str = Field(min_length=1)


class SsoEnrollmentStatusResponse(BaseModel):
    linked: bool
    provider: str | None = None
    issuer_url: str | None = None
    linked_at: datetime | None = None
    idp_subject: str | None = None


class SsoEnrollmentCompleteResponse(BaseModel):
    linked: bool
    provider: str
    issuer_url: str
    idp_subject: str
    linked_at: datetime
    user_id: uuid.UUID
