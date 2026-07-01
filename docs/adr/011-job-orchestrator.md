# ADR-011: Unified Job Orchestration Package

**Date:** 2026-07-01  
**Authors:** Platform Team

## Status

Accepted

## Context

Version 4.5 deferred a shared `packages/job-orchestrator/` layer while background work lived in `apps/worker/worker/` with a duplicated enqueue contract in `apps/api/api/core/job_queue.py`. By Version 4.8 the platform runs nine job types (OCR pipeline, entity resolution, overdue investigation scan, and others) with no shared retry, scheduling, or metrics semantics.

ADR-008 established the Redis list queue and worker registry. The engineering decision log (Version 4.5) recommended converging on a unified orchestration package before job semantics fragment further.

Alternatives considered:

- **Keep worker-local helpers indefinitely** — lowest short-term cost; duplicates enums and queue code between API and worker.
- **Adopt Celery/ARQ immediately** — stronger broker features but heavier ops and migration cost for 4.8 partial scope.
- **Full orchestration parity in one PR** — retries, PostgreSQL job records, cron runner, and metrics export together; too large for a single reviewable slice.

## Decision

Introduce **`packages/job-orchestrator/`** (`verdin-job-orchestrator`) as the shared orchestration layer with these modules:

| Module         | Responsibility (4.8 scaffold)                                     |
| -------------- | ----------------------------------------------------------------- |
| `job.py`       | `BaseJob`, `JobContext`, `JobResult`                              |
| `constants.py` | `JobType`, `JobStatus` (single source of truth)                   |
| `registry.py`  | `@register_job`, lookup helpers                                   |
| `queue.py`     | `JobMessage`, `RedisJobQueue` (LPUSH / BRPOP)                     |
| `retry.py`     | `RetryPolicy`, backoff helpers (not yet wired into runner)        |
| `scheduler.py` | `ScheduledJob`, in-memory registry (cron evaluation deferred)     |
| `metrics.py`   | `JobMetricsRecorder` protocol + no-op / in-memory implementations |

**Migration approach (incremental):**

1. **4.8 slice 5 (this ADR):** Package scaffold; `apps/worker` and `apps/api` import shared primitives via thin re-export modules.
2. **Follow-up slices:** Wire `RetryPolicy` into `worker/runner.py`, register overdue scan in `JobScheduler`, export metrics to Mission Control, and evaluate PostgreSQL job persistence (ADR-008 Sprint 2 plan).
3. **5.0+:** Re-evaluate Celery/ARQ only if Redis list limits block scale.

Scheduled jobs (e.g. daily `overdue_investigation_scan`) remain enqueued by external cron calling `enqueue_job` until the scheduler executes cron expressions in-process or via a dedicated orchestrator service.

## Consequences

### Positive

- One `JobType` / `JobStatus` definition shared by API and worker
- Retry, scheduler, and metrics contracts exist before runner integration
- Package is installable via editable `-e ../../packages/job-orchestrator` like other Verdin Python packages
- ADR-008 remains valid; this package extracts and extends its patterns

### Negative

- Worker and API still own Redis URL / queue name wiring — not yet injected through a single orchestrator service
- Retry and metrics are scaffold-only until runner and dashboard slices land
- Registry is process-local; multi-worker registration still requires importing job modules at startup

### Neutral

- See [`docs/developer-guide.md`](../developer-guide.md#background-jobs) for enqueue examples
- Capability matrix row **Job Orchestration** tracks scaffold vs full parity
- Supersedes duplicated enum definitions in `apps/api/api/core/job_queue.py` (now re-exports from package)
