"""Authentication domain schemas."""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, EmailStr, Field

from api.core.constants import TOKEN_TYPE_BEARER, UserRole
from api.core.responses import BaseSchema
from api.core.security import MAX_PASSWORD_BYTES, password_within_bcrypt_limit


def _validate_password_length(value: str) -> str:
    if not password_within_bcrypt_limit(value):
        raise ValueError(f"Password must not exceed {MAX_PASSWORD_BYTES} bytes when UTF-8 encoded")
    return value


Password = Annotated[str, Field(min_length=8), AfterValidator(_validate_password_length)]


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
    password: Password
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
