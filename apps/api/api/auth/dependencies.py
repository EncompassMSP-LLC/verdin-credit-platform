"""Role-based access control."""

from enum import IntEnum

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.security import decode_token
from api.database.session import get_db
from api.models import User, UserRole
from api.repositories.user_repository import UserRepository

security = HTTPBearer()


class RoleLevel(IntEnum):
    READ_ONLY = 1
    REVIEWER = 2
    CASE_MANAGER = 3
    ADMIN = 4
    OWNER = 5


ROLE_LEVELS: dict[UserRole, RoleLevel] = {
    UserRole.READ_ONLY: RoleLevel.READ_ONLY,
    UserRole.REVIEWER: RoleLevel.REVIEWER,
    UserRole.CASE_MANAGER: RoleLevel.CASE_MANAGER,
    UserRole.ADMIN: RoleLevel.ADMIN,
    UserRole.OWNER: RoleLevel.OWNER,
}


def has_permission(user_role: UserRole, required_role: UserRole) -> bool:
    return ROLE_LEVELS[user_role] >= ROLE_LEVELS[required_role]


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
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    repo = UserRepository(db)
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
