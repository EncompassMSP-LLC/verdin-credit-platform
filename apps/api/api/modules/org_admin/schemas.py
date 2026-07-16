"""Organization admin schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.billing.schemas import OrganizationBillingSummary
from api.modules.org_admin.dispute_settings_models import (
    DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE,
    DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
    MAX_CROSS_BUREAU_BALANCE_TOLERANCE,
    MAX_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    MIN_CROSS_BUREAU_BALANCE_TOLERANCE,
    MIN_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    MIN_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
    OrganizationDisputeSettings,
)
from api.modules.org_admin.models import (
    ApiKeyScope,
    OAuthDeveloperApp,
    OAuthDeveloperAppStatus,
    OrganizationApiKey,
)


class OrgAdminStatusResponse(BaseSchema):
    org_admin_enabled: bool
    api_keys_enabled: bool
    capabilities: list[str]
    deferred_capabilities: list[str]


class OrganizationAdminSummary(BaseSchema):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    active_user_count: int
    active_api_key_count: int
    billing: OrganizationBillingSummary | None = None


class OrganizationDisputeSettingsResponse(BaseSchema):
    organization_id: uuid.UUID
    cross_bureau_balance_tolerance: Decimal
    platform_default_tolerance: Decimal = DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE
    reinvestigation_benchmark_baseline_days: int = DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS
    reinvestigation_benchmark_recent_days: int = DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS
    platform_default_baseline_days: int = DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS
    platform_default_recent_days: int = DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS
    updated_at: datetime | None = None

    @classmethod
    def from_model(
        cls, settings: OrganizationDisputeSettings
    ) -> "OrganizationDisputeSettingsResponse":
        return cls(
            organization_id=settings.organization_id,
            cross_bureau_balance_tolerance=settings.cross_bureau_balance_tolerance,
            reinvestigation_benchmark_baseline_days=(
                settings.reinvestigation_benchmark_baseline_days
            ),
            reinvestigation_benchmark_recent_days=settings.reinvestigation_benchmark_recent_days,
            updated_at=settings.updated_at,
        )

    @classmethod
    def default_for_organization(
        cls, organization_id: uuid.UUID
    ) -> "OrganizationDisputeSettingsResponse":
        return cls(
            organization_id=organization_id,
            cross_bureau_balance_tolerance=DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE,
            reinvestigation_benchmark_baseline_days=(
                DEFAULT_REINVESTIGATION_BENCHMARK_BASELINE_DAYS
            ),
            reinvestigation_benchmark_recent_days=DEFAULT_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
            updated_at=None,
        )


class OrganizationDisputeSettingsUpdate(BaseSchema):
    cross_bureau_balance_tolerance: Decimal | None = Field(
        default=None,
        ge=MIN_CROSS_BUREAU_BALANCE_TOLERANCE,
        le=MAX_CROSS_BUREAU_BALANCE_TOLERANCE,
    )
    reinvestigation_benchmark_baseline_days: int | None = Field(
        default=None,
        ge=MIN_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
        le=MAX_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    )
    reinvestigation_benchmark_recent_days: int | None = Field(
        default=None,
        ge=MIN_REINVESTIGATION_BENCHMARK_RECENT_DAYS,
        le=MAX_REINVESTIGATION_BENCHMARK_BASELINE_DAYS,
    )


class ApiKeyCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    scopes: list[ApiKeyScope] = Field(default_factory=lambda: [ApiKeyScope.READ])
    expires_at: datetime | None = None


class ApiKeyResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    key_prefix: str
    scopes: list[ApiKeyScope]
    is_active: bool
    last_used_at: datetime | None
    revoked_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, api_key: OrganizationApiKey) -> "ApiKeyResponse":
        return cls(
            id=api_key.id,
            organization_id=api_key.organization_id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            scopes=api_key.scope_values,
            is_active=api_key.is_active,
            last_used_at=api_key.last_used_at,
            revoked_at=api_key.revoked_at,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
            created_by_id=api_key.created_by_id,
            updated_by_id=api_key.updated_by_id,
        )


class ApiKeyCreateResponse(ApiKeyResponse):
    api_key: str


class ApiKeyRateLimitStatusResponse(BaseSchema):
    enabled: bool
    limit_per_minute: int
    backend: str


class ApiKeyRotateResponse(BaseSchema):
    api_key: str
    previous_key: ApiKeyResponse
    new_key: ApiKeyResponse


class DeveloperPortalResponse(BaseSchema):
    enabled: bool
    ready: bool
    rotation_enabled: bool
    blockers: list[str]
    active_api_key_count: int
    rate_limit: ApiKeyRateLimitStatusResponse
    api_keys: list[ApiKeyResponse]


class OAuthDeveloperAppCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    redirect_uri: str = Field(min_length=1, max_length=1024)
    scopes: list[str] = Field(default_factory=lambda: ["read"])


class OAuthDeveloperAppResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    redirect_uri: str
    scopes: list[str]
    status: OAuthDeveloperAppStatus
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    revoked_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, app: OAuthDeveloperApp) -> "OAuthDeveloperAppResponse":
        return cls(
            id=app.id,
            organization_id=app.organization_id,
            name=app.name,
            redirect_uri=app.redirect_uri,
            scopes=app.scopes,
            status=app.status,
            requested_by_user_id=app.requested_by_user_id,
            approved_by_user_id=app.approved_by_user_id,
            requested_at=app.requested_at,
            approved_at=app.approved_at,
            revoked_at=app.revoked_at,
            error_message=app.error_message,
            created_at=app.created_at,
            updated_at=app.updated_at,
        )
