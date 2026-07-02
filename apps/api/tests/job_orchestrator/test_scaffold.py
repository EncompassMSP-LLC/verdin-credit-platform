"""Tests for packages/job-orchestrator scaffold."""

from verdin_job_orchestrator import (
    BaseJob,
    InMemoryJobMetricsRecorder,
    JobContext,
    JobResult,
    JobScheduler,
    JobStatus,
    JobType,
    RedisJobQueue,
    RetryPolicy,
    ScheduledJob,
    clear_registry,
    compute_backoff_seconds,
    get_job,
    register_job,
    should_retry,
)


class EchoJob(BaseJob):
    job_type = JobType.OCR

    def run(self, context: JobContext) -> JobResult:
        return JobResult(status=JobStatus.COMPLETED, message=context.job_id)


def test_register_and_resolve_job() -> None:
    clear_registry()
    register_job(EchoJob)

    job = get_job(JobType.OCR)
    result = job.run(JobContext(job_id="job-1", payload={"document_id": "doc-1"}))

    assert result.status is JobStatus.COMPLETED
    assert result.message == "job-1"


def test_retry_backoff_and_limit() -> None:
    policy = RetryPolicy(max_attempts=3, base_delay_seconds=2.0, max_delay_seconds=10.0)

    assert compute_backoff_seconds(1, policy) == 2.0
    assert compute_backoff_seconds(2, policy) == 4.0
    assert compute_backoff_seconds(3, policy) == 8.0
    assert compute_backoff_seconds(4, policy) == 10.0
    assert should_retry(1, policy) is True
    assert should_retry(2, policy) is True
    assert should_retry(3, policy) is False


def test_scheduler_registers_unique_job_types() -> None:
    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression="0 6 * * *",
        ),
    )

    scheduled = scheduler.list_scheduled()
    assert len(scheduled) == 1
    assert scheduled[0].job_type is JobType.OVERDUE_INVESTIGATION_SCAN


def test_scheduler_jobs_due_at_for_matching_cron() -> None:
    from datetime import UTC, datetime

    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression="0 6 * * *",
        ),
    )

    due = scheduler.jobs_due_at(datetime(2026, 7, 2, 6, 0, tzinfo=UTC))
    assert len(due) == 1


def test_in_memory_metrics_recorder() -> None:
    recorder = InMemoryJobMetricsRecorder()
    recorder.record_enqueued(JobType.OCR)
    recorder.record_started(JobType.OCR)
    recorder.record_completed(JobType.OCR, 1.25)
    recorder.record_failed(JobType.OCR)

    assert recorder.enqueued == [JobType.OCR]
    assert recorder.started == [JobType.OCR]
    assert recorder.completed == [(JobType.OCR, 1.25)]
    assert recorder.failed == [JobType.OCR]


def test_redis_job_queue_round_trip(monkeypatch) -> None:
    queue_name = "verdin:jobs"
    store: dict[str, list[str]] = {queue_name: []}

    class FakeRedis:
        def lpush(self, queue_name: str, payload: str) -> None:
            store[queue_name].insert(0, payload)

        def brpop(self, queue_name: str, timeout: int) -> tuple[str, str] | None:
            _ = timeout
            if not store[queue_name]:
                return None
            return queue_name, store[queue_name].pop()

    queue = RedisJobQueue("redis://localhost:6379/0", queue_name)
    monkeypatch.setattr(queue, "_get_client", lambda: FakeRedis())

    message = queue.enqueue(JobType.OCR, {"document_id": "doc-1"})
    dequeued = queue.dequeue(timeout_seconds=0)

    assert dequeued is not None
    assert dequeued.job_id == message.job_id
    assert dequeued.job_type is JobType.OCR
    assert dequeued.payload == {"document_id": "doc-1"}
