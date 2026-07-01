"""Readiness polling for eventually-consistent API state in E2E tests."""

from __future__ import annotations

import httpx

from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.wait_for_worker import poll_until


def wait_for_case_visible(
    http: httpx.Client,
    headers: dict[str, str],
    case_id: str,
    *,
    artifacts: ArtifactCollector | None = None,
    label: str = "case_visible",
) -> dict:
    """Poll until a freshly created case is readable by the API."""

    def fetch() -> httpx.Response:
        return http.get(f"/api/v1/cases/{case_id}", headers=headers)

    response = poll_until(
        fetch,
        lambda item: item.status_code == 200,
        description=f"case {case_id} visible",
        timeout=15.0,
        interval=0.25,
    )
    body = response.json()
    if artifacts is not None:
        artifacts.record(label, body)
    return body
