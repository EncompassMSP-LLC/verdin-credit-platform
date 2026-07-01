"""Job metrics recording scaffold."""

from dataclasses import dataclass, field
from typing import Protocol

from verdin_job_orchestrator.constants import JobType


class JobMetricsRecorder(Protocol):
    def record_enqueued(self, job_type: JobType) -> None: ...

    def record_started(self, job_type: JobType) -> None: ...

    def record_completed(self, job_type: JobType, duration_seconds: float) -> None: ...

    def record_failed(self, job_type: JobType) -> None: ...


class NullJobMetricsRecorder:
    """No-op metrics sink until Mission Control exports queue telemetry."""

    def record_enqueued(self, job_type: JobType) -> None:
        _ = job_type

    def record_started(self, job_type: JobType) -> None:
        _ = job_type

    def record_completed(self, job_type: JobType, duration_seconds: float) -> None:
        _ = job_type, duration_seconds

    def record_failed(self, job_type: JobType) -> None:
        _ = job_type


@dataclass
class InMemoryJobMetricsRecorder:
    """Test double that accumulates metric events."""

    enqueued: list[JobType] = field(default_factory=list)
    started: list[JobType] = field(default_factory=list)
    completed: list[tuple[JobType, float]] = field(default_factory=list)
    failed: list[JobType] = field(default_factory=list)

    def record_enqueued(self, job_type: JobType) -> None:
        self.enqueued.append(job_type)

    def record_started(self, job_type: JobType) -> None:
        self.started.append(job_type)

    def record_completed(self, job_type: JobType, duration_seconds: float) -> None:
        self.completed.append((job_type, duration_seconds))

    def record_failed(self, job_type: JobType) -> None:
        self.failed.append(job_type)
