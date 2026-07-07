"""Organization admin service — API keys and org summary."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_developer_portal import get_api_developer_portal_status
from api.core.api_key_rate_limit import get_api_key_rate_limit_status
from api.core.api_keys import generate_api_key_material
from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.org_admin import get_org_admin_status
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.billing.service import BillingService
from api.modules.org_admin.models import OAuthDeveloperAppStatus, OrganizationApiKey
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE
from api.modules.org_admin.repository import OrgAdminRepository
from api.modules.org_admin.rotation_repository import ApiKeyRotationRepository
from api.modules.org_admin.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyRateLimitStatusResponse,
    ApiKeyResponse,
    ApiKeyRotateResponse,
    DeveloperPortalResponse,
    OAuthDeveloperAppCreate,
    OAuthDeveloperAppResponse,
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
        self._rotations = ApiKeyRotationRepository(session) if session is not None else None

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

    async def get_api_key_rate_limit_status(self, user: User) -> ApiKeyRateLimitStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        status_payload = get_api_key_rate_limit_status()
        return ApiKeyRateLimitStatusResponse(
            enabled=status_payload.enabled,
            limit_per_minute=status_payload.limit_per_minute,
            backend=status_payload.backend,
        )

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

    async def rotate_api_key(self, user: User, api_key_id: uuid.UUID) -> ApiKeyRotateResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        if self._rotations is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key rotation repository is not configured",
            )

        api_key = await self._repo.get_api_key(api_key_id, organization_id=organization_id)
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        if api_key.revoked_at is not None or not api_key.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active API keys can be rotated",
            )

        rotated_at = datetime.now(UTC)

        api_key.is_active = False
        api_key.revoked_at = rotated_at
        apply_audit_on_update(api_key, user.id)
        await self._repo.save_api_key(api_key)
        previous_key = ApiKeyResponse.from_model(api_key)

        full_key, key_prefix, key_hash = generate_api_key_material()
        replacement = OrganizationApiKey(
            organization_id=organization_id,
            name=api_key.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            is_active=True,
            expires_at=api_key.expires_at,
        )
        replacement.set_scopes(api_key.scope_values)
        apply_audit_on_create(replacement, user.id)
        replacement = await self._repo.create_api_key(replacement)

        await self._rotations.create_rotation_log(
            organization_id=organization_id,
            previous_api_key_id=api_key.id,
            new_api_key_id=replacement.id,
            rotated_by_user_id=user.id,
            rotated_at=rotated_at,
        )
        if self._session is not None:
            await self._session.commit()

        new_key = ApiKeyResponse.from_model(replacement)
        return ApiKeyRotateResponse(
            api_key=full_key,
            previous_key=previous_key,
            new_key=new_key,
        )

    async def get_developer_portal(self, user: User) -> DeveloperPortalResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        portal_status = get_api_developer_portal_status()
        rate_limit = await self.get_api_key_rate_limit_status(user)
        keys = await self.list_api_keys(user)
        active_count = await self._repo.count_active_api_keys(organization_id)
        return DeveloperPortalResponse(
            enabled=portal_status.enabled,
            ready=portal_status.ready,
            rotation_enabled=portal_status.rotation_enabled,
            blockers=list(portal_status.blockers),
            active_api_key_count=active_count,
            rate_limit=rate_limit,
            api_keys=keys,
        )

    async def list_oauth_developer_apps(self, user: User) -> list[OAuthDeveloperAppResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        apps = await self._repo.list_oauth_developer_apps(organization_id)
        return [OAuthDeveloperAppResponse.from_model(app) for app in apps]

    async def create_oauth_developer_app(
        self, user: User, data: OAuthDeveloperAppCreate
    ) -> OAuthDeveloperAppResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        requested_at = datetime.now(UTC)
        app = await self._repo.create_oauth_developer_app(
            organization_id=organization_id,
            name=data.name,
            redirect_uri=data.redirect_uri,
            scopes=data.scopes,
            requested_by_user_id=user.id,
            requested_at=requested_at,
        )
        if self._session is not None:
            await self._session.commit()
        return OAuthDeveloperAppResponse.from_model(app)

    async def approve_oauth_developer_app(
        self, user: User, app_id: uuid.UUID
    ) -> OAuthDeveloperAppResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        app = await self._repo.get_oauth_developer_app(app_id, organization_id=organization_id)
        if app is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OAuth app not found")
        if app.status.value != "pending_approval":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="OAuth app is not pending approval",
            )

        app.status = OAuthDeveloperAppStatus.APPROVED
        app.approved_by_user_id = user.id
        app.approved_at = datetime.now(UTC)
        app = await self._repo.save_oauth_developer_app(app)
        if self._session is not None:
            await self._session.commit()
        return OAuthDeveloperAppResponse.from_model(app)
