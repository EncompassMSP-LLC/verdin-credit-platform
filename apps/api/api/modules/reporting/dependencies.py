"""Reporting route authentication dependencies."""

import uuid

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import API_KEY_PREFIX
from api.core.permissions import has_permission
from api.database.session import get_db
from api.modules.auth.dependencies import authenticate_staff_user, optional_bearer
from api.modules.org_admin.api_key_auth import ApiKeyAuthService
from api.modules.org_admin.models import ApiKeyScope
from api.modules.reporting.permissions import REPORTING_READ_ROLE


def _extract_api_key(
    credentials: HTTPAuthorizationCredentials | None,
    x_api_key: str | None,
) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if credentials is not None and credentials.credentials.startswith(API_KEY_PREFIX):
        return credentials.credentials
    return None


async def get_reporting_organization_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> uuid.UUID:
    """Resolve organization scope from staff JWT or organization API key."""
    raw_key = _extract_api_key(credentials, x_api_key)
    if raw_key is not None:
        auth = await ApiKeyAuthService.from_session(db).authenticate(
            raw_key,
            required_scope=ApiKeyScope.READ,
        )
        return auth.organization_id

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await authenticate_staff_user(credentials, db)
    if user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization",
        )
    if not has_permission(user.role, REPORTING_READ_ROLE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view reporting",
        )
    return user.organization_id
