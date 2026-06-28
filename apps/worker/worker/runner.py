"""Worker process loop: dequeue jobs and dispatch via the registry."""

import signal
import sys
import time
from typing import Any

import structlog

from worker import jobs  # noqa: F401 — register placeholder jobs
from worker.base import JobContext
from worker.config import get_worker_settings
from worker.queue import dequeue_job
from worker.registry import get_job, list_job_types

logger = structlog.get_logger(__name__)

_running = True


def handle_shutdown(signum: int, _frame: object) -> None:
    global _running
    logger.info("shutdown_signal_received", signal=signum)
    _running = False


def dispatch_job(job_id: str, job_type_value: str, payload: dict[str, Any]) -> None:
    from worker.constants import JobType

    job_type = JobType(job_type_value)
    job = get_job(job_type)
    context = JobContext(job_id=job_id, payload=payload)

    logger.info("job_started", job_id=job_id, job_type=job_type.value)
    try:
        result = job.run(context)
    except Exception as exc:
        logger.exception(
            "job_failed", job_id=job_id, job_type=job_type.value, error=str(exc)
        )
        return

    logger.info(
        "job_finished",
        job_id=job_id,
        job_type=job_type.value,
        status=result.status.value,
        message=result.message,
    )


def run_worker() -> None:
    settings = get_worker_settings()

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
    )

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    registered = [job_type.value for job_type in list_job_types()]
    logger.info(
        "worker_started",
        version=settings.app_version,
        queue=settings.worker_queue_name,
        registered_jobs=registered,
    )

    last_heartbeat = 0.0

    while _running:
        message = dequeue_job()
        if message is not None:
            dispatch_job(message.job_id, message.job_type.value, message.payload)
            continue

        now = time.monotonic()
        if now - last_heartbeat >= settings.worker_heartbeat_interval_seconds:
            logger.debug("worker_heartbeat", registered_jobs=registered)
            last_heartbeat = now

    logger.info("worker_stopped")
    sys.exit(0)
