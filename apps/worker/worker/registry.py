"""Job registry for mapping job types to implementations."""

from worker.base import BaseJob
from worker.constants import JobType

_REGISTRY: dict[JobType, type[BaseJob]] = {}


def register_job(job_cls: type[BaseJob]) -> type[BaseJob]:
    job_type = job_cls.job_type
    if job_type in _REGISTRY:
        existing = _REGISTRY[job_type]
        raise ValueError(
            f"Job type {job_type.value!r} is already registered by {existing.__name__}",
        )
    _REGISTRY[job_type] = job_cls
    return job_cls


def get_job(job_type: JobType) -> BaseJob:
    job_cls = _REGISTRY.get(job_type)
    if job_cls is None:
        registered = ", ".join(sorted(item.value for item in _REGISTRY))
        raise KeyError(
            f"Unknown job type {job_type.value!r}. Registered: {registered or 'none'}"
        )
    return job_cls()


def list_job_types() -> list[JobType]:
    return list(_REGISTRY.keys())
