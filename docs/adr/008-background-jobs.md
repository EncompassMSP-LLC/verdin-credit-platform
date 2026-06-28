# ADR-008: Redis-Backed Background Jobs

**Date:** 2026-06-28  
**Authors:** Platform Team

## Status

Accepted

## Context

Credit operations require long-running work that must not block HTTP requests: document OCR, bulk report imports, AI-generated summaries, and scheduled monthly reviews. The platform already runs Redis for caching and includes an `apps/worker` process in Docker Compose, but Sprint 1 had only a heartbeat loop with no job contract.

We needed a job architecture that:

- Decouples the API from execution time and failure retries
- Allows multiple worker instances to consume from a shared queue
- Registers job types explicitly so new work is discoverable
- Defers heavy implementation (OCR, AI) to Sprint 2 while establishing patterns now

Alternatives considered: Celery (heavier operational footprint), ARQ/RQ (viable; deferred to keep Sprint 1 minimal), direct PostgreSQL polling (poor fit for bursty workloads).

## Decision

Use a **Redis list queue** with a dedicated worker process and a small in-house job framework in `apps/worker/worker/`:

| Component      | Responsibility                                                                |
| -------------- | ----------------------------------------------------------------------------- |
| `config.py`    | `WorkerSettings` — `REDIS_URL`, `WORKER_QUEUE_NAME`, poll/heartbeat intervals |
| `constants.py` | `JobType`, `JobStatus` shared constants                                       |
| `base.py`      | `BaseJob`, `JobContext`, `JobResult` interface                                |
| `registry.py`  | `@register_job` decorator and type → implementation lookup                    |
| `queue.py`     | `enqueue_job()` (LPUSH), `dequeue_job()` (BRPOP), `JobMessage` schema         |
| `runner.py`    | Poll loop, dispatch, graceful shutdown on SIGINT/SIGTERM                      |
| `jobs/`        | One module per job type                                                       |

### Registered job types (Sprint 1 placeholders)

| `JobType`        | Purpose                      |
| ---------------- | ---------------------------- |
| `ocr`            | Document text extraction     |
| `report_import`  | Bulk credit report ingestion |
| `ai_summary`     | Case/document summarization  |
| `monthly_review` | Scheduled portfolio review   |

### Job status lifecycle

`pending` → `queued` → `running` → `completed` | `failed` | `cancelled`

Sprint 1 placeholders log and return without performing real work. Sprint 2 will add PostgreSQL job records and API status polling.

### Sprint 2 triggering (planned, not implemented)

1. API service validates the request and creates a job record in PostgreSQL
2. API enqueues a JSON message to Redis (`verdin:jobs` by default)
3. Worker dequeues, resolves `job_type` via the registry, calls `BaseJob.run()`
4. Worker updates job status in PostgreSQL; API exposes `GET /api/v1/jobs/{id}`
5. Feature flags (`ENABLE_AI`, `ENABLE_IMPORTS`) gate which endpoints may enqueue jobs

## Consequences

### Positive

- HTTP handlers stay fast; failures in background work do not block user requests
- Redis BRPOP supports multiple workers without additional broker infrastructure
- Registry pattern makes job types explicit and testable
- Placeholder jobs document the Sprint 2 contract before implementation begins

### Negative

- Redis lists lack built-in retry, dead-letter, and priority semantics; these must be added in application code or a future broker migration
- API and worker currently share the enqueue contract by convention; a shared Python package may be extracted later
- No job persistence in Sprint 1 — restarts lose in-flight queue messages until PostgreSQL backing lands

### Neutral

- Run locally: `docker compose up redis -d` then `python main.py` in `apps/worker`
- See [`docs/developer-guide.md`](../developer-guide.md#background-jobs) for layout and enqueue examples
- Job implementations must respect feature flags and audit requirements from [`AGENTS.md`](../../AGENTS.md)
