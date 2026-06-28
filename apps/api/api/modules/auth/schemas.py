"""Authentication domain schemas."""

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from api.core.constants import TOKEN_TYPE_BEARER, UserRole
from api.core.responses import BaseSchema


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = TOKEN_TYPE_BEARER


class TokenPayload(BaseSchema):
    sub: str
    role: UserRole
    exp: int | None = None


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class UserBase(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.READ_ONLY


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    organization_id: uuid.UUID | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    organization_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class OrganizationResponse(BaseSchema):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
