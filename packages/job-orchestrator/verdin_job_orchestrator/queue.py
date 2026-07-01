"""Redis-backed job queue primitives."""

import json
import uuid
from typing import Any

import redis
from pydantic import BaseModel, Field

from verdin_job_orchestrator.constants import JobStatus, JobType


class JobMessage(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED


class RedisJobQueue:
    """Redis list queue using LPUSH / BRPOP."""

    def __init__(self, redis_url: str, queue_name: str, *, poll_interval_seconds: int = 5) -> None:
        self._redis_url = redis_url
        self._queue_name = queue_name
        self._poll_interval_seconds = poll_interval_seconds
        self._client: redis.Redis | None = None

    @property
    def queue_name(self) -> str:
        return self._queue_name

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    def enqueue(self, job_type: JobType, payload: dict[str, Any] | None = None) -> JobMessage:
        message = JobMessage(job_type=job_type, payload=payload or {})
        self._get_client().lpush(self._queue_name, message.model_dump_json())
        return message

    def dequeue(self, timeout_seconds: int | None = None) -> JobMessage | None:
        timeout = self._poll_interval_seconds if timeout_seconds is None else timeout_seconds
        result = self._get_client().brpop(self._queue_name, timeout=timeout)
        if result is None:
            return None

        _, raw_payload = result
        data = json.loads(raw_payload)
        return JobMessage.model_validate(data)
