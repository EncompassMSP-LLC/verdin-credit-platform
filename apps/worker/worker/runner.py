"""Worker process loop: dequeue jobs and dispatch via the registry."""

import signal
import sys
import time
from datetime import UTC, datetime
from typing import Any

import structlog
from verdin_job_orchestrator import NullJobMetricsRecorder, RetryPolicy

from worker import jobs  # noqa: F401 — register placeholder jobs
from worker.config import get_worker_settings
from worker.orchestrator import build_default_scheduler, dispatch_job, tick_scheduler
from worker.queue import dequeue_job, enqueue_job

logger = structlog.get_logger(__name__)

_running = True


def handle_shutdown(signum: int, _frame: object) -> None:
    global _running
    logger.info("shutdown_signal_received", signal=signum)
    _running = False


def run_worker() -> None:
    settings = get_worker_settings()
    scheduler = build_default_scheduler()
    retry_policy = RetryPolicy()
    metrics = NullJobMetricsRecorder()

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
    )

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    from worker.registry import list_job_types

    registered = [job_type.value for job_type in list_job_types()]
    scheduled = [
        {"job_type": job.job_type.value, "cron": job.cron_expression}
        for job in scheduler.list_scheduled()
    ]
    logger.info(
        "worker_started",
        version=settings.app_version,
        queue=settings.worker_queue_name,
        registered_jobs=registered,
        scheduled_jobs=scheduled,
        scheduler_interval_seconds=settings.worker_scheduler_interval_seconds,
    )

    last_heartbeat = 0.0
    last_scheduler_tick = 0.0

    def _dispatch(job_id: str, job_type_value: str, payload: dict[str, Any]) -> None:
        dispatch_job(
            job_id,
            job_type_value,
            payload,
            retry_policy=retry_policy,
            metrics=metrics,
            enqueue_fn=enqueue_job,
        )

    while _running:
        message = dequeue_job()
        if message is not None:
            _dispatch(message.job_id, message.job_type.value, message.payload)
            continue

        now = time.monotonic()
        if now - last_scheduler_tick >= settings.worker_scheduler_interval_seconds:
            tick_scheduler(
                scheduler, enqueue_job, at=datetime.now(tz=UTC), metrics=metrics
            )
            last_scheduler_tick = now

        if now - last_heartbeat >= settings.worker_heartbeat_interval_seconds:
            logger.debug("worker_heartbeat", registered_jobs=registered)
            last_heartbeat = now

    logger.info("worker_stopped")
    sys.exit(0)
