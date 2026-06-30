"""Authentication helpers for the E2E suite."""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(slots=True)
class TokenBundle:
    access_token: str
    refresh_token: str
    token_type: str

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


def login(client: httpx.Client, email: str, password: str) -> TokenBundle:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    body = response.json()
    return TokenBundle(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        token_type=body.get("token_type", "bearer"),
    )


def refresh(client: httpx.Client, refresh_token: str) -> TokenBundle:
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    response.raise_for_status()
    body = response.json()
    return TokenBundle(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        token_type=body.get("token_type", "bearer"),
    )
