"""Pydantic schemas for admin-gated native mobile passkey client scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.native_mobile_passkey_client import (
    NativeMobilePasskeyClientStatus as ClientGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.enterprise.native_mobile_passkey_client_models import (
    NativeMobilePasskeyClientRun,
    NativeMobilePasskeyClientRunStatus,
)


class NativeMobilePasskeyClientStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    mobile_passkey_readiness_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: ClientGateStatus) -> "NativeMobilePasskeyClientStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            mobile_passkey_readiness_ready=status.mobile_passkey_readiness_ready,
            blockers=list(status.blockers),
        )


class NativeMobilePasskeyClientSubmitRequest(BaseSchema):
    client_summary: str = Field(min_length=1, max_length=2000)
    platform: str = Field(min_length=1, max_length=50)


class NativeMobilePasskeyClientRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    mobile_passkey_readiness_run_id: uuid.UUID
    entity_id: str
    status: NativeMobilePasskeyClientRunStatus
    client_summary: str
    platform: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: NativeMobilePasskeyClientRun
    ) -> "NativeMobilePasskeyClientRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            mobile_passkey_readiness_run_id=run.mobile_passkey_readiness_run_id,
            entity_id=run.entity_id,
            status=run.status,
            client_summary=run.client_summary,
            platform=run.platform,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class NativeMobilePasskeyClientRunResultResponse(BaseSchema):
    completed_at: datetime
    run: NativeMobilePasskeyClientRunResponse


class NativeMobilePasskeyClientRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
