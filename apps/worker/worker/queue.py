"""Redis-backed job queue primitives."""

import json
import uuid
from typing import Any

import redis
from pydantic import BaseModel, Field

from worker.config import get_worker_settings
from worker.constants import JobStatus, JobType


class JobMessage(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED


def get_redis_client() -> redis.Redis:
    settings = get_worker_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_job(job_type: JobType, payload: dict[str, Any] | None = None) -> JobMessage:
    """Push a job onto the Redis queue. Used by the API in Sprint 2."""
    settings = get_worker_settings()
    message = JobMessage(job_type=job_type, payload=payload or {})
    client = get_redis_client()
    client.lpush(settings.worker_queue_name, message.model_dump_json())
    return message


def dequeue_job(timeout_seconds: int | None = None) -> JobMessage | None:
    """Block until a job is available or the timeout elapses."""
    settings = get_worker_settings()
    client = get_redis_client()
    timeout = (
        settings.worker_poll_interval_seconds
        if timeout_seconds is None
        else timeout_seconds
    )
    result = client.brpop(settings.worker_queue_name, timeout=timeout)
    if result is None:
        return None

    _, raw_payload = result
    data = json.loads(raw_payload)
    return JobMessage.model_validate(data)
