"""Unit tests for password hashing helpers."""

import bcrypt
import pytest

from api.core.security import (
    MAX_PASSWORD_BYTES,
    hash_password,
    password_within_bcrypt_limit,
    verify_password,
)


def test_hash_and_verify_round_trip() -> None:
    hashed = hash_password("correct horse battery")
    assert verify_password("correct horse battery", hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_hash_rejects_password_over_72_bytes() -> None:
    with pytest.raises(ValueError, match="72 bytes"):
        hash_password("a" * (MAX_PASSWORD_BYTES + 1))


def test_verify_rejects_password_over_72_bytes_without_raising() -> None:
    # Two distinct over-length passwords sharing a 72-byte prefix must not be
    # accepted, and verification must never raise on over-length input.
    hashed = hash_password("a" * MAX_PASSWORD_BYTES)
    assert verify_password("a" * (MAX_PASSWORD_BYTES + 10), hashed) is False


def test_max_length_password_is_allowed() -> None:
    password = "a" * MAX_PASSWORD_BYTES
    assert password_within_bcrypt_limit(password) is True
    assert verify_password(password, hash_password(password)) is True


def test_multibyte_password_counts_bytes_not_characters() -> None:
    # Each "é" is 2 bytes in UTF-8, so 36 of them is exactly the 72-byte limit.
    assert password_within_bcrypt_limit("é" * 36) is True
    assert password_within_bcrypt_limit("é" * 37) is False


def test_verify_supports_existing_stored_bcrypt_hashes() -> None:
    # Hashes created directly by bcrypt (as stored by earlier releases / seed
    # data) must continue to verify.
    legacy = bcrypt.hashpw(b"changeme123", bcrypt.gensalt(rounds=12)).decode("utf-8")
    assert verify_password("changeme123", legacy) is True
    assert verify_password("changeme124", legacy) is False
