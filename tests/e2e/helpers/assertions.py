"""Assertion helpers that attach response context to failures and artifacts."""

from __future__ import annotations

import httpx

from tests.e2e.helpers.artifacts import ArtifactCollector


def expect_ok(
    response: httpx.Response,
    *,
    label: str,
    artifacts: ArtifactCollector,
    expected_status: int = 200,
) -> dict:
    """Assert an expected status code, recording the exchange as an artifact.

    Returns the parsed JSON body on success.
    """
    body: object
    try:
        body = response.json()
    except ValueError:
        body = response.text

    artifacts.record(
        label,
        {
            "method": response.request.method,
            "url": str(response.request.url),
            "status_code": response.status_code,
            "body": body,
        },
    )

    assert response.status_code == expected_status, (
        f"{label}: expected {expected_status}, got {response.status_code}. Body: {body!r}"
    )
    return body if isinstance(body, dict) else {}
