"""Worker orchestration helpers — retry, metrics, and scheduler ticks."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import structlog
from verdin_job_orchestrator import (
    InMemoryJobMetricsRecorder,
    JobMetricsRecorder,
    JobScheduler,
    JobType,
    NullJobMetricsRecorder,
    RetryPolicy,
    ScheduledJob,
    compute_backoff_seconds,
    should_retry,
)

from worker.base import JobContext
from worker.constants import JobStatus, JobType as WorkerJobType
from worker.registry import get_job

logger = structlog.get_logger(__name__)

ATTEMPT_PAYLOAD_KEY = "_attempt"
DEFAULT_OVERDUE_SCAN_CRON = "0 6 * * *"
DEFAULT_RETENTION_ENFORCEMENT_CRON = "0 3 * * *"
DEFAULT_REPORTING_MV_REFRESH_CRON = "0 4 * * *"

EnqueueFn = Callable[[WorkerJobType, dict[str, Any]], object]


def build_default_scheduler() -> JobScheduler:
    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression=DEFAULT_OVERDUE_SCAN_CRON,
        ),
    )
    scheduler.register(
        ScheduledJob(
            job_type=JobType.RETENTION_ENFORCEMENT_SCAN,
            cron_expression=DEFAULT_RETENTION_ENFORCEMENT_CRON,
        ),
    )
    scheduler.register(
        ScheduledJob(
            job_type=JobType.REPORTING_MV_REFRESH,
            cron_expression=DEFAULT_REPORTING_MV_REFRESH_CRON,
        ),
    )
    return scheduler


def tick_scheduler(
    scheduler: JobScheduler,
    enqueue_fn: EnqueueFn,
    *,
    at: Any | None = None,
    metrics: JobMetricsRecorder | None = None,
) -> list[JobType]:
    """Enqueue scheduled jobs that are due at ``at`` (defaults to now)."""
    from datetime import datetime

    metrics_recorder = metrics or NullJobMetricsRecorder()
    due_jobs = scheduler.jobs_due_at(at if isinstance(at, datetime) else None)
    enqueued: list[JobType] = []

    for scheduled in due_jobs:
        payload = scheduled.payload_factory()
        enqueue_fn(WorkerJobType(scheduled.job_type.value), payload)
        scheduler.mark_triggered(
            scheduled.job_type, at if isinstance(at, datetime) else None
        )
        metrics_recorder.record_enqueued(scheduled.job_type)
        enqueued.append(scheduled.job_type)
        logger.info(
            "scheduled_job_enqueued",
            job_type=scheduled.job_type.value,
            cron_expression=scheduled.cron_expression,
        )

    return enqueued


def dispatch_job(
    job_id: str,
    job_type_value: str,
    payload: dict[str, Any],
    *,
    retry_policy: RetryPolicy | None = None,
    metrics: JobMetricsRecorder | None = None,
    enqueue_fn: EnqueueFn | None = None,
) -> None:
    policy = retry_policy or RetryPolicy()
    metrics_recorder = metrics or NullJobMetricsRecorder()
    attempt = int(payload.get(ATTEMPT_PAYLOAD_KEY, 1))

    job_type = WorkerJobType(job_type_value)
    orchestrator_job_type = JobType(job_type.value)
    job = get_job(job_type)
    context = JobContext(job_id=job_id, payload=payload)

    metrics_recorder.record_started(orchestrator_job_type)
    started = time.monotonic()

    logger.info(
        "job_started",
        job_id=job_id,
        job_type=job_type.value,
        attempt=attempt,
    )

    try:
        result = job.run(context)
    except Exception as exc:
        duration = time.monotonic() - started
        metrics_recorder.record_failed(orchestrator_job_type)
        logger.exception(
            "job_failed",
            job_id=job_id,
            job_type=job_type.value,
            attempt=attempt,
            duration_seconds=duration,
            error=str(exc),
        )
        _maybe_retry_job(
            job_type=job_type,
            orchestrator_job_type=orchestrator_job_type,
            payload=payload,
            attempt=attempt,
            policy=policy,
            enqueue_fn=enqueue_fn,
            reason=str(exc),
        )
        return

    duration = time.monotonic() - started
    if result.status is JobStatus.FAILED:
        metrics_recorder.record_failed(orchestrator_job_type)
        logger.warning(
            "job_failed",
            job_id=job_id,
            job_type=job_type.value,
            attempt=attempt,
            duration_seconds=duration,
            message=result.message,
        )
        _maybe_retry_job(
            job_type=job_type,
            orchestrator_job_type=orchestrator_job_type,
            payload=payload,
            attempt=attempt,
            policy=policy,
            enqueue_fn=enqueue_fn,
            reason=result.message,
        )
        return

    metrics_recorder.record_completed(orchestrator_job_type, duration)
    logger.info(
        "job_finished",
        job_id=job_id,
        job_type=job_type.value,
        attempt=attempt,
        duration_seconds=duration,
        status=result.status.value,
        message=result.message,
    )


def _maybe_retry_job(
    *,
    job_type: WorkerJobType,
    orchestrator_job_type: JobType,
    payload: dict[str, Any],
    attempt: int,
    policy: RetryPolicy,
    enqueue_fn: EnqueueFn | None,
    reason: str,
) -> None:
    if enqueue_fn is None or not should_retry(attempt, policy):
        return

    delay = compute_backoff_seconds(attempt, policy)
    time.sleep(delay)
    retry_payload = {**payload, ATTEMPT_PAYLOAD_KEY: attempt + 1}
    enqueue_fn(job_type, retry_payload)
    logger.info(
        "job_retry_enqueued",
        job_type=job_type.value,
        orchestrator_job_type=orchestrator_job_type.value,
        next_attempt=attempt + 1,
        delay_seconds=delay,
        reason=reason,
    )


__all__ = [
    "ATTEMPT_PAYLOAD_KEY",
    "DEFAULT_OVERDUE_SCAN_CRON",
    "InMemoryJobMetricsRecorder",
    "build_default_scheduler",
    "dispatch_job",
    "tick_scheduler",
]
