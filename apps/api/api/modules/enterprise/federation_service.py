"""IdP federation provider registry service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.idp_federation import get_idp_federation_status
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.enterprise.federation_models import (
    IdpFederationProvider,
    IdpFederationProviderType,
)
from api.modules.enterprise.federation_repository import IdpFederationRepository
from api.modules.enterprise.federation_schemas import (
    IdpFederationProviderListResponse,
    IdpFederationProviderRegisterRequest,
    IdpFederationProviderResponse,
    IdpFederationStatusResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class IdpFederationService:
    def __init__(
        self,
        repo: IdpFederationRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> IdpFederationService:
        return cls(IdpFederationRepository(session), session=session)

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
                detail="Insufficient permissions to view IdP federation",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage IdP federation",
            )

    async def get_status_response(self, user: User) -> IdpFederationStatusResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        status_payload = get_idp_federation_status()
        provider_count = await self._repo.count_providers(organization_id)
        return IdpFederationStatusResponse.from_status(
            status_payload,
            provider_count=provider_count,
        )

    async def list_providers(self, user: User) -> IdpFederationProviderListResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        providers = await self._repo.list_providers(organization_id)
        return IdpFederationProviderListResponse(
            total_results=len(providers),
            providers=[IdpFederationProviderResponse.from_model(item) for item in providers],
        )

    async def register_provider(
        self,
        user: User,
        body: IdpFederationProviderRegisterRequest,
    ) -> IdpFederationProviderResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        federation_status = get_idp_federation_status()
        if not federation_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "IdP federation is not ready",
                    "blockers": list(federation_status.blockers),
                },
            )

        if body.provider_type == IdpFederationProviderType.OIDC and not body.issuer_url:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="issuer_url is required for OIDC providers",
            )

        existing = await self._repo.get_by_key(organization_id, body.provider_key)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Provider key already registered for organization",
            )

        if body.is_primary:
            await self._repo.clear_primary(organization_id)

        provider = IdpFederationProvider(
            organization_id=organization_id,
            provider_key=body.provider_key,
            provider_type=body.provider_type,
            display_name=body.display_name,
            issuer_url=body.issuer_url,
            is_primary=body.is_primary,
            enabled=body.enabled,
            registered_by_user_id=user.id,
        )
        saved = await self._repo.save_provider(provider)
        if self._session is not None:
            await self._session.commit()
        return IdpFederationProviderResponse.from_model(saved)
