"""Pydantic schemas for native mobile app store distribution scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.native_mobile_app_store_distribution import (
    NativeMobileAppStoreDistributionStatus as DistributionGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.enterprise.native_mobile_app_store_distribution_models import (
    NativeMobileAppStoreDistributionRun,
    NativeMobileAppStoreDistributionRunStatus,
)


class NativeMobileAppStoreDistributionStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    native_mobile_passkey_client_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: DistributionGateStatus
    ) -> "NativeMobileAppStoreDistributionStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            native_mobile_passkey_client_ready=status.native_mobile_passkey_client_ready,
            blockers=list(status.blockers),
        )


class NativeMobileAppStoreDistributionSubmitRequest(BaseSchema):
    distribution_summary: str = Field(min_length=1, max_length=2000)
    store_target: str = Field(min_length=1, max_length=50)


class NativeMobileAppStoreDistributionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    native_mobile_passkey_client_run_id: uuid.UUID
    entity_id: str
    status: NativeMobileAppStoreDistributionRunStatus
    distribution_summary: str
    platform: str
    store_target: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    ready_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: NativeMobileAppStoreDistributionRun
    ) -> "NativeMobileAppStoreDistributionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            native_mobile_passkey_client_run_id=run.native_mobile_passkey_client_run_id,
            entity_id=run.entity_id,
            status=run.status,
            distribution_summary=run.distribution_summary,
            platform=run.platform,
            store_target=run.store_target,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            ready_at=run.ready_at,
            error_message=run.error_message,
        )


class NativeMobileAppStoreDistributionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: NativeMobileAppStoreDistributionRunResponse


class NativeMobileAppStoreDistributionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
