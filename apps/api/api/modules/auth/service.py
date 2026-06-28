"""Authentication service — business logic for auth flows."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import TOKEN_TYPE_REFRESH
from api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.modules.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from api.repositories.user import UserRepositoryProtocol


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        user_repo: UserRepositoryProtocol | None = None,
    ) -> None:
        self._repo: UserRepositoryProtocol = (
            user_repo if user_repo is not None else UserRepository(session)
        )

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(credentials.email)
        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        user = await self._repo.get_by_id(payload["sub"])
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def get_current_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def register(self, data: UserCreate) -> UserResponse:
        existing = await self._repo.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            organization_id=data.organization_id,
        )
        created = await self._repo.create(user)
        return UserResponse.model_validate(created)
