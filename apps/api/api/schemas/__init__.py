"""Pydantic schemas for API request/response models."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.models import CaseStatus, TaskPriority, TaskStatus, UserRole


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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


class CaseResponse(BaseSchema):
    id: uuid.UUID
    title: str
    description: str | None
    status: CaseStatus
    case_number: str | None
    organization_id: uuid.UUID
    account_id: uuid.UUID | None
    assigned_to_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class AccountResponse(BaseSchema):
    id: uuid.UUID
    name: str
    account_number: str | None
    email: str | None
    phone: str | None
    organization_id: uuid.UUID
    created_at: datetime


class DocumentResponse(BaseSchema):
    id: uuid.UUID
    title: str
    file_name: str
    mime_type: str | None
    file_size: int | None
    case_id: uuid.UUID
    created_at: datetime


class TaskResponse(BaseSchema):
    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    case_id: uuid.UUID
    assigned_to_id: uuid.UUID | None
    created_at: datetime


class HealthResponse(BaseSchema):
    status: str
    version: str
    environment: str


class VersionResponse(BaseSchema):
    version: str
    name: str
