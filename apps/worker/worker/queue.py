"""Redis-backed job queue primitives."""

from typing import Any

from verdin_job_orchestrator.constants import JobType
from verdin_job_orchestrator.queue import JobMessage, RedisJobQueue

from worker.config import get_worker_settings

_queue: RedisJobQueue | None = None


def _get_queue() -> RedisJobQueue:
    global _queue
    if _queue is None:
        settings = get_worker_settings()
        _queue = RedisJobQueue(
            settings.redis_url,
            settings.worker_queue_name,
            poll_interval_seconds=settings.worker_poll_interval_seconds,
        )
    return _queue


def enqueue_job(job_type: JobType, payload: dict[str, Any] | None = None) -> JobMessage:
    """Push a job onto the Redis queue."""
    return _get_queue().enqueue(job_type, payload)


def dequeue_job(timeout_seconds: int | None = None) -> JobMessage | None:
    """Block until a job is available or the timeout elapses."""
    return _get_queue().dequeue(timeout_seconds)


__all__ = ["JobMessage", "dequeue_job", "enqueue_job"]
