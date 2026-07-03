"""TOTP enrollment helpers for enterprise MFA."""

from __future__ import annotations

import base64
import hashlib

import pyotp
from cryptography.fernet import Fernet, InvalidToken

from api.core.config import get_settings


def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def generate_totp_secret() -> str:
    return str(pyotp.random_base32())


def build_totp_provisioning_uri(*, secret: str, account_name: str, issuer: str) -> str:
    return str(
        pyotp.totp.TOTP(secret).provisioning_uri(name=account_name, issuer_name=issuer),
    )


def verify_totp_code(*, secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=1))


def encrypt_totp_secret(secret: str) -> str:
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_totp_secret(encrypted: str) -> str:
    try:
        return _fernet().decrypt(encrypted.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted TOTP secret") from exc
