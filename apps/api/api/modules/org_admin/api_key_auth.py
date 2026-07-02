"""API key authentication for machine clients."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import API_KEY_PREFIX, verify_api_key
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.org_admin.models import ApiKeyScope, OrganizationApiKey
from api.modules.org_admin.repository import OrgAdminRepository


@dataclass(frozen=True, slots=True)
class ApiKeyAuthContext:
    organization_id: uuid.UUID
    api_key_id: uuid.UUID
    scopes: list[ApiKeyScope]


class ApiKeyAuthService:
    def __init__(self, repo: OrgAdminRepository, session: AsyncSession | None = None) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ApiKeyAuthService":
        return cls(OrgAdminRepository(session), session=session)

    def _require_enabled(self) -> None:
        if not is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key authentication is not enabled",
            )

    async def authenticate(
        self,
        raw_key: str,
        *,
        required_scope: ApiKeyScope,
    ) -> ApiKeyAuthContext:
        self._require_enabled()

        if not raw_key.startswith(API_KEY_PREFIX):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        key_prefix = raw_key[:16]
        candidates = await self._repo.list_active_api_keys_by_prefix(key_prefix)
        matched: OrganizationApiKey | None = None
        for candidate in candidates:
            if verify_api_key(raw_key, candidate.key_hash):
                matched = candidate
                break

        if matched is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        if matched.revoked_at is not None or not matched.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is revoked",
            )

        if matched.expires_at is not None and matched.expires_at <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

        scopes = matched.scope_values
        if required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key missing required scope: {required_scope.value}",
            )

        await self._repo.touch_api_key_last_used(matched.id)
        if self._session is not None:
            await self._session.commit()

        return ApiKeyAuthContext(
            organization_id=matched.organization_id,
            api_key_id=matched.id,
            scopes=scopes,
        )
