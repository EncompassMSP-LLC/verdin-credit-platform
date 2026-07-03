"""Client portal dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import TOKEN_REALM_PORTAL, TOKEN_TYPE_ACCESS
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.security import decode_token
from api.database.session import get_db
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.repository import ClientPortalUserRepository

portal_security = HTTPBearer()


def require_client_portal_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client portal is not enabled",
        )


def require_portal_push_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_PORTAL_PUSH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal push is not enabled",
        )


async def get_current_portal_user(
    credentials: HTTPAuthorizationCredentials = Depends(portal_security),
    db: AsyncSession = Depends(get_db),
) -> ClientPortalUser:
    require_client_portal_enabled()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != TOKEN_TYPE_ACCESS:
        raise credentials_exception

    if payload.get("realm") != TOKEN_REALM_PORTAL:
        raise credentials_exception

    portal_user_id = payload.get("sub")
    if portal_user_id is None:
        raise credentials_exception

    repo = ClientPortalUserRepository(db)
    portal_user = await repo.get_by_id(portal_user_id)
    if portal_user is None or not portal_user.is_active or portal_user.is_deleted:
        raise credentials_exception

    return portal_user
