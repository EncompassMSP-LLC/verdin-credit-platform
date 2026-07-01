"""Redis-backed job enqueue for the API."""

from typing import Any

from verdin_job_orchestrator.constants import JobStatus, JobType
from verdin_job_orchestrator.queue import JobMessage, RedisJobQueue

from api.core.config import get_settings

_queue: RedisJobQueue | None = None


def _get_queue() -> RedisJobQueue:
    global _queue
    if _queue is None:
        settings = get_settings()
        _queue = RedisJobQueue(settings.redis_url, settings.worker_queue_name)
    return _queue


def enqueue_job(job_type: JobType, payload: dict[str, Any] | None = None) -> JobMessage:
    """Push a job onto the worker Redis queue."""
    return _get_queue().enqueue(job_type, payload)


__all__ = ["JobMessage", "JobStatus", "JobType", "enqueue_job"]
