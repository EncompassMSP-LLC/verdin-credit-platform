# Sprint 4.3.1 — Operational Core Stabilization

**Purpose:** stabilize Version 4.3.0 before opening Version 4.5 automation work.

Version 4.3.0 establishes the Operational Core: cases, accounts, documents, OCR, classification, metadata, entity resolution, timeline, tasks, and Mission Control. Sprint 4.3.1 should validate that those capabilities work as one product, establish performance baselines, and close reliability or security gaps before new automation features build on top.

## Workstreams

Sprint 4.3.1 is organized into measurable workstreams rather than miscellaneous cleanup:

| Workstream            | Status      | Goal                                                                              |
| --------------------- | ----------- | --------------------------------------------------------------------------------- |
| Quality               | ✅ Complete | E2E workflow tests, cross-module coverage, eliminate flaky tests                  |
| Performance           | ✅ Complete | Benchmark dashboard aggregation, profile document pipeline, capture baselines     |
| Security              | ✅ Complete | RBAC coverage, authentication audit, upload/storage validation, dependency review |
| Operational Readiness | Planned     | Logging, health checks, observability, deployment docs, backup/recovery           |

The execution order below maps to these workstreams.

## Execution Order

### 1. End-to-End Workflow Validation ✅ Delivered

A black-box workflow suite ships in [`tests/e2e/`](../../tests/e2e/README.md) and
runs in CI via [`.github/workflows/e2e.yml`](../../.github/workflows/e2e.yml). A
single test (`test_full_case_lifecycle`) drives the journey below against a
running API and worker over HTTP and serves as the release gate. It passes
consistently (5/5 local runs, ~9s each).

> **Reliability fix surfaced by the gate:** the API enqueued the OCR job
> _before_ the request transaction committed, so an idle worker could dequeue
> and query the document before it was durable (`"Document not found"` →
> permanent stall). Fixed by committing the unit of work before enqueuing, in
> both the API (`documents` upload/version) and the worker chain (OCR →
> classify → metadata → entity resolution each enqueue the next stage only
> after its writes commit).

Automate the complete operational workflow as an integration test suite that can run in CI:

```text
Create Organization
    ↓
Create Case
    ↓
Add Credit Account
    ↓
Upload Credit Report
    ↓
OCR
    ↓
Classification
    ↓
Metadata Extraction
    ↓
Entity Resolution
    ↓
Timeline Events
    ↓
Task Creation
    ↓
Mission Control Dashboard
```

Golden path checklist:

- [x] Create a dedicated backend integration suite for the full workflow.
- [x] Seed organization and users with representative roles.
- [x] Create a case and linked credit account.
- [x] Upload a credit report fixture and assert document metadata, storage key, hash, and version state.
- [x] Run OCR (real worker) and assert status transitions and extracted text.
- [x] Run classification and assert document type, confidence, method, and timestamp.
- [x] Run metadata extraction and assert extracted fields.
- [x] Run entity resolution and assert a matched account that links back to the document.
- [x] Assert timeline events exist for each key domain action (upload, OCR, classification, metadata, entity resolution).
- [x] Assert task creation succeeds for operational work items.
- [x] Assert Mission Control includes the case, document, task, processing, timeline, and alert data.
- [ ] Add the E2E workflow as a required GitHub status check for merges into `main`.

Keep `test_full_case_lifecycle.py` focused on the fast, deterministic happy path. Edge cases should be isolated into separate E2E scenarios so failures diagnose one behavior at a time:

- `test_entity_resolution_ambiguous.py` — ambiguous match
- `test_entity_resolution_unmatched.py` — no match
- `test_ocr_failure_recovery.py` — OCR retry
- `test_worker_restart.py` — worker resilience

### Remaining Sprint 4.3.1 Priorities

With the golden-path E2E suite live, complete the remaining stabilization work in this order:

1. ✅ Performance baselines: captured in [`docs/quality/performance/v4.3.1-baseline.md`](../quality/performance/v4.3.1-baseline.md).
2. ✅ Security review: verified RBAC, authentication flows, upload validation, dependency audit, secrets, and configuration.
3. ✅ Coverage improvements: focused on cross-module workflows and event-driven interactions rather than raw percentage growth.
4. ✅ Branch protection: `main` requires PR review, up-to-date branches, CI checks, and the golden-path E2E workflow.

### 2. Performance Baselines ✅ Complete

Capture baseline metrics before optimizing. These numbers become the comparison point for Version 4.5 automation.

Tracking document: [`docs/quality/performance/v4.3.1-baseline.md`](../quality/performance/v4.3.1-baseline.md)

| Metric              | Initial Target                        |
| ------------------- | ------------------------------------- |
| Dashboard API       | `<500 ms`                             |
| Login               | `<150 ms`                             |
| Case creation       | `<200 ms`                             |
| Document upload     | `<500 ms` excluding OCR               |
| OCR processing      | Record baseline by file type and size |
| Classification      | Record baseline by file type and size |
| Metadata extraction | Record baseline by file type and size |
| Entity resolution   | Record baseline by candidate set size |
| Timeline write      | `<100 ms`                             |

