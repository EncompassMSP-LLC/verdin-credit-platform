"""SCIM provisioning service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.core.scim_provisioning import get_scim_provisioning_settings
from api.modules.auth.models import User
from api.modules.enterprise.models import (
    ScimProvisionLog,
    ScimProvisionOperation,
    ScimResourceType,
)
from api.modules.enterprise.scim_repository import ScimProvisioningRepository
from api.modules.enterprise.scim_schemas import (
    ScimGroupListResponse,
    ScimGroupProvisionRequest,
    ScimGroupResourceResponse,
    ScimProvisioningStatusResponse,
    ScimUserListResponse,
    ScimUserProvisionRequest,
    ScimUserResourceResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE

_SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
_SCIM_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"


class ScimProvisioningService:
    def __init__(
        self, repo: ScimProvisioningRepository, session: AsyncSession | None = None
    ) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> ScimProvisioningService:
        return cls(ScimProvisioningRepository(session), session=session)

    def get_status_response(self) -> ScimProvisioningStatusResponse:
        status_value = get_scim_provisioning_settings()
        return ScimProvisioningStatusResponse.from_status(status_value)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view SCIM provisioning",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage SCIM provisioning",
            )

    async def _upsert_log(
        self,
        *,
        organization_id: uuid.UUID,
        resource_type: ScimResourceType,
        external_id: str,
        display_name: str | None,
        active: bool,
        operation: ScimProvisionOperation,
        auth_mode: str,
        provisioned_by_user_id: uuid.UUID | None,
    ) -> ScimProvisionLog:
        existing = await self._repo.get_provision_log(
            organization_id,
            resource_type=resource_type,
            external_id=external_id,
        )
        if existing is None:
            log = ScimProvisionLog(
                organization_id=organization_id,
                resource_type=resource_type,
                operation=operation,
                external_id=external_id,
                display_name=display_name,
                active=active,
                auth_mode=auth_mode,
                provisioned_by_user_id=provisioned_by_user_id,
            )
        else:
            existing.operation = operation
            existing.display_name = display_name
            existing.active = active
            existing.auth_mode = auth_mode
            existing.provisioned_by_user_id = provisioned_by_user_id
            log = existing
        saved = await self._repo.save_provision_log(log)
        if self._session is not None:
            await self._session.commit()
        return saved

    async def provision_user(
        self,
        user: User,
        body: ScimUserProvisionRequest,
        *,
        auth_mode: str = "staff",
    ) -> ScimUserResourceResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        existing = await self._repo.get_provision_log(
            organization_id,
            resource_type=ScimResourceType.USER,
            external_id=body.external_id,
        )
        operation = (
            ScimProvisionOperation.CREATE if existing is None else ScimProvisionOperation.UPDATE
        )
        if body.active is False:
            operation = ScimProvisionOperation.DEACTIVATE
        display_name = body.user_name
        if body.name is not None:
            parts = [part for part in (body.name.given_name, body.name.family_name) if part]
            if parts:
                display_name = " ".join(parts)
        saved = await self._upsert_log(
            organization_id=organization_id,
            resource_type=ScimResourceType.USER,
            external_id=body.external_id,
            display_name=display_name,
            active=body.active if body.active is not None else True,
            operation=operation,
            auth_mode=auth_mode,
            provisioned_by_user_id=user.id,
        )
        return ScimUserResourceResponse.from_log(saved, schema=_SCIM_USER_SCHEMA)

    async def list_users(self, user: User) -> ScimUserListResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        logs = await self._repo.list_provision_logs(
            organization_id,
            resource_type=ScimResourceType.USER,
        )
        resources = [
            ScimUserResourceResponse.from_log(log, schema=_SCIM_USER_SCHEMA) for log in logs
        ]
        return ScimUserListResponse(totalResults=len(resources), resources=resources)

    async def provision_group(
        self,
        user: User,
        body: ScimGroupProvisionRequest,
        *,
        auth_mode: str = "staff",
    ) -> ScimGroupResourceResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        saved = await self._upsert_log(
            organization_id=organization_id,
            resource_type=ScimResourceType.GROUP,
            external_id=body.external_id,
            display_name=body.display_name,
            active=True,
            operation=ScimProvisionOperation.CREATE,
            auth_mode=auth_mode,
            provisioned_by_user_id=user.id,
        )
        return ScimGroupResourceResponse.from_log(saved, schema=_SCIM_GROUP_SCHEMA)

    async def list_groups(self, user: User) -> ScimGroupListResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        logs = await self._repo.list_provision_logs(
            organization_id,
            resource_type=ScimResourceType.GROUP,
        )
        resources = [
            ScimGroupResourceResponse.from_log(log, schema=_SCIM_GROUP_SCHEMA) for log in logs
        ]
        return ScimGroupListResponse(totalResults=len(resources), resources=resources)
