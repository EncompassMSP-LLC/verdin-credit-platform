"""In-memory scheduled job registry with cron evaluation."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from croniter import croniter

from verdin_job_orchestrator.constants import JobType

PayloadFactory = Callable[[], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ScheduledJob:
    """Describes a recurring job enqueue target."""

    job_type: JobType
    cron_expression: str
    payload_factory: PayloadFactory = field(default=lambda: {})


class JobScheduler:
    """Registers scheduled jobs and evaluates cron expressions."""

    def __init__(self) -> None:
        self._jobs: dict[JobType, ScheduledJob] = {}
        self._last_triggered: dict[JobType, datetime] = {}

    def register(self, scheduled_job: ScheduledJob) -> None:
        if scheduled_job.job_type in self._jobs:
            existing = self._jobs[scheduled_job.job_type]
            raise ValueError(
                f"Job type {scheduled_job.job_type.value!r} already scheduled "
                f"with cron {existing.cron_expression!r}",
            )
        self._jobs[scheduled_job.job_type] = scheduled_job

    def list_scheduled(self) -> list[ScheduledJob]:
        return list(self._jobs.values())

    def jobs_due_at(self, at: datetime | None = None) -> list[ScheduledJob]:
        current = (at or datetime.now(tz=UTC)).replace(second=0, microsecond=0)
        due: list[ScheduledJob] = []
        for scheduled in self._jobs.values():
            if not croniter.match(scheduled.cron_expression, current):
                continue
            last_triggered = self._last_triggered.get(scheduled.job_type)
            if last_triggered is not None and last_triggered >= current:
                continue
            due.append(scheduled)
        return due

    def mark_triggered(self, job_type: JobType, at: datetime | None = None) -> None:
        current = (at or datetime.now(tz=UTC)).replace(second=0, microsecond=0)
        self._last_triggered[job_type] = current
