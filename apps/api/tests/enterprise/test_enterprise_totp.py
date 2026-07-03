"""Enterprise TOTP helper unit tests."""

import pyotp

from api.core.enterprise_totp import (
    build_totp_provisioning_uri,
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_totp_secret,
    verify_totp_code,
)


def test_totp_encrypt_decrypt_roundtrip() -> None:
    secret = generate_totp_secret()
    encrypted = encrypt_totp_secret(secret)
    assert decrypt_totp_secret(encrypted) == secret


def test_verify_totp_code_accepts_current_token() -> None:
    secret = generate_totp_secret()
    code = pyotp.TOTP(secret).now()
    assert verify_totp_code(secret=secret, code=code) is True


def test_build_totp_provisioning_uri() -> None:
    secret = generate_totp_secret()
    uri = build_totp_provisioning_uri(
        secret=secret,
        account_name="user@example.com",
        issuer="Verdin",
    )
    assert uri.startswith("otpauth://totp/")
