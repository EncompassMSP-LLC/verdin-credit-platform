"""Retry policy helpers for background jobs."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0


def compute_backoff_seconds(attempt: int, policy: RetryPolicy) -> float:
    """Exponential backoff capped at ``max_delay_seconds`` (attempt is 1-based)."""
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    delay = policy.base_delay_seconds * (2 ** (attempt - 1))
    return min(delay, policy.max_delay_seconds)


def should_retry(attempt: int, policy: RetryPolicy) -> bool:
    """Return True when another attempt is allowed after ``attempt`` failures."""
    return attempt < policy.max_attempts
