"""Security helpers — password hashing and JWT token management."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from api.core.config import get_settings
from api.core.constants import (
    TOKEN_REALM_PORTAL,
    TOKEN_REALM_STAFF,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    UserRole,
)

settings = get_settings()

# bcrypt only hashes the first 72 bytes of a password. Rather than silently
# truncating (which would let two distinct long passwords sharing a 72-byte
# prefix authenticate as one another), we reject over-length passwords at hash
# time. Callers should also validate length at the schema boundary so clients
# get a 422 instead of a 500.
MAX_PASSWORD_BYTES = 72


def password_within_bcrypt_limit(password: str) -> bool:
    return len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # A password longer than the bcrypt limit could never have been stored, so it
    # cannot match. Short-circuit to avoid bcrypt raising on over-length input
    # while remaining compatible with every existing stored hash.
    if not password_within_bcrypt_limit(plain_password):
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def hash_password(password: str) -> str:
    if not password_within_bcrypt_limit(password):
        raise ValueError(f"Password must not exceed {MAX_PASSWORD_BYTES} bytes when UTF-8 encoded")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: str,
    role: UserRole,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role.value,
        "type": TOKEN_TYPE_ACCESS,
        "realm": TOKEN_REALM_STAFF,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": TOKEN_TYPE_REFRESH,
        "realm": TOKEN_REALM_STAFF,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_portal_access_token(
    subject: str,
    *,
    organization_id: str,
    client_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "type": TOKEN_TYPE_ACCESS,
        "realm": TOKEN_REALM_PORTAL,
        "organization_id": organization_id,
        "client_id": client_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_portal_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": TOKEN_TYPE_REFRESH,
        "realm": TOKEN_REALM_PORTAL,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
