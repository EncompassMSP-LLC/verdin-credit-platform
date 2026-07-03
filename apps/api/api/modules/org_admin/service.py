"""Organization admin service — API keys and org summary."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import generate_api_key_material
from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.org_admin import get_org_admin_status
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.billing.service import BillingService
from api.modules.org_admin.models import OrganizationApiKey
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE
from api.modules.org_admin.repository import OrgAdminRepository
from api.modules.org_admin.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    OrgAdminStatusResponse,
    OrganizationAdminSummary,
)


class OrgAdminService:
    def __init__(
        self,
        repo: OrgAdminRepository,
        session: AsyncSession | None = None,
        billing_service: BillingService | None = None,
    ) -> None:
        self._repo = repo
        self._session = session
        self._billing = billing_service

    @classmethod
    def from_session(cls, session: AsyncSession) -> "OrgAdminService":
        return cls(
            OrgAdminRepository(session),
            session=session,
            billing_service=BillingService.from_session(session),
        )

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
                detail="Insufficient permissions to view organization admin",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage organization admin",
            )

    async def get_status(self, user: User) -> OrgAdminStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return get_org_admin_status()

    async def get_organization_summary(self, user: User) -> OrganizationAdminSummary:
        self._require_read(user)
        organization_id = self._require_organization(user)
        organization = await self._repo.get_organization(organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        active_users = await self._repo.count_active_users(organization_id)
        active_api_keys = await self._repo.count_active_api_keys(organization_id)
        billing = None
        if self._billing is not None:
            billing = await self._billing.get_organization_billing_summary(organization_id)
        return OrganizationAdminSummary(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            is_active=organization.is_active,
            active_user_count=active_users,
            active_api_key_count=active_api_keys,
            billing=billing,
        )

    async def list_api_keys(self, user: User) -> list[ApiKeyResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        keys = await self._repo.list_api_keys(organization_id)
        return [ApiKeyResponse.from_model(api_key) for api_key in keys]

    async def get_api_key(self, user: User, api_key_id: uuid.UUID) -> ApiKeyResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        api_key = await self._repo.get_api_key(api_key_id, organization_id=organization_id)
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        return ApiKeyResponse.from_model(api_key)

    async def create_api_key(self, user: User, data: ApiKeyCreate) -> ApiKeyCreateResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        if not data.scopes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one scope is required",
            )

        full_key, key_prefix, key_hash = generate_api_key_material()
        api_key = OrganizationApiKey(
            organization_id=organization_id,
            name=data.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            is_active=True,
            expires_at=data.expires_at,
        )
        api_key.set_scopes(data.scopes)
        apply_audit_on_create(api_key, user.id)
        api_key = await self._repo.create_api_key(api_key)
        if self._session is not None:
            await self._session.commit()

        response = ApiKeyResponse.from_model(api_key)
        return ApiKeyCreateResponse(**response.model_dump(), api_key=full_key)

    async def revoke_api_key(self, user: User, api_key_id: uuid.UUID) -> ApiKeyResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        api_key = await self._repo.get_api_key(api_key_id, organization_id=organization_id)
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        if api_key.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key has already been revoked",
            )

        api_key.is_active = False
        api_key.revoked_at = datetime.now(UTC)
        apply_audit_on_update(api_key, user.id)
        api_key = await self._repo.save_api_key(api_key)
        if self._session is not None:
            await self._session.commit()
        return ApiKeyResponse.from_model(api_key)