Capture:

- [x] Dataset size and seed shape.
- [x] Local versus CI or containerized environment.
- [x] Median, p95, and max latency where practical.
- [ ] Re-measure in CI and establish candidate performance regression thresholds.
- [x] Profile login latency before optimizing.

### 3. Security Review

Create and execute a pass/fail security checklist.

Tracking document: [`docs/quality/security/v4.3.1-review.md`](../quality/security/v4.3.1-review.md)

- [x] Authentication: login, JWT expiration and refresh, invalid token handling, inactive user behavior.
- [x] Authorization: RBAC verification for protected endpoints and organization isolation.
- [x] File uploads: MIME validation, file size limits, malformed document handling, duplicate hash behavior.
- [x] Object storage: MinIO bucket policy, object access controls, authenticated downloads.
- [x] Secrets and configuration: environment-driven settings, no hardcoded production credentials, safe CI logging.
- [x] Dependencies: frontend dependency audit, Python dependency audit, critical/high findings triaged.

Expected output: security findings with severity, affected paths, and recommended fixes.

Run this workstream before expanding coverage. Security findings may change the behavior that high-value tests need to enforce.

### 4. Test Coverage

Expand confidence through high-value cross-module scenarios rather than chasing raw coverage percentage:

- [x] Event bus publishing/subscribing.
- [x] Worker retry/failure behavior.
- [x] Dashboard aggregation.
- [x] Entity resolution edge cases.
- [x] Timeline generation.
- [x] RBAC denial paths for dashboard, tasks, documents, and timeline endpoints.

### 5. Architecture Review

Review the current implementation against the architecture and governance docs before introducing Version 4.5 complexity.

For each major module (`auth`, `cases`, `accounts`, `documents`, `timeline`, `tasks`, `dashboard`, worker jobs):

- [ ] Follows router → service → repository; routers do not query SQLAlchemy directly.
- [ ] Business logic lives in services, database access in repositories.
- [ ] Publishes events instead of tightly coupling modules when actions are user-visible or workflow-relevant.
- [ ] Complies with accepted ADRs.
- [ ] Avoids duplicate business logic across modules.
- [ ] Preserves organization scoping and role checks.
- [ ] Has clear test coverage for success, failure, and RBAC paths.

Architecture snapshot:

- [ ] Generate and save [`docs/architecture/v4.3.0-snapshot.md`](../architecture/v4.3.0-snapshot.md).
- [ ] Include module map, package dependencies, event flow, database entities, API surface, active ADRs, and v4.3.0 capability matrix.
- [ ] Treat the snapshot as the as-built reference for regression investigations during Version 4.5.

### 6. Operational Readiness

Confirm the Operational Core is deployable, observable, and recoverable before automation expands the surface area:

- [ ] Verify structured logging is consistent across API, worker, and background jobs.
- [ ] Verify health checks for API, database, Redis, and object storage.
- [ ] Confirm observability for request latency, errors, and job outcomes (metrics or logs).
- [ ] Ensure deployment documentation (Docker Compose and environment setup) is current.
- [ ] Validate PostgreSQL backup and restore procedure.
- [ ] Validate object storage (MinIO) backup and recovery procedure.
- [ ] Document any operational gaps with owners and follow-up actions.

## Definition of Done

- [ ] Golden-path E2E passes consistently in CI.
- [x] Performance baselines are captured and documented.
- [x] Security review is completed with tracked findings.
- [x] High-value workflow coverage is expanded.
- [x] Branch protection is configured to enforce the E2E release gate.
- [x] No critical or high-severity issues are outstanding.
- [ ] Version 4.5 planning starts from stable Operational Core contracts, not foundational rewrites.

## Version 4.5 Opening Focus

Version 4.5 should intentionally shift from foundational CRUD to automation and intelligence. Every 4.5 epic should leverage the Operational Core instead of modifying its core contracts.

Recommended first epic:

1. Credit Report Import Wizard

This should open Version 4.5 because it exercises nearly every Operational Core subsystem: document ingestion, OCR, classification, metadata extraction, entity resolution, timeline, tasks, and Mission Control.

Suggested follow-up epic order:

1. Bureau-specific parsers
2. Workflow Automation Engine
3. Dispute Generation Engine
4. AI Case Assistant
5. Client Portal
6. Notifications

## Recommended 4.5 Principles

- Build on Mission Control and timeline events as the operational source of truth.
- Prefer workflow automation around existing case/task/document primitives.
- Keep AI outputs auditable: model/version, confidence, source document, timestamp.
- Preserve 4.3 public API contracts unless a formal migration is documented.
- Avoid foundational data-model churn during the first automation sprint.
- Establish a dedicated **Job Orchestration** capability early in 4.5 so OCR, automation, AI processing, notifications, and imports share one execution model (see [`docs/engineering/changelog.md`](../engineering/changelog.md)) instead of evolving independently.
