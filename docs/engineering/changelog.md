# Engineering Decision Log

This log captures engineering decisions that are too implementation-oriented for release notes and not always large enough for an ADR.

For each sprint or milestone, record:

- Why a technical choice was made
- Alternatives considered
- Technical debt introduced, if any
- Follow-up work
- Performance observations
- Risks

Use ADRs for durable architecture decisions that require formal acceptance. Use release notes for user-facing changes. Use this log for technical context that future maintainers will need when debugging, refactoring, or planning.

## Sprint 4.3.0 — Operational Core

### Decision: Mission Control Aggregates Through One Endpoint

**Decision:** `GET /api/v1/dashboard` returns a single Mission Control snapshot with `overview`, `cases`, `accounts`, `documents`, `timeline`, `tasks`, `processing`, `performance`, and `alerts`.

**Reason:** Reduce frontend chattiness and keep metric ownership in the backend. The frontend should not know whether a metric comes from cases, documents, tasks, timeline, OCR, classification, metadata, or entity resolution.

**Alternatives considered:**

- Multiple frontend API calls to each domain module
- A frontend composition layer that calls domain APIs and merges results
- Separate dashboard endpoints for KPIs, timeline, tasks, alerts, and processing

**Technical debt introduced:** Aggregation query complexity is concentrated in `api/modules/dashboard/repository.py`.

**Follow-up work:**

- Measure dashboard aggregation latency in Sprint 4.3.1.
- Add indexes or query refactors if p95 latency exceeds the `<500 ms` target.
- Consider a denormalized read model if dashboard traffic or metric count grows substantially.

**Performance observations:** Baseline not yet captured. Sprint 4.3.1 owns measurement.

**Risks:** A single aggregation endpoint can become slow or difficult to maintain if it accumulates too much domain-specific logic.

### Decision: Timeline Is the First Event Consumer

**Decision:** Domain services publish platform events, and the timeline subscriber persists append-only `TimelineEvent` rows.

**Reason:** Establish an event-driven foundation without introducing a full workflow engine too early.

**Alternatives considered:**

- Direct timeline writes from each domain service
- Full event-stream infrastructure before timeline requirements were proven
- No event bus until workflow automation

**Technical debt introduced:** The event bus is currently lightweight and in-process; future durable delivery semantics are not yet defined.

**Follow-up work:**

- Validate event publishing in cross-module workflow tests.
- Decide whether workflow automation in 4.5 needs durable queue semantics.
- Add delivery metrics when job orchestration is introduced.

**Performance observations:** Timeline query speed target for Sprint 4.3.1 is `<250 ms` for common recent activity/filter queries.

**Risks:** If event consumers expand without orchestration and metrics, retry and ordering behavior may become inconsistent.

### Decision: Task Management Is a First-Class Operational Module

**Decision:** Tasks have their own model, repository, service, router, API client, validation types, and UI rather than remaining a placeholder.

**Reason:** Automation and dashboard alerts need a durable work queue with RBAC, timeline events, filters, assignment, due dates, and lifecycle transitions.

**Alternatives considered:**

- Keep tasks as a simple case sub-resource
- Generate tasks only from future workflow automation
- Store task-like items as timeline metadata

**Technical debt introduced:** Automatic task creation rules are not yet centralized. Sprint 4.3.1 should verify current event-driven task behavior and document gaps.

**Follow-up work:**

- Add cross-module tests for task creation from events.
- Feed high-priority overdue tasks into Mission Control alerts.
- Use tasks as the target primitive for 4.5 workflow automation.

**Performance observations:** Task query baseline should include list, overdue, due-today, and high-priority filters.

**Risks:** If automation creates tasks without idempotency guarantees, duplicate operational work items may appear.

### Decision: Stabilize Before Starting Version 4.5

**Decision:** Sprint 4.3.1 is a stabilization sprint before new automation features begin.

**Reason:** Version 4.3.0 introduced the core operating model. Validating full workflows, performance, security, and coverage before automation reduces the risk of carrying foundational issues into larger AI and workflow features.

**Alternatives considered:**

- Begin 4.5 import wizard immediately
- Fix stabilization issues opportunistically during 4.5 feature work
- Treat dashboard merge as sufficient validation

**Technical debt introduced:** None intentionally; the sprint exists to identify and retire debt.

**Follow-up work:**

