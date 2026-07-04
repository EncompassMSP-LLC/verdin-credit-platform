"""SCIM 2.0 provision scaffold schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from api.core.scim_provisioning import ScimProvisioningStatus
from api.modules.enterprise.models import ScimProvisionLog


class ScimProvisioningStatusResponse(BaseModel):
    enabled: bool
    ready: bool
    bearer_token_configured: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: ScimProvisioningStatus) -> "ScimProvisioningStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            bearer_token_configured=status.bearer_token_configured,
            blockers=list(status.blockers),
        )


class ScimName(BaseModel):
    given_name: str | None = Field(default=None, alias="givenName", max_length=100)
    family_name: str | None = Field(default=None, alias="familyName", max_length=100)

    model_config = {"populate_by_name": True}


class ScimUserProvisionRequest(BaseModel):
    schemas: list[str] = Field(
        default_factory=lambda: ["urn:ietf:params:scim:schemas:core:2.0:User"]
    )
    user_name: str = Field(alias="userName", min_length=1, max_length=255)
    external_id: str = Field(alias="externalId", min_length=1, max_length=255)
    active: bool | None = True
    name: ScimName | None = None

    model_config = {"populate_by_name": True}


class ScimGroupProvisionRequest(BaseModel):
    schemas: list[str] = Field(
        default_factory=lambda: ["urn:ietf:params:scim:schemas:core:2.0:Group"]
    )
    display_name: str = Field(alias="displayName", min_length=1, max_length=255)
    external_id: str = Field(alias="externalId", min_length=1, max_length=255)

    model_config = {"populate_by_name": True}


class ScimMeta(BaseModel):
    resource_type: str = Field(alias="resourceType")
    created: datetime | None = None

    model_config = {"populate_by_name": True}


class ScimUserResourceResponse(BaseModel):
    schemas: list[str]
    id: uuid.UUID
    external_id: str = Field(alias="externalId")
    user_name: str = Field(alias="userName")
    active: bool
    meta: ScimMeta

    model_config = {"populate_by_name": True}

    @classmethod
    def from_log(cls, log: ScimProvisionLog, *, schema: str) -> "ScimUserResourceResponse":
        return cls(
            schemas=[schema],
            id=log.id,
            externalId=log.external_id,
            userName=log.display_name or log.external_id,
            active=log.active,
            meta=ScimMeta(resourceType="User", created=log.created_at),
        )


class ScimGroupResourceResponse(BaseModel):
    schemas: list[str]
    id: uuid.UUID
    external_id: str = Field(alias="externalId")
    display_name: str = Field(alias="displayName")
    meta: ScimMeta

    model_config = {"populate_by_name": True}

    @classmethod
    def from_log(cls, log: ScimProvisionLog, *, schema: str) -> "ScimGroupResourceResponse":
        return cls(
            schemas=[schema],
            id=log.id,
            externalId=log.external_id,
            displayName=log.display_name or log.external_id,
            meta=ScimMeta(resourceType="Group", created=log.created_at),
        )


class ScimUserListResponse(BaseModel):
    schemas: list[str] = Field(
        default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
    )
    total_results: int = Field(alias="totalResults")
    resources: list[ScimUserResourceResponse] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ScimGroupListResponse(BaseModel):
    schemas: list[str] = Field(
        default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
    )
    total_results: int = Field(alias="totalResults")
    resources: list[ScimGroupResourceResponse] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
