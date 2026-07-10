"""Shared API response models."""

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseSchema):
    detail: str
    code: str | None = None


class MessageResponse(BaseSchema):
    message: str


class HealthResponse(BaseSchema):
    status: str
    version: str
    environment: str


class ReadinessResponse(BaseSchema):
    status: str
    checks: dict[str, str]


class VersionResponse(BaseSchema):
    version: str
    name: str


class IDResponse(BaseSchema):
    id: str = Field(description="UUID of the created resource")
