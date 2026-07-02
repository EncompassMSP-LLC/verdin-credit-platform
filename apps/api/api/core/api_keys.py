"""API key generation and verification helpers."""

import hashlib
import secrets

API_KEY_PREFIX = "vrd_live_"


def generate_api_key_material() -> tuple[str, str, str]:
    """Return ``(full_key, key_prefix, key_hash)`` for persistence."""
    secret = secrets.token_urlsafe(32)
    full_key = f"{API_KEY_PREFIX}{secret}"
    key_prefix = full_key[:16]
    key_hash = hash_api_key(full_key)
    return full_key, key_prefix, key_hash


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def verify_api_key(api_key: str, key_hash: str) -> bool:
    return hash_api_key(api_key) == key_hash
