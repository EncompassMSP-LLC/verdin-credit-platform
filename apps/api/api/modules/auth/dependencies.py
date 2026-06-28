"""Role-based access control dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import TOKEN_TYPE_ACCESS, UserRole
from api.core.permissions import has_permission
from api.core.security import decode_token
from api.database.session import get_db
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.repositories.user import UserRepositoryProtocol

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != TOKEN_TYPE_ACCESS:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    repo: UserRepositoryProtocol = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active or user.is_deleted:
        raise credentials_exception

    return user


def require_role(minimum_role: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