- Complete the Sprint 4.3.1 checklist.
- Capture performance baselines.
- Save the v4.3.0 architecture snapshot as the as-built reference.

**Performance observations:** Baseline targets are defined in `docs/sprint-4.3.1/operational-core-stabilization.md`.

**Risks:** If stabilization is skipped, 4.5 automation could amplify hidden workflow or performance defects.

## Version 4.5 Planning

### Decision: Adopt Predictable Release Cadence

**Decision:** Use `main` as always releasable, `feature/*` for individual capabilities, `sprint/*` for stabilization and integration, semantic tags for releases, and GitHub Releases for every tagged version.

**Reason:** The platform has matured from scaffold to Operational Core. A predictable cadence preserves a clean, auditable history while Version 4.5 adds larger automation and AI capabilities.

**Alternatives considered:**

- Continue merging all work directly through feature branches without stabilization branches
- Tag only major releases and skip patch/stabilization tags
- Use release notes in the repo without GitHub Releases

**Technical debt introduced:** None intentionally. The process adds lightweight release ceremony that must be kept current.

**Follow-up work:**

- Tag `v4.3.0` from `main` after Mission Control is merged.
- Publish a GitHub Release for `v4.3.0` using the GA release notes.
- Use a `sprint/4.3.1-stabilization` branch for the stabilization checklist if multiple fixes or test suites are needed.
- Tag `v4.3.1` only after end-to-end workflow tests, baselines, security review, and coverage goals pass consistently in CI.

**Performance observations:** Release tags should reference the baseline metrics captured in Sprint 4.3.1 so future versions can compare dashboard, OCR, entity resolution, timeline, and task performance.

**Risks:** If `main` is allowed to drift from releasable status, tags and GitHub Releases lose trust as audit artifacts. If stabilization work is mixed into broad feature branches, 4.5 may inherit unresolved Operational Core issues.

### Decision: Group 4.5 Into Four Focused Epics

**Decision:** Organize Version 4.5 around four cohesive epics:

1. Credit Report Intelligence
2. Workflow Automation
3. AI Assistance
4. Client Experience

**Reason:** Grouping related capabilities keeps the release cohesive and prevents 4.5 from becoming a collection of unrelated features.

**Alternatives considered:**

- Track each feature as a separate epic
- Start with AI features before import/workflow foundations
- Continue extending foundational CRUD modules

**Technical debt introduced:** Epic boundaries may need refinement after Sprint 4.3.1 reveals workflow or performance constraints.

**Follow-up work:**

- Open a formal Version 4.5 kickoff milestone after Sprint 4.3.1 exits.
- Define success criteria and dependency maps for each epic.
- Verify each epic builds on Operational Core contracts.

**Performance observations:** Automation should be evaluated against 4.3.1 baselines.

**Risks:** If epics modify core contracts rather than leveraging them, 4.5 could create avoidable architectural churn.

### Decision: Plan a Unified Job Orchestration Layer

**Decision:** By the end of Version 4.5, background processing should converge on a unified job orchestration layer, proposed as `packages/job-orchestrator/`.

Potential package shape:

```text
packages/job-orchestrator/
├── job.py
├── queue.py
├── scheduler.py
├── retry.py
├── registry.py
└── metrics.py
```

**Reason:** 4.5 will add many background processes: OCR, classification, metadata extraction, entity resolution, workflow automation, notifications, AI summaries, and report imports. A shared orchestration layer gives them consistent retries, scheduling, metrics, and monitoring.

**Alternatives considered:**

- Let each worker job manage its own queue and retry policy
- Adopt Celery/RabbitMQ/Kafka immediately
- Keep the current lightweight Redis job helpers indefinitely

**Technical debt introduced:** None yet; this is planned architecture. If delayed too long, duplicated retry and scheduling logic may emerge across worker jobs.

**Follow-up work:**

- During 4.3.1, inventory current worker job patterns and retry behavior.
- In 4.5 kickoff, decide whether `packages/job-orchestrator/` is introduced before or during the Workflow Automation epic.
- Define metrics required for Mission Control and future operational dashboards.

**Performance observations:** Job orchestration should emit queue depth, duration, retry count, failure count, and throughput metrics.

**Risks:** Introducing orchestration too early could over-abstract current needs; introducing it too late could leave 4.5 with fragmented job semantics.

## Version 4.5.0 — Automation release candidate sign-off

