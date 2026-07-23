"""Mortgage partner API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.modules.mortgage_partner.models import (
    PartnerAccessAction,
    PartnerOrgType,
    PartnerRole,
    PartnershipStatus,
    ReferralStatus,
)


class MortgagePartnerStatusResponse(BaseModel):
    mortgage_partner_enabled: bool
    capabilities: list[str]
    deferred_capabilities: list[str]


class PartnershipCreate(BaseModel):
    partner_organization_id: uuid.UUID
    display_name: str = Field(min_length=1, max_length=255)
    partner_type: PartnerOrgType = PartnerOrgType.LENDER
    status: PartnershipStatus = PartnershipStatus.ACTIVE
    notes: str | None = None


class PartnershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cro_organization_id: uuid.UUID
    partner_organization_id: uuid.UUID
    partner_type: PartnerOrgType
    status: PartnershipStatus
    display_name: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PartnershipMemberCreate(BaseModel):
    user_id: uuid.UUID
    partner_role: PartnerRole = PartnerRole.LOAN_OFFICER
    is_active: bool = True


class PartnershipMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partnership_id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    partner_role: PartnerRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PartnerReferralCreate(BaseModel):
    client_id: uuid.UUID
    case_id: uuid.UUID | None = None
    status: ReferralStatus = ReferralStatus.NEW
    source_label: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class PartnerReferralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partnership_id: uuid.UUID
    cro_organization_id: uuid.UUID
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    status: ReferralStatus
    source_label: str | None
    notes: str | None
    referred_by_user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    client_display_name: str | None = None


class PartnerAccessAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cro_organization_id: uuid.UUID
    partnership_id: uuid.UUID | None
    actor_user_id: uuid.UUID
    action: PartnerAccessAction
    resource_type: str
    resource_id: uuid.UUID | None
    detail: str | None
    occurred_at: datetime
    created_at: datetime


class PartnerRoleMatrixItem(BaseModel):
    role: PartnerRole
    permissions: list[str]


class PartnerRoleMatrixResponse(BaseModel):
    roles: list[PartnerRoleMatrixItem]
