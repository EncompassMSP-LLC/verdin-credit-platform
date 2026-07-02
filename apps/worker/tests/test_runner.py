"""Worker dispatch, retry, and scheduler tick tests."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from verdin_job_orchestrator import (
    InMemoryJobMetricsRecorder,
    JobScheduler,
    JobType,
    RetryPolicy,
    ScheduledJob,
)

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType as WorkerJobType
from worker.orchestrator import (
    ATTEMPT_PAYLOAD_KEY,
    build_default_scheduler,
    dispatch_job,
    tick_scheduler,
)


class FailingJob(BaseJob):
    job_type = WorkerJobType.OCR

    def run(self, context: JobContext) -> JobResult:
        raise RuntimeError(f"boom: {context.job_id}")


class CompletedJob(BaseJob):
    job_type = WorkerJobType.OCR

    def run(self, context: JobContext) -> JobResult:
        return JobResult(status=JobStatus.COMPLETED, message=f"done: {context.job_id}")


class FailedResultJob(BaseJob):
    job_type = WorkerJobType.OCR

    def run(self, context: JobContext) -> JobResult:
        return JobResult(status=JobStatus.FAILED, message="terminal failure")


def test_dispatch_job_contains_job_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("worker.orchestrator.get_job", lambda _job_type: FailingJob())

    dispatch_job("job-1", WorkerJobType.OCR.value, {"document_id": "doc-1"})


def test_dispatch_job_accepts_successful_terminal_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("worker.orchestrator.get_job", lambda _job_type: CompletedJob())
    metrics = InMemoryJobMetricsRecorder()

    dispatch_job(
        "job-2",
        WorkerJobType.OCR.value,
        {"document_id": "doc-2"},
        metrics=metrics,
    )

    assert metrics.completed
    assert metrics.completed[0][0] is JobType.OCR


def test_dispatch_job_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("worker.orchestrator.get_job", lambda _job_type: FailingJob())
    monkeypatch.setattr("worker.orchestrator.time.sleep", lambda _seconds: None)
    enqueue = MagicMock()
    metrics = InMemoryJobMetricsRecorder()

    dispatch_job(
        "job-3",
        WorkerJobType.OCR.value,
        {"document_id": "doc-3"},
        retry_policy=RetryPolicy(max_attempts=3),
        metrics=metrics,
        enqueue_fn=enqueue,
    )

    enqueue.assert_called_once()
    retry_payload = enqueue.call_args.args[1]
    assert retry_payload[ATTEMPT_PAYLOAD_KEY] == 2
    assert metrics.failed == [JobType.OCR]


def test_dispatch_job_retries_on_failed_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "worker.orchestrator.get_job", lambda _job_type: FailedResultJob()
    )
    monkeypatch.setattr("worker.orchestrator.time.sleep", lambda _seconds: None)
    enqueue = MagicMock()

    dispatch_job(
        "job-4",
        WorkerJobType.OCR.value,
        {},
        retry_policy=RetryPolicy(max_attempts=2),
        enqueue_fn=enqueue,
    )

    enqueue.assert_called_once()


def test_build_default_scheduler_registers_overdue_scan() -> None:
    scheduler = build_default_scheduler()
    scheduled = scheduler.list_scheduled()
    assert len(scheduled) == 1
    assert scheduled[0].job_type is JobType.OVERDUE_INVESTIGATION_SCAN


def test_tick_scheduler_enqueues_due_jobs() -> None:
    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression="0 6 * * *",
        ),
    )
    enqueue = MagicMock()
    metrics = InMemoryJobMetricsRecorder()
    due_at = datetime(2026, 7, 2, 6, 0, tzinfo=UTC)

    enqueued = tick_scheduler(scheduler, enqueue, at=due_at, metrics=metrics)

    assert enqueued == [JobType.OVERDUE_INVESTIGATION_SCAN]
    enqueue.assert_called_once()
    assert metrics.enqueued == [JobType.OVERDUE_INVESTIGATION_SCAN]

    # Second tick in the same minute should not duplicate enqueue.
    enqueue.reset_mock()
    assert tick_scheduler(scheduler, enqueue, at=due_at, metrics=metrics) == []
