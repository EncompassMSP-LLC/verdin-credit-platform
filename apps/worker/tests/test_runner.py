"""Worker dispatch failure handling tests."""

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.runner import dispatch_job


class FailingJob(BaseJob):
    job_type = JobType.OCR

    def run(self, context: JobContext) -> JobResult:
        raise RuntimeError(f"boom: {context.job_id}")


class CompletedJob(BaseJob):
    job_type = JobType.OCR

    def run(self, context: JobContext) -> JobResult:
        return JobResult(status=JobStatus.COMPLETED, message=f"done: {context.job_id}")


def test_dispatch_job_contains_job_exceptions(monkeypatch) -> None:
    monkeypatch.setattr("worker.runner.get_job", lambda _job_type: FailingJob())

    dispatch_job("job-1", JobType.OCR.value, {"document_id": "doc-1"})


def test_dispatch_job_accepts_successful_terminal_result(monkeypatch) -> None:
    monkeypatch.setattr("worker.runner.get_job", lambda _job_type: CompletedJob())

    dispatch_job("job-2", JobType.OCR.value, {"document_id": "doc-2"})
