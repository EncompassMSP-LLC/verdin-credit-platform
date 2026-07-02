"""Client portal auth and provisioning services."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.constants import TOKEN_REALM_PORTAL, TOKEN_TYPE_REFRESH
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.permissions import has_permission
from api.core.security import (
    create_portal_access_token,
    create_portal_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.modules.auth.models import User
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.repository import ClientPortalUserRepository
from api.modules.client_portal.schemas import (
    ClientPortalUserProvision,
    ClientPortalUserResponse,
    ClientPortalUserUpdate,
    PortalLoginRequest,
    PortalMeResponse,
    PortalTokenResponse,
)
from api.modules.clients.models import Client
from api.modules.clients.permissions import CLIENT_WRITE_ROLE
from api.modules.clients.repository import ClientRepository


class ClientPortalAuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._portal_users = ClientPortalUserRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientPortalAuthService":
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    async def login(self, credentials: PortalLoginRequest) -> PortalTokenResponse:
        self._require_enabled()
        portal_user = await self._portal_users.get_by_email(credentials.email)
        if portal_user is None or not verify_password(
            credentials.password,
            portal_user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        portal_user.last_login_at = datetime.now(UTC)
        await self._portal_users.save(portal_user)
        await self._session.commit()

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def refresh(self, refresh_token: str) -> PortalTokenResponse:
        self._require_enabled()
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        if payload.get("realm") != TOKEN_REALM_PORTAL:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        portal_user = await self._portal_users.get_by_id(payload["sub"])
        if portal_user is None or not portal_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client record is unavailable",
            )

        return PortalTokenResponse(
            access_token=create_portal_access_token(
                str(portal_user.id),
                organization_id=str(portal_user.organization_id),
                client_id=str(portal_user.client_id),
            ),
            refresh_token=create_portal_refresh_token(str(portal_user.id)),
        )

    async def get_me(self, portal_user: ClientPortalUser) -> PortalMeResponse:
        client = await self._clients.get_by_id(
            portal_user.client_id,
            organization_id=portal_user.organization_id,
        )
        if client is None or client.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return PortalMeResponse(
            id=portal_user.id,
            organization_id=portal_user.organization_id,
            client_id=portal_user.client_id,
            email=portal_user.email,
            client_display_name=client.display_name,
            is_active=portal_user.is_active,
            last_login_at=portal_user.last_login_at,
        )


class ClientPortalProvisioningService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._portal_users = ClientPortalUserRepository(session)
        self._clients = ClientRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ClientPortalProvisioningService":
        return cls(session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client portal is not enabled",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CLIENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage client portal access",
            )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    async def _get_client_for_user(self, client_id: uuid.UUID, user: User) -> Client:
        organization_id = self._require_organization(user)
        client = await self._clients.get_by_id(client_id, organization_id=organization_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    async def provision_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientPortalUserProvision,
    ) -> ClientPortalUserResponse:
        self._require_enabled()
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)

        existing_for_client = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if existing_for_client is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portal access already exists for this client",
            )

        existing_email = await self._portal_users.get_by_email(data.email)
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered for portal access",
            )

        portal_user = ClientPortalUser(
            organization_id=client.organization_id,
            client_id=client.id,
            email=str(data.email),
            hashed_password=hash_password(data.password),
            is_active=True,
        )
        apply_audit_on_create(portal_user, user.id)
        await self._portal_users.add(portal_user)
        await self._session.commit()
        await self._session.refresh(portal_user)
        return ClientPortalUserResponse.from_model(portal_user)

    async def get_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
    ) -> ClientPortalUserResponse:
        self._require_enabled()
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )
        return ClientPortalUserResponse.from_model(portal_user)

    async def update_portal_user(
        self,
        user: User,
        client_id: uuid.UUID,
        data: ClientPortalUserUpdate,
    ) -> ClientPortalUserResponse:
        self._require_enabled()
        self._require_write(user)
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )

        updates = data.model_dump(exclude_unset=True)
        if "email" in updates and updates["email"] is not None:
            email = str(updates["email"])
            existing = await self._portal_users.get_by_email(email)
            if existing is not None and existing.id != portal_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered for portal access",
                )
            updates["email"] = email
        if "password" in updates and updates["password"] is not None:
            updates["hashed_password"] = hash_password(updates.pop("password"))

        for key, value in updates.items():
            setattr(portal_user, key, value)
        apply_audit_on_update(portal_user, user.id)
        await self._portal_users.save(portal_user)
        await self._session.commit()
        await self._session.refresh(portal_user)
        return ClientPortalUserResponse.from_model(portal_user)

    async def revoke_portal_user(self, user: User, client_id: uuid.UUID) -> None:
        self._require_write(user)
        self._require_enabled()
        client = await self._get_client_for_user(client_id, user)
        portal_user = await self._portal_users.get_by_client_id(
            client.id,
            organization_id=client.organization_id,
        )
        if portal_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal access not provisioned for this client",
            )
        portal_user.soft_delete()
        apply_audit_on_update(portal_user, user.id)
        await self._portal_users.save(portal_user)
        await self._session.commit()
