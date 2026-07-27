"""Organization context API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.modules.auth.models import OrganizationType
from api.modules.org_context.models import OrgDemoFeature


class OrganizationContextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: uuid.UUID
    name: str
    slug: str
    organization_type: OrganizationType
    is_active: bool
    feature_flags: dict[str, bool]
    demo_capabilities_allowed: bool
    allow_demo_orgs: bool
    enable_sample_data: bool
    enable_demo_login: bool
    created_at: datetime


class OrganizationFeatureFlagUpsert(BaseModel):
    feature: OrgDemoFeature
    enabled: bool


class DemoSampleBorrowersRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=25)


class DemoSampleBorrowersResponse(BaseModel):
    created_client_ids: list[uuid.UUID]
    organization_id: uuid.UUID
    feature: OrgDemoFeature = OrgDemoFeature.SAMPLE_BORROWERS
