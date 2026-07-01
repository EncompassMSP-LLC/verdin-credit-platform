"""Base job interface and execution context."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from verdin_job_orchestrator.constants import JobStatus, JobType


@dataclass(slots=True)
class JobContext:
    job_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JobResult:
    status: JobStatus
    message: str = ""
    data: dict[str, Any] | None = None


class BaseJob(ABC):
    """Contract for background jobs dispatched by the worker registry."""

    job_type: ClassVar[JobType]

    @abstractmethod
    def run(self, context: JobContext) -> JobResult:
        """Execute the job and return a terminal or intermediate status."""
