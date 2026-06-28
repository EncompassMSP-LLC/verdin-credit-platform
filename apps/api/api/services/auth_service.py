"""Authentication service — business logic for auth flows."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.models import User
from api.repositories.user_repository import UserRepository
from api.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

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
        if payload is None or payload.get("type") != "refresh":
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
