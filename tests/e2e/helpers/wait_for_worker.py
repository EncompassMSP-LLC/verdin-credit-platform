"""Polling helpers that wait for asynchronous worker results.

The document pipeline (OCR → classification → metadata → entity resolution)
runs in a separate worker process driven by a Redis queue. These helpers poll
the API until the expected state is reached or a timeout elapses, so the E2E
test never depends on fixed sleeps.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

DEFAULT_TIMEOUT_SECONDS = 90.0
DEFAULT_INTERVAL_SECONDS = 2.0


class WorkerTimeoutError(AssertionError):
    """Raised when the worker does not reach the expected state in time."""


def poll_until(
    fetch: Callable[[], T],
    predicate: Callable[[T], bool],
    *,
    description: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    interval: float = DEFAULT_INTERVAL_SECONDS,
) -> T:
    """Call ``fetch`` until ``predicate`` is satisfied or ``timeout`` elapses.

    Returns the last fetched value once the predicate holds. Raises
    ``WorkerTimeoutError`` with the last observed value otherwise.
    """
    deadline = time.monotonic() + timeout
    last_value: T | None = None
    attempts = 0
    while time.monotonic() < deadline:
        attempts += 1
        last_value = fetch()
        if predicate(last_value):
            return last_value
        time.sleep(interval)

    raise WorkerTimeoutError(
        f"Timed out after {timeout:.0f}s waiting for: {description} "
        f"(attempts={attempts}, last_value={last_value!r})"
    )