### Decision: Formal scope limits and deferrals for v4.5.0

**Decision:** Version 4.5.0 ships as a **release candidate** with three **Partial** epics (workflow auto-tasks, dispute foundation, rules AI) and explicit deferral of client experience, LLM assistance, BPM/cron, and job-orchestrator package to 4.8+.

**Reason:** The sprint loop delivered import intelligence, dispute lifecycle, and event-driven tasks with E2E coverage. Remaining roadmap items (portal, notifications, LLM) require infrastructure or compliance gates not in scope for this RC.

**Alternatives considered:**

- Hold v4.5.0 until LLM features ship (blocked on provider/PII approval)
- Mark Partial capabilities as ✅ without written limits (rejected — governance requires scope notes)
- Defer dispute generation entirely to 4.8 (rejected — foundation lifecycle is production-usable)

**Technical debt introduced:** Overdue investigation uses read-time escalation on account GET rather than a scheduled worker job.

**Follow-up work:**

- Release notes and `v4.5.0` tag (slice 5.5–5.6)
- 4.8 kickoff: notifications, LLM policy, `job-orchestrator` evaluation

**Documentation:** [`docs/governance/version-4.5-scope.md`](../governance/version-4.5-scope.md), capability matrix epic sign-off table.

**Risks:** Stakeholders may expect full workflow engine or LLM in 4.5 — scope doc is the source of truth for what shipped vs deferred.

## Version 4.8.0 — Operations kickoff

### Decision: In-app notifications as first 4.8 slice

**Decision:** Ship persisted per-user in-app notifications (API + staff bell UI) before email/SMS delivery or client portal auth.

**Reason:** Notifications are a dependency for workflow reminders, dispute updates, and future client messaging. In-app delivery requires no external provider.

**Alternatives considered:**

- Start with client portal (rejected — needs client model + auth partition first)
- Start with LLM summaries (rejected — policy ADR gate not yet merged)
- Defer notifications to email-first (rejected — no delivery infra in 4.5)

**Technical debt introduced:** Notification creation is admin-only HTTP for now; workflow modules should call `NotificationService.notify_user()` in follow-up slices.

**Follow-up work:**

- Wire auto-task and dispute lifecycle events to `notify_user`
- Scheduled overdue investigation worker (checklist slice 4)
- Email delivery scaffold (checklist slice 9)

**Documentation:** [`docs/governance/version-4.8-scope.md`](../governance/version-4.8-scope.md), [`docs/development/version-4.8-completion-checklist.md`](../development/version-4.8-completion-checklist.md)

**Risks:** Users may expect email/SMS in the same slice — scope doc limits 4.8 notifications to in-app for RC.

## Version 4.8 — Overdue investigation worker

### Decision: Worker scan replaces GET auto-escalation

**Decision:** Add `overdue_investigation_scan` worker job to scan eligible accounts and create escalation tasks. Remove read-time escalation from `GET /accounts/{id}`; retain explicit `POST /accounts/{id}/dispute-investigation-overdue` for staff.

**Reason:** 4.5 technical debt used account GET as a pseudo-cron. A dedicated worker job is schedulable and auditable without side effects on read paths.

**Follow-up work:** Wire daily enqueue via external cron or `JobScheduler` registry (slice 5 scaffold).

## Version 4.8 — Job orchestration package scaffold

### Decision: Extract shared orchestration into `packages/job-orchestrator/`

**Decision:** Introduce `verdin-job-orchestrator` with job contracts, registry, Redis queue, retry/scheduler/metrics scaffolds, and ADR-011. API and worker import shared `JobType` / queue primitives via thin re-export modules.

**Reason:** Duplicated enqueue code and enums between API and worker blocked consistent retries, scheduling, and observability.

**Alternatives considered:**

- Full Celery migration in 4.8 (rejected — ops cost)
- Defer package to 5.0 (rejected — overdue scan and future jobs need a convergence point now)

**Technical debt introduced:** Retry policy and metrics recorders are not yet wired into `worker/runner.py`; cron evaluation in `JobScheduler` is a placeholder.

**Follow-up work:**

- Wire runner retries and metrics export
- Register scheduled jobs (overdue scan daily cron) when scheduler executes expressions
- PostgreSQL job persistence per ADR-008 Sprint 2 plan

**Documentation:** [`docs/adr/011-job-orchestrator.md`](../adr/011-job-orchestrator.md)
