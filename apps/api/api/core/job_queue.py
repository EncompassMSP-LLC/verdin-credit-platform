"""Redis-backed job enqueue for the API."""

import uuid
from enum import StrEnum
from typing import Any

import redis
from pydantic import BaseModel, Field

from api.core.config import get_settings


class JobType(StrEnum):
    OCR = "ocr"
    DOCUMENT_CLASSIFY = "document_classify"
    REPORT_IMPORT = "report_import"
    AI_SUMMARY = "ai_summary"
    MONTHLY_REVIEW = "monthly_review"


class JobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobMessage(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED


def _get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_job(job_type: JobType, payload: dict[str, Any] | None = None) -> JobMessage:
    """Push a job onto the worker Redis queue."""
    settings = get_settings()
    message = JobMessage(job_type=job_type, payload=payload or {})
    client = _get_redis_client()
    client.lpush(settings.worker_queue_name, message.model_dump_json())
    return message
