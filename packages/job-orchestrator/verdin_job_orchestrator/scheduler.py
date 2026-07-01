"""In-memory scheduled job registry (scaffold for external cron wiring)."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from verdin_job_orchestrator.constants import JobType

PayloadFactory = Callable[[], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ScheduledJob:
    """Describes a recurring job enqueue target."""

    job_type: JobType
    cron_expression: str
    payload_factory: PayloadFactory = field(default=lambda: {})


class JobScheduler:
    """Registers scheduled jobs; execution is delegated to an external cron runner."""

    def __init__(self) -> None:
        self._jobs: dict[JobType, ScheduledJob] = {}

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
        """Placeholder hook — cron evaluation lands in a follow-up slice."""
        _ = at or datetime.now(tz=UTC)
        return []
