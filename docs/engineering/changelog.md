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

## Compliance intelligence — attorney-preserve checklist

**Decision:** Add `GET /cases/{case_id}/dispute-strategy/attorney-checklist` that lists required/optional packet items for strategy accounts (attorney_preserve is always recommended as hygiene). Near-ceiling scores are escalation-flagged.

**Reason:** Attorney-preserve was advisory only; investigators needed a concrete handoff checklist without transmitting materials to counsel automatically.

**Alternatives considered:** PDF packet export only; merge into CFPB checklist endpoint.

**Technical debt:** Checklist is heuristic; does not verify which exhibits are already on the case.

**Follow-up work:** Mark checklist items complete against case documents; optional packet PDF export.

## Compliance intelligence — CFPB escalation checklist

**Decision:** Add `GET /cases/{case_id}/dispute-strategy/cfpb-checklist` that lists required/optional packet items for accounts where the strategy CFPB stage is recommended.

**Reason:** CFPB escalation was advisory only; investigators needed a concrete preservation/filing checklist without auto-submission.

**Alternatives considered:** Auto-create CFPB portal drafts; PDF export only.

**Technical debt:** Checklist is heuristic; does not verify which exhibits are already on the case.

**Follow-up work:** Mark checklist items complete against case documents.

## Compliance intelligence — strategy account metadata inference

**Decision:** Infer `account_type` / `account_status` / `payment_status` from strategy `primary_rule_ids` when creating direct (non-discrepancy) accounts during strategy prepare.

**Reason:** Direct accounts were created as OTHER/UNKNOWN, which weakened dispute draft context.

**Alternatives considered:** Persist full tradeline snapshot on strategy targets; require parsed-candidate import first.

**Technical debt:** Heuristic only; rule text must mention status tokens to map.

**Follow-up work:** Pull status from parsed tradeline when document_id is known; attorney-preserve packet export.

## Compliance intelligence — direct strategy account letter prep

**Decision:** Extend `POST /cases/{case_id}/dispute-strategy/prepare` to create accounts and dispute letter drafts for strategy targets that lack cross-bureau `match_keys` (Metro 2/FCRA-only findings), while keeping the discrepancy prepare path for match-keyed accounts.

**Reason:** Investigators were blocked from acting on strong single-bureau findings that never appear in the cross-bureau discrepancy list.

**Alternatives considered:** Require manual account import first; only prepare cross-bureau items.

**Technical debt:** Direct-created accounts infer type/status from rule IDs; may still fall back to unknown when rules lack status tokens.

**Follow-up work:** Map bureau/status from findings; CFPB packet checklist export.

## Compliance intelligence — strategy stage letter prep

**Decision:** Add `POST /cases/{case_id}/dispute-strategy/prepare` to create CRA/furnisher dispute letter drafts from recommended strategy accounts that have cross-bureau `match_keys`.

**Reason:** Phase 7 plans needed an actionable handoff into the existing prepare-disputes workflow without auto-filing.

**Alternatives considered:** Always open generic letters; LLM freeform drafting per stage.

**Technical debt:** Metro 2/FCRA-only accounts without match keys cannot prepare via this path yet.

**Follow-up work:** Account creation from non-discrepancy strategy issues; CFPB packet checklist export.

## Compliance intelligence — evidence PDF page scan

**Decision:** Wire `locate_tradeline_pages()` into `GET /cases/{case_id}/compliance-evidence-links` with per-request PDF and lookup caches. Dispute strategy continues to call evidence links with `include_page_scan=False` so planning stays lightweight.

**Reason:** Phase 5 deferred live page maps; investigators need page pointers on report evidence links.

**Alternatives considered:** Always defer pages; persist OCR page maps; require a separate endpoint.

**Technical debt:** Text-match page scan is heuristic; empty matches mark `unavailable` rather than `deferred`.

**Follow-up work:** Persist page maps; OCR line refs; optional query flag to skip scan on large cases.

## Compliance intelligence — dispute strategy generator

**Decision:** Add `GET /cases/{case_id}/dispute-strategy` that groups litigation-strength ranked issues by account and emits a deterministic four-stage plan (CRA dispute → furnisher → CFPB if warranted → attorney preserve). Reuses evidence checklist hints when available.

**Reason:** Phase 7 of the Consumer Credit Litigation Intelligence stack needs a tailored multi-stage plan, not a single generic letter.

**Alternatives considered:** LLM-generated freeform strategy; auto-creating dispute letter drafts per stage.

**Technical debt:** Stage thresholds are heuristic; CFPB/attorney gates are score-based only.

**Follow-up work:** Optional PDF page maps; persist strategy runs; wire stage actions into dispute letter prep.

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

## Version 4.8 — Client and contact model

### Decision: First-class Client aggregate with nested contacts

**Decision:** Add `clients` and `client_contacts` tables with staff CRUD API (`/clients`, `/clients/{id}/contacts`). Cases retain inline `client_name` / `client_email` for backward compatibility; optional `client_id` FK deferred.

**Reason:** Client portal auth (slice 7) requires a durable client identity separate from case denormalized fields.

**Follow-up work:** Link cases to clients, read-only progress view (slice 11).

## Version 4.8 — Client portal auth partition

### Decision: Separate JWT realm for portal users

**Decision:** Add `client_portal_users` table, `/portal/auth/*` endpoints, and JWT `realm=portal` claims. Staff provisions portal credentials via `/clients/{id}/portal-user`. Feature-flagged with `ENABLE_CLIENT_PORTAL`.

**Reason:** Portal users must not share staff RBAC tokens or access staff APIs.

**Follow-up work:** Client portal case progress view (slice 11), dedicated portal token storage in web app.

## Version 4.8 — LLM provider policy and gates

### Decision: `ENABLE_LLM` + `packages/llm-gateway/` before external calls

**Decision:** Add ADR-012, `verdin-llm-gateway` package with provider config, PII scrubbing, and `require_llm_ready()` gate. Separate `ENABLE_LLM` from heuristic `ENABLE_AI`. Expose `GET /llm/status` for staff readiness checks.

**Reason:** 4.5 deferred all LLM work pending compliance gates; implementation slices must not call providers without policy merged.

**Follow-up work:** Actual LLM summary endpoints and worker integration behind gate.

## Version 4.8 — Email delivery scaffold (feature-flagged)

### Decision: Add non-sending readiness gate before provider integration

**Decision:** Add `ENABLE_EMAIL_DELIVERY`, email provider config env vars, and `GET /notifications/email/status` to report readiness (`enabled`, `ready`, provider metadata, blockers). No external provider calls are executed in this slice.

**Reason:** Notifications epic requires an email/SMS scaffold in 4.8, but production delivery wiring needs a later slice and provider selection.

**Follow-up work:** Implement provider adapters (`smtp` / `sendgrid`), enqueue delivery attempts from notification workflows, and add retry/metrics via `job-orchestrator`.

## Version 4.8 — Operations reporting read model

### Decision: Dedicated reporting endpoint + dashboard embedding

**Decision:** Add `GET /reporting/operations` with org-scoped aggregates for clients, dispute account/letter status counts, and notification backlog. Embed the same read model in `GET /dashboard` as an `operations` section.

**Reason:** 4.8 reporting epic needs read-optimized operational KPIs without bloating the core Mission Control aggregation queries.

**Follow-up work:** Materialized views or read replicas if aggregate latency exceeds dashboard targets; bureau performance and revenue metrics deferred to 5.0.

## Version 4.8 — Client portal case progress view

### Decision: Read-only portal case endpoints with interim case matching

**Decision:** Add `GET /portal/cases` and `GET /portal/cases/{id}` for portal JWT users, plus a minimal client portal UI (`/portal/login`, `/portal`, `/portal/cases/:id`). Cases match the portal client via email/name heuristics until optional `cases.client_id` linking ships.

**Reason:** 4.8 client experience epic requires read-only progress without exposing staff APIs or internal notes.

**Follow-up work:** Add `client_id` FK on cases, dedicated portal token storage isolation from staff session, secure messaging.

## Version 4.8.0 — Operations release sign-off

### Decision: Partial epic delivery with explicit deferrals to 5.0

**Decision:** Ship `v4.8.0` with all five Operations epics marked **Partial** and documented limits in scope doc, capability matrix epic sign-off table, and release notes. LLM summary endpoints and production email/SMS delivery remain deferred post-gate.

**Reason:** 4.8 delivers operational foundations (notifications, portal, reporting, workflow jobs, LLM policy) without over-promising enterprise or compliance features.

**Documentation:** [`docs/governance/version-4.8-scope.md`](../governance/version-4.8-scope.md), [`docs/release-notes/v4.8.0.md`](../release-notes/v4.8.0.md)

## Version 5.0.0 — Enterprise kickoff

### Decision: Formal scope and ordered checklist before implementation slices

**Decision:** Publish `version-5.0-scope.md`, `version-5.0-completion-checklist.md`, capability matrix 5.0 planned rows, and Version 5.0 sprint loop rule. First implementation slice is `cases.client_id` linking.

**Reason:** 4.8 deferred enterprise identity, compliance, production comms, and post-gate LLM work to 5.0; kickoff docs are the source of truth for slice order.

**Follow-up work:** Slice 2 — Alembic migration + API for case–client FK.

### Decision: Optional `cases.client_id` FK with portal FK-first matching

**Decision:** Add nullable `cases.client_id` FK to `clients`, staff create/update/list support with org-scoped validation, and portal case queries that match on FK first with email/name heuristics as fallback for unlinked cases.

**Reason:** Durable case–client relationships replace fragile heuristic-only portal matching while preserving backward compatibility for legacy inline client fields.

**Follow-up work:** Slice 3 — production email delivery adapters.

### Decision: Production email delivery with SMTP/SendGrid adapters and audit trail

**Decision:** Wire `smtp` and `sendgrid` provider adapters behind `ENABLE_EMAIL_DELIVERY`, persist `email_delivery_logs`, expose `POST /notifications/email/send` and `GET /notifications/email/deliveries`, and add optional `deliver_email` on notification create.

**Reason:** Communications epic requires production email beyond the 4.8 readiness scaffold, with auditable sends for compliance and workflow integration.

**Follow-up work:** Slice 4 — LLM case summary endpoint (post-gate).

### Decision: Post-gate LLM case summary endpoint with PII scrubbing and audit trail

**Decision:** Add `verdin_llm_gateway` completion clients (OpenAI-compatible, Anthropic), `POST /cases/{case_id}/llm-summary` for case managers, scrubbed context via `scrub_payload()`, and timeline event `CASE_LLM_SUMMARY_GENERATED` with model and prompt hash metadata.

**Reason:** 5.0 AI epic requires at least one staff-authenticated LLM endpoint after ADR-012 gates; case summaries are the highest-value first surface.

**Follow-up work:** Slice 5 — job orchestrator runner wiring + overdue cron.

### Decision: Wire job orchestrator retry/metrics and in-process overdue scan cron

**Decision:** Implement cron evaluation in `JobScheduler` (croniter), wire `RetryPolicy` and `JobMetricsRecorder` into `worker/orchestrator.py`, and register `overdue_investigation_scan` at `0 6 * * *` UTC with in-process scheduler ticks.

**Reason:** 4.8 deferred runner integration; 5.0 platform slice requires schedulable overdue scan without external cron-only wiring.

**Follow-up work:** Slice 6 — MFA / SSO foundation (feature-flagged).

### Decision: Enterprise identity readiness scaffold behind `ENABLE_ENTERPRISE`

**Decision:** Add `enterprise_identity` settings/gates, `GET /enterprise/status` for SSO (`oidc`/`saml`) and MFA (`totp`) readiness, and `@verdin/api-client` types. Staff and portal auth partitions remain separate.

**Reason:** Enterprise identity epic requires a compliance gate before IdP or TOTP enrollment endpoints ship in later slices.

**Follow-up work:** Slice 7 — compliance center scaffold + consent model.

### Decision: Compliance center scaffold with consent records and retention placeholders

**Decision:** Add `consent_records` and `retention_policies` tables (migration `017`), compliance module with org-scoped consent CRUD + withdrawal, retention policy placeholders (admin), `GET /compliance/status`, and `@verdin/api-client` compliance functions.

**Reason:** Compliance epic requires durable consent history and retention policy foundations before legal sign-off or enforcement workflows ship in later versions.

**Follow-up work:** Slice 8 — portal document upload.

### Decision: Portal document upload scoped to linked cases

**Decision:** Add `POST /portal/cases/{case_id}/documents` and `GET /portal/cases/{case_id}/documents` for portal JWT users, reuse document storage/OCR pipeline, emit `PORTAL_DOCUMENT_UPLOADED` timeline events, and expose `@verdin/api-client` upload helpers.

**Reason:** Client portal epic requires clients to submit evidence on linked cases without staff mediation; uploads remain org-scoped with the same case visibility rules as read-only progress.

**Follow-up work:** Slice 9 — portal secure messaging scaffold.

### Decision: Secure messaging thread scaffold for portal and staff

**Decision:** Add `message_threads` and `thread_messages` tables (migration `018`), one thread per case, portal `GET/POST /portal/cases/{case_id}/messages`, staff `GET/POST /cases/{case_id}/message-thread`, timeline events for portal and staff messages, and `@verdin/api-client` messaging helpers.

**Reason:** Client portal epic requires a durable messaging foundation on linked cases before real-time delivery or attachments ship in later versions.

**Follow-up work:** Slice 10 — enterprise reporting read models.

### Decision: Enterprise bureau performance and team productivity read models

**Decision:** Add `GET /reporting/bureau-performance` and `GET /reporting/team-productivity` org-scoped aggregate endpoints, `GET /reporting/status` capabilities overview, and `@verdin/api-client` reporting helpers.

**Reason:** Reporting epic requires enterprise dashboards beyond 4.8 operations KPIs without materialized views or revenue pipelines in this slice.

**Follow-up work:** Slice 11 — API keys + org admin scaffold.

### Decision: Organization admin scaffold with API key lifecycle

**Decision:** Add `organization_api_keys` table (migration `019`), org-admin module with `GET /org-admin/status`, organization summary, API key create/list/get/revoke endpoints, SHA-256 hashed key storage with `vrd_live_` prefix, and `@verdin/api-client` org-admin helpers. Gated behind `ENABLE_ENTERPRISE`; admin role required.

**Reason:** Enterprise admin epic requires durable API key foundations before SCIM, billing admin, or key-authenticated integrations ship in later versions.

**Follow-up work:** Slice 12 — capability matrix 5.0 sign-off + deferrals.

### Decision: Version 5.0 epic sign-off with explicit deferrals to 5.0+ / 5.1+

**Decision:** Mark all nine Version 5.0 epics **Partial ✅** in `version-5.0-scope.md`, add capability matrix epic sign-off table, document deferred AI workflow orchestration and predictive outcomes in the AI tracker, and update roadmap with v5.0.0 RC outcomes.

**Reason:** Governance slice closes the 5.0 implementation track before release notes and tag; all promised capabilities are either shipped (partial) or explicitly deferred with written limits.

**Documentation:** [`docs/governance/version-5.0-scope.md`](../governance/version-5.0-scope.md), [`docs/governance/capability-matrix.md`](../governance/capability-matrix.md)

**Follow-up work:** Slice 13 — `docs/release-notes/v5.0.0.md`.

### Decision: Publish Version 5.0.0 release notes

**Decision:** Add `docs/release-notes/v5.0.0.md` covering all nine partial epics, feature flags, migrations 015–019, deferrals, and update capability matrix, roadmap, and governance release history.

**Reason:** Release notes are the user-facing summary of the Enterprise Edition RC before the `v5.0.0` git tag.

**Documentation:** [`docs/release-notes/v5.0.0.md`](../release-notes/v5.0.0.md)

**Follow-up work:** Slice 14 — tag `v5.0.0`.

### Decision: Tag `v5.0.0` — Enterprise Edition release

**Decision:** Mark Version 5.0 completion checklist complete and tag `v5.0.0` on `main` with GitHub Release notes sourced from `docs/release-notes/v5.0.0.md`.

**Reason:** Closes the Version 5.0 sprint loop; all nine epics ship as Partial with documented deferrals.

**Documentation:** [`docs/release-notes/v5.0.0.md`](../release-notes/v5.0.0.md), [`docs/development/version-5.0-completion-checklist.md`](../development/version-5.0-completion-checklist.md)

## Version 5.0+ — Product Hardening kickoff

### Decision: Pilot UI checklist after v5.0.0 tag

**Decision:** Publish `version-5.0-plus-scope.md`, `version-5.0-plus-completion-checklist.md`, and Version 5.0+ sprint loop. First implementation slices: web `predev` api-client build and staff client management UI.

**Reason:** v5.0 shipped enterprise APIs without staff UI for clients, compliance, reporting, and org admin; pilot readiness requires product surfaces before 5.1 enterprise hardening.

**Follow-up work:** Slice 4 — case form `client_id` picker.

### Decision: Case form client picker for durable case–client linking

**Decision:** Extend `createCaseSchema` with optional `client_id`, add `ClientPicker` on case create/edit forms, auto-fill client name/email from linked records, and show client profile link on case detail.

**Reason:** 5.0+ pilot requires staff to link cases to client records without API calls; portal matching prefers FK when set.

**Follow-up work:** Slice 5 — portal document upload UI.

### Decision: Portal document upload UI on case detail

**Decision:** Add `PortalCaseDocuments` on portal case detail with document list and multipart upload form using existing portal document API helpers.

**Reason:** 5.0+ pilot requires clients to submit evidence without staff mediation; backend upload endpoints shipped in v5.0.0.

**Follow-up work:** Slice 6 — portal secure messaging UI.

### Decision: Portal secure messaging UI on case detail

**Decision:** Add `PortalCaseMessages` on portal case detail with thread history and send form using portal messaging API helpers.

**Reason:** 5.0+ pilot requires clients to communicate with staff on linked cases without email; backend messaging scaffold shipped in v5.0.0.

**Follow-up work:** Slice 7 — staff case messaging UI.

### Decision: Staff case messaging UI on case detail

**Decision:** Add `CaseMessageThreadPanel` on staff case detail with thread history and reply form using staff messaging API helpers, gated by `VITE_ENABLE_CLIENT_PORTAL`.

**Reason:** 5.0+ pilot requires staff to respond to portal clients without leaving the case workspace.

**Follow-up work:** Slice 8 — compliance center staff UI.

### Decision: Compliance center staff UI

**Decision:** Add `/compliance` page with consent record list/create/withdraw and retention policy list/create, gated by `VITE_ENABLE_ENTERPRISE`.

**Reason:** 5.0+ pilot requires staff to manage compliance artifacts without API calls; backend compliance center shipped in v5.0.0.

**Follow-up work:** Slice 9 — enterprise reporting staff UI.

### Decision: Enterprise reporting staff UI

**Decision:** Add `/reporting` page with operations, bureau performance, and team productivity tabs using enterprise reporting API helpers, gated by `VITE_ENABLE_ENTERPRISE`.

**Reason:** 5.0+ pilot requires staff to access bureau and team read models without API calls; backend reporting shipped in v5.0.0.

**Follow-up work:** Slice 10 — org admin staff UI.

### Decision: Org admin staff UI

**Decision:** Add `/org-admin` page with organization summary, API key list/create/revoke, and one-time secret display; fix api-client create key body serialization.

**Reason:** 5.0+ pilot requires admins to manage API keys without CLI; backend org admin shipped in v5.0.0.

**Follow-up work:** Slice 11 — LLM case summary UI.

### Decision: LLM case summary UI on case detail

**Decision:** Add `CaseLlmSummaryPanel` on staff case detail with LLM readiness check and generate action using `POST /cases/{id}/llm-summary`, gated by `VITE_ENABLE_LLM`.

**Reason:** 5.0+ pilot requires staff to trigger gated case summaries from the case workspace without API calls.

**Follow-up work:** Slice 12 — capability matrix 5.0+ sign-off.

### Decision: Version 5.0+ pilot sign-off

**Decision:** Mark all eight 5.0+ epics **Partial ✅** in scope doc, add capability matrix 5.0+ epic sign-off table, complete checklist exit criteria, and update roadmap to pilot-ready status.

**Reason:** All twelve 5.0+ UI slices shipped; pilot can run staff and portal workflows behind feature flags without API-only gaps.

**Follow-up work:** 5.1+ planning — billing, IdP enrollment, API key middleware, autonomous agents per deferrals table.

### Decision: Kick off Version 5.1 production hardening

**Decision:** Add `version-5.1-scope.md`, `version-5.1-completion-checklist.md`, and `.cursor/rules/version-51-sprint-loop.mdc`; link 5.1 from product roadmap.

**Reason:** 5.0+ pilot sign-off complete; deferred production integrations need a sequenced delivery path before v5.1.0 release.

**Follow-up work:** Slice 2 — API key auth middleware.

### Decision: API key auth middleware on reporting operations

**Decision:** Add `ApiKeyAuthService` with prefix/hash validation, scope checks, and `last_used_at` audit; wire `GET /reporting/operations` to accept `X-API-Key` or `Authorization: Bearer vrd_live_…` alongside staff JWT. Gated behind `ENABLE_ENTERPRISE`.

**Reason:** 5.1 requires at least one production integration path authenticated by organization API keys before billing and external automation expand.

**Follow-up work:** Slice 3 — production SMS delivery.

### Decision: IdP and TOTP staff enrollment

**Decision:** Add TOTP enrollment (`/enterprise/mfa/totp/*`) with encrypted secret storage and OIDC account linking (`/enterprise/sso/enrollment/*`) with signed state tokens, `user_totp_enrollments` and `user_sso_enrollments` tables, and `@verdin/api-client` enrollment helpers. Gated behind `ENABLE_ENTERPRISE`.

**Reason:** 5.1 identity epic requires staff enrollment beyond the v5.0 readiness scaffold before SCIM or multi-IdP federation.

**Follow-up work:** Slice 5 — Stripe billing scaffold.

### Decision: Stripe billing scaffold

**Decision:** Add `organization_billing_accounts` and `billing_webhook_events` tables, Stripe customer/subscription helpers, admin billing setup/subscribe endpoints, webhook handler at `POST /billing/webhooks/stripe`, and embedded `billing` on `GET /org-admin/organization`. Gated by `ENABLE_BILLING`.

**Reason:** 5.1 billing epic requires a durable Stripe integration foundation before usage metering or invoicing ships in later versions.

**Follow-up work:** Slice 6 — compliance enforcement jobs.

### Decision: Compliance retention enforcement jobs

**Decision:** Add `retention_enforcement_runs` audit table, admin compliance endpoints (`GET /compliance/enforcement/status`, `GET /compliance/enforcement/runs`, `POST /compliance/enforcement/run`), worker job `retention_enforcement_scan` (`0 3 * * *` UTC), and soft-delete enforcement for `documents`, `communications`, and `client_profiles` scopes. `audit_logs` scope records `skipped` runs until append-only purge is implemented. Gated by `ENABLE_COMPLIANCE_ENFORCEMENT`.

**Reason:** 5.1 compliance epic requires executable retention enforcement with auditability beyond v5.0 policy placeholders.

**Follow-up work:** Slice 8 — portal push notification scaffold.

### Decision: Portal push notification scaffold

**Decision:** Add `portal_push_subscriptions` and `portal_push_delivery_logs` tables, portal endpoints (`GET /portal/push/status`, `POST /portal/push/subscribe`, `DELETE /portal/push/subscriptions/{id}`), Web Push provider scaffold in `api/core/portal_push.py`, staff-message dispatch hook, `PortalPushPanel` UI, and `@verdin/api-client` helpers. Gated by `ENABLE_PORTAL_PUSH`.

**Reason:** 5.1 portal real-time epic requires auditable push delivery for secure messaging beyond polling-only portal UX.

**Follow-up work:** Slice 9 — reporting materialized views.

### Decision: Reporting materialized views

**Decision:** Add PostgreSQL materialized views (`mv_bureau_account_counts`, `mv_bureau_sent_letter_counts`, `mv_team_member_productivity`), `reporting_mv_refresh_runs` audit table, admin refresh endpoints (`GET/POST /reporting/materialized-views/*`), worker job `reporting_mv_refresh` (`0 4 * * *` UTC), and bureau/team read paths that use MVs when `ENABLE_MATERIALIZED_REPORTING=true`.

**Reason:** 5.1 reporting epic requires read-optimized bureau and team aggregates without live-query latency on every dashboard load.

**Follow-up work:** Slice 10 — capability matrix 5.1 sign-off.

### Decision: Version 5.1 epic sign-off

**Decision:** Mark six Version 5.1 epics **Partial ✅** in `version-5.1-scope.md`, defer **Communications production** (SMS) and **LLM expansion** (document summary UI) to 5.2+, add capability matrix 5.1 epic sign-off table, and complete checklist Phase 1 exit criteria.

**Reason:** All ten recommended 5.1 implementation slices are shipped or explicitly deferred; governance docs reflect production-hardening outcomes.

**Follow-up work:** `docs/release-notes/v5.1.0.md` + tag `v5.1.0`.

### Decision: Version 5.1.0 release notes

**Decision:** Publish `docs/release-notes/v5.1.0.md`, mark Version 5.1 checklist complete, update roadmap to **Shipped** (`v5.1.0`), and tag `v5.1.0` on `main`.

**Reason:** Final exit criterion for the 5.1 production-hardening milestone.

**Follow-up work:** 5.2 kickoff — deferred SMS, LLM document summaries, Web Push HTTP.

### Decision: Kick off Version 5.2 deferred production surfaces

**Decision:** Add `version-5.2-scope.md`, `version-5.2-completion-checklist.md`, and `.cursor/rules/version-52-sprint-loop.mdc`; link 5.2 from product roadmap.

**Reason:** v5.1.0 sign-off complete; SMS, LLM document summaries, and portal push production depth need a sequenced delivery path before v5.2.0 release.

**Follow-up work:** Slice 2 — production SMS delivery.

### Decision: Production SMS delivery

**Decision:** Add Twilio SMS provider adapter, `sms_delivery_logs` audit table, optional `users.phone_number`, and notification endpoints `GET /notifications/sms/status`, `POST /notifications/sms/send`, `GET /notifications/sms/deliveries` gated by `ENABLE_SMS_DELIVERY`.

**Reason:** 5.2 communications epic ships production SMS deferred from v5.1.0 alongside existing email delivery for staff notification workflows.

**Follow-up work:** Slice 3 — LLM document summary UI.

### Decision: LLM document summary UI

**Decision:** Add `POST /documents/{document_id}/llm-summary` with PII-scrubbed document context, timeline event `DOCUMENT_LLM_SUMMARY_GENERATED`, `DocumentLlmSummaryPanel` on staff document detail, and `@verdin/api-client` helpers. Gated by `ENABLE_LLM`.

**Reason:** 5.2 AI epic ships document summaries deferred from v5.1.0 alongside existing case summary UI from 5.0.

**Follow-up work:** Slice 4 — Web Push HTTP delivery.

### Decision: Web Push HTTP delivery

**Decision:** Replace scaffold `WebPushPortalPushAdapter` with real VAPID Web Push HTTP sends via `pywebpush`; staff-message dispatch records `sent`/`failed` in `portal_push_delivery_logs`. Messaging capability updated to `portal_web_push`.

**Reason:** 5.2 portal push epic ships production HTTP delivery deferred from v5.1 scaffold when VAPID keys are configured.

**Follow-up work:** Slice 5 — revenue analytics scaffold.

### Decision: Revenue analytics scaffold

**Decision:** Add `GET /reporting/revenue` with billing-derived readiness metrics (subscription state, client/portal counts, heuristic readiness score), `api/core/revenue_analytics.py`, Revenue readiness tab on enterprise reporting UI, and promote `revenue_metrics` to enterprise reporting capabilities when `ENABLE_BILLING=true`.

**Reason:** 5.2 revenue epic ships an org-scoped read model from Stripe billing account state without usage metering or cross-org benchmarks.

**Follow-up work:** Slice 6 — API key rate-limit scaffold.

### Decision: API key rate-limit scaffold

**Decision:** Add Redis fixed-window rate limiting for API key auth on `GET /reporting/operations`, `ENABLE_API_KEY_RATE_LIMIT` flag, `GET /org-admin/api-keys/rate-limit/status`, and promote `api_key_rate_limiting` to org admin capabilities when enabled.

**Reason:** 5.2 API integrations epic ships per-organization rate limits on the production API key path without per-route limit UI.

**Follow-up work:** Slice 7 — capability matrix 5.2 sign-off.

### Decision: Version 5.2 epic sign-off

**Decision:** Mark all five Version 5.2 epics **Partial ✅** in `version-5.2-scope.md`, add capability matrix 5.2 epic sign-off table, update AI tracker for document summaries, and complete checklist Phase 1 exit criteria.

**Reason:** All 5.2 slices shipped behind feature flags with tests and docs; deferrals documented for 5.3+.

**Follow-up work:** `docs/release-notes/v5.2.0.md` + tag `v5.2.0`.

### Decision: Version 5.2.0 release notes

**Decision:** Publish `docs/release-notes/v5.2.0.md`, mark Version 5.2 checklist complete, update roadmap to **Shipped** (`v5.2.0`), and tag `v5.2.0` on `main`.

**Reason:** Final exit criterion for the 5.2 deferred production surfaces milestone.

**Follow-up work:** 5.3+ planning — SCIM, usage metering, predictive analytics.

### Decision: Kick off Version 5.3 enterprise depth

**Decision:** Add `version-5.3-scope.md`, `version-5.3-completion-checklist.md`, and `.cursor/rules/version-53-sprint-loop.mdc`; link 5.3 from product roadmap.

**Reason:** v5.2.0 sign-off complete; usage metering, SCIM, predictive analytics, and API developer surfaces need a sequenced delivery path before v5.3.0 release.

**Follow-up work:** Slice 2 — billing usage metering scaffold.

### Decision: Billing usage metering scaffold

**Decision:** Add `billing_usage_events` table (migration `027`), `GET /billing/usage/summary` and `POST /billing/usage/events`, `api/core/usage_metering.py`, `ENABLE_BILLING_USAGE_METERING` flag, and promote `billing_usage_metering` to org admin capabilities when enabled.

**Reason:** 5.3 billing epic ships org-scoped usage event recording and aggregated read model without Stripe metered billing or invoicing.

**Follow-up work:** Slice 3 — SCIM provisioning scaffold.

### Decision: SCIM provisioning scaffold

**Decision:** Add `scim_provision_logs` table (migration `028`), `GET /enterprise/scim/status` and SCIM 2.0 `Users`/`Groups` provision/list endpoints, `api/core/scim_provisioning.py`, `ENABLE_SCIM_PROVISIONING` flag, and promote `scim_provisioning` to org admin capabilities when enabled.

**Reason:** 5.3 identity epic ships org-scoped SCIM provision audit logs and readiness gate aligned with OIDC enrollment without full IdP lifecycle sync.

**Follow-up work:** Slice 4 — predictive analytics scaffold.

### Decision: Predictive analytics scaffold

**Decision:** Add `predictive_outcome_snapshots` and `predictive_outcome_refresh_runs` tables (migration `029`), `GET /reporting/predictive/status`, `GET /reporting/predictive/outcomes`, and `POST /reporting/predictive/refresh`, `api/core/predictive_analytics.py`, `ENABLE_PREDICTIVE_ANALYTICS` flag, and promote `predictive_outcomes` to enterprise reporting capabilities when enabled.

**Reason:** 5.3 reporting epic ships org-scoped historical outcome aggregates with snapshot refresh scaffold without cross-org benchmarks or model serving.

**Follow-up work:** Slice 5 — API key rotation + dev portal.

### Decision: API developer portal and key rotation

**Decision:** Add `api_key_rotation_logs` table (migration `030`), `GET /org-admin/developer-portal` and `POST /org-admin/api-keys/{id}/rotate`, `api/core/api_developer_portal.py`, `ENABLE_API_DEVELOPER_PORTAL` flag, org admin UI developer portal card, and promote `api_key_rotation` + `developer_portal` capabilities when enabled.

**Reason:** 5.3 API integrations epic ships internal developer portal scaffold and rotation workflow without public external portal or OAuth client credentials.

**Follow-up work:** Slice 6 — batch document summarization job.

### Decision: Batch document LLM summarization job

**Decision:** Add `batch_document_summary_runs` table (migration `031`), `GET/POST /documents/batch-llm-summaries/*` endpoints, `batch_document_llm_summary` worker job (`JobType.BATCH_DOCUMENT_LLM_SUMMARY`), `api/core/batch_llm_summaries.py`, and `ENABLE_BATCH_LLM_SUMMARIES` flag.

**Reason:** 5.3 LLM operations epic ships org-scoped batch summarization enqueue + worker processing with PII scrubbing and timeline audit without autonomous agents or external batch export.

**Follow-up work:** Slice 7 — capability matrix 5.3 sign-off.

### Decision: Version 5.3 epic sign-off

**Decision:** Mark all five Version 5.3 epics **Partial ✅** in `version-5.3-scope.md`, add capability matrix 5.3 epic sign-off table, update AI tracker for predictive outcomes and batch document summaries, and complete checklist Phase 1 exit criteria.

**Reason:** All 5.3 slices shipped behind feature flags with tests and docs; deferrals documented for 5.4+.

**Follow-up work:** `docs/release-notes/v5.3.0.md` + tag `v5.3.0`.

### Decision: Version 5.3.0 release notes

**Decision:** Publish `docs/release-notes/v5.3.0.md`, mark Version 5.3 checklist complete, update roadmap to **Shipped** (`v5.3.0`), and tag `v5.3.0` on `main`.

**Reason:** Final exit criterion for the 5.3 enterprise depth milestone.

**Follow-up work:** 5.4+ planning — autonomous workflows, invoicing, multi-IdP federation.

### Decision: Kick off Version 5.4 production operations

**Decision:** Add `version-5.4-scope.md`, `version-5.4-completion-checklist.md`, and `.cursor/rules/version-54-sprint-loop.mdc`; link 5.4 from product roadmap and capability matrix.

**Reason:** v5.3.0 sign-off complete; invoicing/dunning, multi-IdP federation, marketing SMS, and agent observability need a sequenced delivery path before v5.4.0 release.

**Follow-up work:** Slice 2 — invoicing & dunning scaffold.

### Decision: Billing invoicing and dunning scaffold

**Decision:** Add `billing_invoicing_runs` table (migration `032`), `GET /billing/invoicing/status`, `GET /billing/invoicing/runs`, and `POST /billing/invoicing/run`, `api/core/billing_invoicing.py`, `ENABLE_BILLING_INVOICING` flag, and promote `billing_invoicing` to org admin capabilities when enabled.

**Reason:** 5.4 billing epic ships org-scoped invoice/dunning run audit scaffold without Stripe invoice PDF generation or payment collection automation.

**Follow-up work:** Slice 3 — multi-IdP federation scaffold.

### Decision: Multi-IdP federation scaffold

**Decision:** Add `idp_federation_providers` table (migration `033`), `GET /enterprise/federation/status`, `GET /enterprise/federation/providers`, and `POST /enterprise/federation/providers`, `api/core/idp_federation.py`, `ENABLE_IDP_FEDERATION` flag, and promote `idp_federation` to org admin capabilities when enabled.

**Reason:** 5.4 identity epic ships org-scoped multi-IdP provider registry aligned with SCIM provision audit without SAML metadata upload or HRIS sync.

**Follow-up work:** Slice 4 — marketing SMS campaigns scaffold.

### Decision: Marketing SMS campaigns scaffold

**Decision:** Add `sms_marketing_campaign_runs` table (migration `034`), `GET /notifications/sms-campaigns/status`, `GET /notifications/sms-campaigns/runs`, and `POST /notifications/sms-campaigns/run`, `api/core/sms_marketing.py`, `ENABLE_SMS_MARKETING_CAMPAIGNS` flag (requires `ENABLE_SMS_DELIVERY`), and synchronous enqueue processor with org-scoped run audit.

**Reason:** 5.4 communications epic ships marketing SMS campaign enqueue scaffold without Twilio bulk send or opt-out compliance automation.

**Follow-up work:** Slice 5 — agent observability scaffold.

### Decision: Agent observability scaffold

**Decision:** Add `agent_observability_runs` table (migration `035`), `GET /llm/agents/status`, `GET /llm/agents/runs`, and `POST /llm/agents/run`, `api/core/agent_observability.py`, `ENABLE_AGENT_OBSERVABILITY` flag (requires `ENABLE_AI`), and timeline event correlation for case-scoped runs.

**Reason:** 5.4 AI operations epic ships agent run audit and staff review reads without autonomous execution or external LLM calls.

**Follow-up work:** Slice 6 — v5.4.0 sign-off and release notes.

### Decision: Version 5.4 epic sign-off

**Decision:** Mark all four Version 5.4 epics **Partial ✅** in `version-5.4-scope.md`, add capability matrix 5.4 epic sign-off table, update AI tracker for agent observability, and complete checklist Phase 1 exit criteria.

**Reason:** All 5.4 slices shipped behind feature flags with tests and docs; deferrals documented for 5.5+.

**Follow-up work:** `docs/release-notes/v5.4.0.md` + tag `v5.4.0`.

### Decision: Version 5.4.0 release notes

**Decision:** Publish `docs/release-notes/v5.4.0.md`, mark Version 5.4 checklist complete, update roadmap to **Shipped** (`v5.4.0`), and tag `v5.4.0` on `main`.

**Reason:** Final exit criterion for the 5.4 production operations milestone.

**Follow-up work:** 5.5+ planning — autonomous workflows, production invoicing automation, deeper identity federation.

### Decision: Kick off Version 5.5 production automation

**Decision:** Add `version-5.5-scope.md`, `version-5.5-completion-checklist.md`, and `.cursor/rules/version-55-sprint-loop.mdc`; link 5.5 from product roadmap and capability matrix.

**Reason:** v5.4.0 sign-off complete; invoice collection, SAML metadata, marketing SMS delivery worker, and human-gated agent execution need a sequenced delivery path before v5.5.0 release.

**Follow-up work:** Slice 2 — invoice collection scaffold.

### Decision: Billing invoice collection scaffold

**Decision:** Add `billing_invoice_collection_runs` table (migration `036`), `GET /billing/collection/status`, `GET /billing/collection/runs`, and `POST /billing/collection/run`, `api/core/billing_invoice_collection.py`, `ENABLE_BILLING_INVOICE_COLLECTION` flag (requires `ENABLE_BILLING_INVOICING`), and synchronous collection processor with org-scoped run audit.

**Reason:** 5.5 billing epic ships invoice PDF and payment reminder collection scaffold without Stripe API calls or tax calculation.

**Follow-up work:** Slice 3 — SAML metadata upload scaffold.

### Decision: SAML federation metadata upload scaffold

**Decision:** Add `saml_federation_metadata_uploads` table (migration `037`), `GET /enterprise/federation/saml-metadata/status`, `GET /enterprise/federation/saml-metadata/uploads`, and `POST /enterprise/federation/saml-metadata/upload`, `api/core/saml_federation_metadata.py`, `ENABLE_SAML_FEDERATION_METADATA` flag (requires `ENABLE_IDP_FEDERATION`), and org-scoped metadata validation with upload audit.

**Reason:** 5.5 identity epic ships SAML metadata upload and basic XML validation without full IdP lifecycle sync or HRIS integration.

**Follow-up work:** Slice 4 — marketing SMS delivery worker.

### Decision: Marketing SMS campaign delivery worker

**Decision:** Add `sms_marketing_campaign_delivery` worker job, `ENABLE_SMS_MARKETING_DELIVERY` flag (requires `ENABLE_SMS_MARKETING_CAMPAIGNS`), pending campaign runs with Redis enqueue, Twilio delivery from worker, and `campaign_run_id` on `sms_delivery_logs` (migration `038`).

**Reason:** 5.5 communications epic moves marketing SMS from audit-only enqueue to worker-driven Twilio delivery with org-scoped outcome audit.

**Follow-up work:** Slice 5 — human-gated agent execution scaffold.

### Decision: Human-gated agent execution scaffold

**Decision:** Add `agent_execution_steps` table (migration `039`), `GET /llm/execution/status`, `GET /llm/execution/steps`, `POST /llm/execution/steps`, and `POST /llm/execution/steps/{id}/approve`, `api/core/agent_execution.py`, `ENABLE_AGENT_EXECUTION` flag (requires `ENABLE_AGENT_OBSERVABILITY`), and case timeline correlation on admin approval.

**Reason:** 5.5 AI operations epic ships human-gated execution audit without autonomous dispute filing or external tool calling.

**Follow-up work:** Slice 6 — v5.5.0 sign-off and release notes.

### Decision: Version 5.5 epic sign-off

**Decision:** Mark all four Version 5.5 epics **Partial ✅** in `version-5.5-scope.md`, add capability matrix 5.5 epic sign-off table, update AI tracker for agent execution, and complete checklist Phase 1 exit criteria.

**Reason:** All 5.5 slices shipped behind feature flags with tests and docs; deferrals documented for 5.6+.

**Follow-up work:** `docs/release-notes/v5.5.0.md` + tag `v5.5.0`.

### Decision: Version 5.5.0 release notes

**Decision:** Publish `docs/release-notes/v5.5.0.md`, mark Version 5.5 checklist complete, update roadmap to **Shipped** (`v5.5.0`), and tag `v5.5.0` on `main`.

**Reason:** Final exit criterion for the 5.5 production automation milestone.

**Follow-up work:** 5.6+ planning — autonomous workflows, deliverability dashboards, HRIS sync.

### Decision: Kick off Version 5.6 compliance-reviewed production depth

**Decision:** Add `version-5.6-scope.md`, `version-5.6-completion-checklist.md`, and `.cursor/rules/version-56-sprint-loop.mdc`; link 5.6 from product roadmap and capability matrix.

**Reason:** v5.5.0 sign-off complete (`v5.5.0` tagged); HRIS sync, SMS deliverability dashboards, LLM dispute draft augment, and compliance-gated dispute filing prep need a sequenced delivery path before v5.6.0 release.

**Follow-up work:** Slice 2 — HRIS bidirectional sync scaffold.

### Decision: HRIS bidirectional sync scaffold

**Decision:** Add `hris_bidirectional_sync_runs` table (migration `040`), `GET /enterprise/federation/hris-sync/status`, `GET /enterprise/federation/hris-sync/runs`, and `POST /enterprise/federation/hris-sync/run`, `api/core/hris_bidirectional_sync.py`, `ENABLE_HRIS_BIDIRECTIONAL_SYNC` flag (requires `ENABLE_SAML_FEDERATION_METADATA`), and org-scoped sync run audit with valid metadata prerequisite.

**Reason:** 5.6 identity epic ships HRIS sync run audit scaffold without full employee lifecycle sync or certificate rotation.

**Follow-up work:** Slice 3 — SMS deliverability dashboard scaffold.

### Decision: SMS deliverability dashboard scaffold

**Decision:** Add `GET /notifications/sms-campaigns/deliverability/status` and `GET /notifications/sms-campaigns/deliverability/summary`, `api/core/sms_deliverability_dashboard.py`, `ENABLE_SMS_DELIVERABILITY_DASHBOARD` flag (requires `ENABLE_SMS_MARKETING_DELIVERY`), and org-scoped delivery metrics aggregate from campaign runs and delivery logs.

**Reason:** 5.6 communications epic ships deliverability read model without multi-provider failover or real-time alerting.

**Follow-up work:** Slice 4 — LLM dispute draft augment scaffold.

### Decision: LLM dispute draft augment scaffold

**Decision:** Add `llm_dispute_draft_augments` table (migration `041`), `GET /llm/dispute-draft/status`, `GET /accounts/{account_id}/dispute-draft/llm-augments`, and `POST /accounts/{account_id}/dispute-draft/llm-augment`, `api/core/llm_dispute_draft_augment.py`, `ENABLE_LLM_DISPUTE_DRAFT_AUGMENT` flag (requires `ENABLE_LLM`), scrubbed LLM augment audit, and case timeline correlation.

**Reason:** 5.6 AI assistance epic ships ADR-012-gated dispute letter augment without auto-send or unsupervised LLM loops.

**Follow-up work:** Slice 5 — compliance-gated dispute filing prep scaffold.

### Decision: Compliance-gated dispute filing prep scaffold

**Decision:** Add `dispute_filing_prep_runs` table (migration `042`), `GET /compliance/dispute-filing/status`, `GET /compliance/dispute-filing/runs`, `POST /compliance/dispute-filing/accounts/{account_id}/prep`, and `POST /compliance/dispute-filing/runs/{run_id}/approve`, `api/core/dispute_filing_prep.py`, `ENABLE_DISPUTE_FILING_PREP` flag (requires human-gated agent execution readiness), admin approval audit, and case timeline correlation.

**Reason:** 5.6 disputes epic ships compliance-gated filing prep without autonomous bureau submission.

**Follow-up work:** Slice 6 — v5.6.0 capability matrix sign-off and release tag.

### Decision: Version 5.6 epic sign-off

**Decision:** Mark all four Version 5.6 epics **Partial ✅** in `version-5.6-scope.md`, add capability matrix 5.6 epic sign-off table, update AI tracker for LLM dispute augment and filing prep, complete checklist exit criteria, and publish `docs/release-notes/v5.6.0.md`.

**Reason:** v5.6.0 completes compliance-reviewed production depth scaffolds; autonomous bureau filing and unsupervised agent loops remain deferred to 5.7+.

**Follow-up work:** Version 5.7 planning — autonomous dispute filing and deeper agent automation (compliance-gated).

### Decision: Kick off Version 5.7 compliance-gated autonomous workflows

**Decision:** Add `version-5.7-scope.md`, `version-5.7-completion-checklist.md`, and `.cursor/rules/version-57-sprint-loop.mdc`; link 5.7 from product roadmap and capability matrix.

**Reason:** v5.6.0 sign-off complete (`v5.6.0` tagged); bureau submission, agent tool-calling, SAML cert rotation, and Stripe invoice PDF scaffolds need a sequenced delivery path before v5.7.0 release.

**Follow-up work:** Slice 2 — dispute bureau submission scaffold.

### Decision: Dispute bureau submission scaffold

**Decision:** Add `dispute_bureau_submission_runs` table (migration `043`), `GET /compliance/dispute-bureau-submission/status`, `GET .../runs`, `POST .../prep-runs/{id}/submit`, and `POST .../runs/{id}/approve`, `api/core/dispute_bureau_submission.py`, `ENABLE_DISPUTE_BUREAU_SUBMISSION` flag (requires `prepared` filing prep run), admin-gated submission audit, and case timeline correlation.

**Reason:** 5.7 disputes epic ships bureau submission run audit scaffold without unsupervised filing or live bureau API integration.

**Follow-up work:** Slice 3 — agent external tool-calling scaffold.

### Decision: Agent external tool-calling scaffold

**Decision:** Add `agent_tool_invocation_requests` table (migration `044`), `GET /llm/tool-calling/status`, `GET .../requests`, `POST .../requests`, and `POST .../requests/{id}/approve`, `api/core/agent_external_tool_calling.py`, `ENABLE_AGENT_EXTERNAL_TOOL_CALLING` flag (requires agent execution readiness), admin-gated invocation audit, and case timeline correlation.

**Reason:** 5.7 AI operations epic ships human-gated external tool invocation audit without live tool calls or unsupervised loops.

**Follow-up work:** Slice 4 — SAML certificate rotation scaffold.

### Decision: SAML certificate rotation scaffold

**Decision:** Add `saml_certificate_rotation_runs` table (migration `045`), `GET /enterprise/federation/saml-cert-rotation/status`, `GET .../runs`, `POST .../metadata-uploads/{id}/rotate`, and `POST .../runs/{id}/approve`, `api/core/saml_certificate_rotation.py`, `ENABLE_SAML_CERTIFICATE_ROTATION` flag (requires HRIS sync + SAML metadata readiness), admin-gated rotation audit scaffold.

**Reason:** 5.7 identity epic ships federation cert rotation run audit without automated IdP rotation or operator-bypass flows.

**Follow-up work:** Slice 5 — Stripe invoice PDF scaffold.

### Decision: Stripe invoice PDF scaffold

**Decision:** Add `stripe_invoice_pdf_runs` table (migration `046`), `GET /billing/invoice-pdf/status`, `GET .../runs`, `POST .../collection-runs/{id}/generate`, and `POST .../runs/{id}/approve`, `api/core/stripe_invoice_pdf.py`, `ENABLE_STRIPE_INVOICE_PDF` flag (requires invoice collection readiness), admin-gated PDF generation audit scaffold.

**Reason:** 5.7 billing epic ships Stripe invoice PDF generation run audit without live Stripe API calls or tax calculation.

**Follow-up work:** Slice 6 — capability matrix 5.7 sign-off + `v5.7.0` release.

### Decision: Version 5.7 epic sign-off

**Decision:** Mark all four Version 5.7 epics **Partial ✅** in `version-5.7-scope.md`, add capability matrix 5.7 epic sign-off table, update AI tracker for agent external tool-calling, complete checklist exit criteria, and publish `docs/release-notes/v5.7.0.md`.

**Reason:** v5.7.0 completes compliance-gated autonomous workflow scaffolds; unsupervised agent loops, live bureau filing, and Stripe tax calculation remain deferred to 5.8+.

**Follow-up work:** Version 5.8 planning — unsupervised agent loops and production integration depth (compliance-gated).

### Decision: Kick off Version 5.8 compliance-gated production integrations

**Decision:** Add `version-5.8-scope.md`, `version-5.8-completion-checklist.md`, and `.cursor/rules/version-58-sprint-loop.mdc`; link 5.8 from product roadmap and capability matrix.

**Reason:** v5.7.0 sign-off complete (`v5.7.0` tagged); supervised agent loops, bureau live API integration, Stripe tax calculation, and HRIS lifecycle sync scaffolds need a sequenced delivery path before v5.8.0 release.

**Follow-up work:** Slice 3 — bureau live API integration scaffold.

### Decision: Agent supervised loop scaffold (Version 5.8 slice 2)

**Decision:** Ship human-gated agent supervised loop audit (`agent_supervised_loop_runs` migration 047) with status, list, start-from-invoked-tool-request, and admin approve endpoints behind `ENABLE_AGENT_SUPERVISED_LOOPS`.

**Reason:** 5.8 AI operations epic extends 5.7 tool-calling with multi-step loop audit and human gates between steps without fully unsupervised loops.

**Follow-up work:** Slice 4 — Stripe tax calculation scaffold.

### Decision: Bureau live API integration scaffold (Version 5.8 slice 3)

**Decision:** Ship operator-gated bureau live API invocation audit (`bureau_live_api_runs` migration 048) with status, list, invoke-from-submitted-submission-run, and admin approve endpoints behind `ENABLE_BUREAU_LIVE_API`.

**Reason:** 5.8 disputes epic extends 5.7 bureau submission with external API invocation audit and operator gates without unsupervised filing loops.

**Follow-up work:** Slice 4 — Stripe tax calculation scaffold.

### Decision: Stripe tax calculation scaffold (Version 5.8 slice 4)

**Decision:** Ship admin-gated Stripe tax calculation audit (`stripe_tax_calculation_runs` migration 049) with status, list, calculate-from-generated-pdf-run, and admin approve endpoints behind `ENABLE_STRIPE_TAX_CALCULATION`.

**Reason:** 5.8 billing epic extends 5.7 invoice PDF with tax calculation run audit without live Stripe Tax API calls.

**Follow-up work:** Slice 5 — HRIS lifecycle sync scaffold.

### Decision: HRIS lifecycle sync scaffold (Version 5.8 slice 5)

**Decision:** Ship admin-gated HRIS lifecycle sync audit (`hris_lifecycle_sync_runs` migration 050) with status, list, start-from-completed-bidirectional-run, and admin approve endpoints behind `ENABLE_HRIS_LIFECYCLE_SYNC`.

**Reason:** 5.8 enterprise epic extends 5.6 HRIS bidirectional sync with full employee lifecycle sync run audit without passwordless enrollment UI or multi-IdP bulk provisioning.

**Follow-up work:** Slice 6 — capability matrix 5.8 sign-off + `v5.8.0` release.

### Decision: Version 5.8 epic sign-off

**Decision:** Mark all four Version 5.8 epics **Partial ✅** in `version-5.8-scope.md`, add capability matrix 5.8 epic sign-off table, update AI tracker for agent supervised loops, complete checklist exit criteria, and publish `docs/release-notes/v5.8.0.md`.

**Reason:** v5.8.0 completes compliance-gated production integration scaffolds; fully unsupervised agent loops, autonomous bureau filing, and live Stripe Tax API calls remain deferred to 5.9+.

**Follow-up work:** Version 5.9 planning — unsupervised agent loops and production integration depth (compliance-gated).

### Decision: Kick off Version 5.9 compliance-gated autonomous production

**Decision:** Add `version-5.9-scope.md`, `version-5.9-completion-checklist.md`, and `.cursor/rules/version-59-sprint-loop.mdc`; link 5.9 from product roadmap and capability matrix.

**Reason:** v5.8.0 sign-off complete (`v5.8.0` tagged); unsupervised agent loops, autonomous bureau filing, live Stripe Tax API, and SAML automated rotation scaffolds need a sequenced delivery path before v5.9.0 release.

**Follow-up work:** Slice 2 — agent unsupervised loop scaffold.

### Decision: Agent unsupervised loop scaffold (Version 5.9 slice 2)

**Decision:** Ship admin-gated agent unsupervised loop audit (`agent_unsupervised_loop_runs` migration 051) with status, list, start-from-completed-supervised-run, and admin approve endpoints behind `ENABLE_AGENT_UNSUPERVISED_LOOPS`.

**Reason:** 5.9 AI operations epic extends 5.8 supervised loops with multi-step loop audit without per-step human gates, while retaining admin approval before completion.

**Follow-up work:** Slice 3 — autonomous bureau filing scaffold.

### Decision: Autonomous bureau filing scaffold (Version 5.9 slice 3)

**Decision:** Ship admin-gated autonomous bureau filing audit (`autonomous_bureau_filing_runs` migration 052) with status, list, start-from-invoked-live-api-run, and admin approve endpoints behind `ENABLE_AUTONOMOUS_BUREAU_FILING`.

**Reason:** 5.9 disputes epic extends 5.8 bureau live API with operator-gated autonomous filing run audit without unsupervised re-filing loops.

**Follow-up work:** Slice 4 — live Stripe Tax API scaffold.

### Decision: Live Stripe Tax API scaffold (Version 5.9 slice 4)

**Decision:** Ship admin-gated Stripe live Tax API invocation audit (`stripe_live_tax_api_runs` migration 053) with status, list, start-from-calculated-tax-run, and admin approve endpoints behind `ENABLE_STRIPE_LIVE_TAX_API`.

**Reason:** 5.9 billing epic extends 5.8 tax calculation with admin-gated live Tax API invocation audit without automated charge retries.

**Follow-up work:** Slice 5 — SAML automated rotation scaffold.

### Decision: SAML automated rotation scaffold (Version 5.9 slice 5)

**Decision:** Add admin-gated SAML automated rotation run audit (`saml_automated_rotation_runs`) behind `ENABLE_SAML_AUTOMATED_ROTATION` (requires `ENABLE_SAML_CERTIFICATE_ROTATION`). Operators start automated rotation from a **rotated** SAML certificate rotation run; admin approve transitions status to `automated`.

**Reason:** 5.9 enterprise epic extends certificate rotation with operator-gated automated rotation audit without unsupervised IdP credential changes.

**Follow-up work:** Slice 6 — v5.9.0 sign-off.

### Decision: Version 5.9 epic sign-off

**Decision:** Mark all four Version 5.9 epics **Partial ✅** in `version-5.9-scope.md`, add capability matrix 5.9 epic sign-off table, complete checklist exit criteria, and publish `docs/release-notes/v5.9.0.md`.

**Reason:** v5.9.0 completes compliance-gated autonomous production scaffolds; arbitrary agent execution, unsupervised bureau re-filing, and automated charge retries remain deferred to 5.10+.

**Follow-up work:** Version 5.10 planning — production automation depth where compliance-approved.

### Decision: Kick off Version 5.10 compliance-gated production automation

**Decision:** Add `version-5.10-scope.md`, `version-5.10-completion-checklist.md`, and `.cursor/rules/version-510-sprint-loop.mdc`; link 5.10 from product roadmap and capability matrix.

**Reason:** v5.9.0 sign-off complete (`v5.9.0` tagged); arbitrary agent execution, bureau re-filing audit, Stripe charge retry, and SAML passwordless enrollment scaffolds need a sequenced delivery path before v5.10.0 release.

**Follow-up work:** Slice 2 — agent arbitrary execution scaffold.

### Decision: Agent arbitrary execution scaffold (Version 5.10 slice 2)

**Decision:** Ship admin-gated agent arbitrary execution audit (`agent_arbitrary_execution_runs` migration 055) with status, list, start-from-completed-unsupervised-run, and admin approve endpoints behind `ENABLE_AGENT_ARBITRARY_EXECUTION`.

**Reason:** 5.10 AI operations epic extends 5.9 unsupervised loops with arbitrary execution run audit without PII export or fully autonomous agents without admin approval.

**Follow-up work:** Slice 3 — bureau re-filing audit scaffold.

### Decision: Bureau re-filing audit scaffold (Version 5.10 slice 3)

**Decision:** Ship operator-gated bureau re-filing audit (`bureau_refiling_runs` migration 056) with status, list, start-from-filed-autonomous-filing-run, and admin approve endpoints behind `ENABLE_BUREAU_REFILING`.

**Reason:** 5.10 disputes epic extends 5.9 autonomous filing with operator-gated re-filing run audit without unsupervised re-filing loops.

**Follow-up work:** Slice 4 — Stripe charge retry scaffold.

### Decision: Stripe charge retry scaffold (Version 5.10 slice 4)

**Decision:** Ship admin-gated Stripe charge retry audit (`stripe_charge_retry_runs` migration 057) with status, list, submit-from-invoked-live-tax-api-run, and admin approve endpoints behind `ENABLE_STRIPE_CHARGE_RETRY`.

**Reason:** 5.10 billing epic extends 5.9 live Tax API invocation with operator-gated charge retry run audit without live charge retries.

**Follow-up work:** Slice 5 — SAML passwordless enrollment scaffold.

### Decision: SAML passwordless enrollment scaffold (Version 5.10 slice 5)

**Decision:** Ship admin-gated SAML passwordless enrollment audit (`saml_passwordless_enrollment_runs` migration 058) with status, list, enroll-from-automated-rotation-run, and admin approve endpoints behind `ENABLE_SAML_PASSWORDLESS_ENROLLMENT`.

**Reason:** 5.10 identity epic extends 5.9 SAML automated rotation with operator-gated passwordless enrollment run audit without passwordless rollout UI.

**Follow-up work:** Slice 6 — v5.10.0 sign-off and release notes.

### Decision: Version 5.10 epic sign-off

**Decision:** Mark all four Version 5.10 epics **Partial ✅** in `version-5.10-scope.md`, add capability matrix 5.10 epic sign-off table, complete checklist exit criteria, and publish `docs/release-notes/v5.10.0.md`.

**Reason:** v5.10.0 completes compliance-gated production automation scaffolds; unsupervised re-filing, live charge retries, and passwordless rollout UI remain deferred to 5.11+.

**Follow-up work:** Version 5.11 planning — production automation depth where compliance-approved.

### Decision: Version 5.11 kickoff (slice 1)

**Decision:** Publish `version-5.11-scope.md`, `version-5.11-completion-checklist.md`, capability matrix 5.11 planning table, roadmap 5.11 section, and `.cursor/rules/version-511-sprint-loop.mdc`.

**Reason:** v5.10.0 sign-off complete (`v5.10.0` tagged); unsupervised re-filing, live charge retry execution, HRIS passwordless UI, and multi-IdP bulk provisioning scaffolds need a sequenced delivery path before v5.11.0 release.

**Follow-up work:** Slice 2 — unsupervised bureau re-filing scaffold.

### Decision: Bureau unsupervised re-filing scaffold (Version 5.11 slice 2)

**Decision:** Ship operator-gated bureau unsupervised re-filing audit (`bureau_unsupervised_refiling_runs` migration 059) with status, list, start-from-refiled-bureau-refiling-run, and admin approve endpoints behind `ENABLE_BUREAU_UNSUPERVISED_REFILING`.

**Reason:** 5.11 disputes epic extends 5.10 bureau re-filing with operator-gated unsupervised re-filing run audit without live bureau API calls.

**Follow-up work:** Slice 3 — live charge retry execution scaffold.

### Decision: Stripe live charge retry execution scaffold (Version 5.11 slice 3)

**Decision:** Ship admin-gated Stripe live charge retry execution audit (`stripe_live_charge_retry_execution_runs` migration 060) with status, list, submit-from-retried-charge-retry-run, and admin approve endpoints behind `ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION`.

**Reason:** 5.11 billing epic extends 5.10 charge retry with operator-gated live execution run audit without live Stripe charge API calls.

**Follow-up work:** Slice 4 — HRIS passwordless UI scaffold.

### Decision: HRIS passwordless UI scaffold (Version 5.11 slice 4)

**Decision:** Ship admin-gated HRIS passwordless UI audit (`hris_passwordless_ui_runs` migration 061) with status, list, start-from-enrolled-saml-passwordless-enrollment-run, and admin approve endpoints behind `ENABLE_HRIS_PASSWORDLESS_UI`.

**Reason:** 5.11 identity epic extends 5.10 SAML passwordless enrollment with operator-gated HRIS-linked UI run audit without native mobile passkey UI.

**Follow-up work:** Slice 5 — multi-IdP bulk provisioning scaffold.

### Decision: Multi-IdP bulk provisioning scaffold (Version 5.11 slice 5)

**Decision:** Ship admin-gated multi-IdP bulk provisioning audit (`bulk_idp_provisioning_runs` migration 062) with status, list, start-from-approved-hris-passwordless-ui-run, and admin approve endpoints behind `ENABLE_MULTI_IDP_BULK_PROVISIONING`.

**Reason:** 5.11 enterprise epic extends HRIS passwordless UI with operator-gated bulk IdP provisioning run audit without cross-org IdP templates or automated cert rotation.

**Follow-up work:** Slice 6 — capability matrix 5.11 sign-off.

### Decision: Version 5.11 epic sign-off

**Decision:** Mark all four Version 5.11 epics **Partial ✅** in `version-5.11-scope.md`, add capability matrix 5.11 epic sign-off table, complete checklist exit criteria, and publish `docs/release-notes/v5.11.0.md`.

**Reason:** v5.11.0 completes compliance-gated production execution scaffolds; native mobile apps, public OAuth dev portal, cross-org benchmarks, and live bureau API calls remain deferred to 5.12+.

**Follow-up work:** Version 5.12 planning — production depth where compliance-approved.

### Decision: Version 5.12 kickoff (slice 1)

**Decision:** Publish `version-5.12-scope.md`, `version-5.12-completion-checklist.md`, roadmap 5.12 section, capability matrix 5.12 planning status, and `.cursor/rules/version-512-sprint-loop.mdc`.

**Reason:** v5.11.0 sign-off complete (`v5.11.0` tagged); bureau live API invocation, public OAuth developer portal, cross-org benchmarks, and mobile passkey readiness need sequenced delivery before v5.12.0 release.

**Follow-up work:** Slice 2 — bureau live API invocation scaffold.

### Decision: Bureau live API invocation audit enrichment (Version 5.12 slice 2)

**Decision:** Extend bureau live API invocation runs with `invocation_reference_id` and `invocation_channel` audit fields (migration `063_bureau_live_api_audit`) and expose both fields via API and `@verdin/api-client`.

**Reason:** 5.12 disputes epic keeps operator-gated invocation flow while improving downstream traceability for live-integration readiness and reconciliation.

**Follow-up work:** Slice 3 — public OAuth developer portal scaffold.

### Decision: Public OAuth developer portal scaffold (Version 5.12 slice 3)

**Decision:** Ship admin-gated OAuth developer portal app registration audit (`oauth_developer_apps` migration 064) with list, create, and approve endpoints behind `ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL`.

**Reason:** 5.12 platform epic extends internal developer portal controls with an auditable public OAuth app scaffold while preserving explicit admin approval.

**Follow-up work:** Slice 4 — cross-org benchmark analytics scaffold.

### Decision: Cross-org benchmark analytics scaffold (Version 5.12 slice 4)

**Decision:** Ship governance-gated cross-org benchmark analytics with `cross_org_benchmark_runs`
(migration `065`), reporting status/summary/run endpoints, and `@verdin/api-client` support behind
`ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS`.

**Reason:** 5.12 reporting epic extends predictive scaffolds with aggregate-only benchmark
comparisons and explicit run audit while keeping tenant-level exports and sensitive dimensions
deferred.

**Follow-up work:** Slice 5 — mobile passkey readiness scaffold.

### Decision: Mobile passkey readiness scaffold (Version 5.12 slice 5)

**Decision:** Ship admin-gated mobile passkey readiness audit (`mobile_passkey_readiness_runs`
migration `066`), federation status/list/start-from-approved-hris-ui-run/approve endpoints, and
`@verdin/api-client` support behind `ENABLE_MOBILE_PASSKEY_READINESS`.

**Reason:** 5.12 identity epic extends HRIS passwordless UI scaffolds with web-first passkey
readiness and operator-gated enrollment audit while deferring native mobile clients and device
attestation.

**Follow-up work:** Slice 6 — capability matrix 5.12 sign-off and `v5.12.0` release.

### Decision: Version 5.12 epic sign-off

**Decision:** Mark all four Version 5.12 epics **Partial ✅** in `version-5.12-scope.md`, add capability matrix 5.12 epic sign-off table, complete checklist exit criteria, and publish `docs/release-notes/v5.12.0.md`.

**Reason:** v5.12.0 completes compliance-gated expansion surface scaffolds; native mobile apps, OAuth marketplace publishing, autonomous bureau filing, and unredacted benchmark exports remain deferred to 5.13+.

**Follow-up work:** Version 5.13 planning — production depth where compliance-approved.

### Decision: Native mobile passkey client scaffold (Version 5.13 slice 1)

**Decision:** Ship admin-gated native mobile passkey client audit (`native_mobile_passkey_client_runs`
migration `067`), federation status/list/start-from-approved-passkey-readiness-run/approve endpoints,
and `@verdin/api-client` support behind `ENABLE_NATIVE_MOBILE_PASSKEY_CLIENT`.

**Reason:** 5.13 identity epic extends 5.12 mobile passkey readiness with operator-gated native
client enrollment audit while deferring device attestation and app store distribution.

**Follow-up work:** Slice 2 — OAuth marketplace publishing scaffold or next 5.13 deferred epic.

### Decision: OAuth marketplace publishing scaffold (Version 5.13 slice 2)

**Decision:** Ship admin-gated OAuth marketplace publishing audit (`oauth_marketplace_publishing_runs`
migration `068`), org-admin status/list/start-from-approved-oauth-app/approve endpoints, and
`@verdin/api-client` support behind `ENABLE_OAUTH_MARKETPLACE_PUBLISHING`.

**Reason:** 5.13 platform epic extends 5.12 public OAuth developer portal with operator-gated
marketplace listing audit while deferring public marketplace distribution and partner trust scoring.

**Follow-up work:** Slice 3 — fully autonomous bureau API filing scaffold or cross-org benchmark export.

### Decision: Fully autonomous bureau API filing scaffold (Version 5.13 slice 3)

**Decision:** Ship admin-gated fully autonomous bureau API filing audit (`fully_autonomous_bureau_api_filing_runs`
migration `069_full_auto_bureau_api`), compliance status/list/start-from-filed-autonomous-filing/approve endpoints, and
`@verdin/api-client` support behind `ENABLE_FULLY_AUTONOMOUS_BUREAU_API_FILING`.

**Reason:** 5.13 disputes epic extends 5.9 autonomous bureau filing with operator-gated fully
autonomous API execution audit while deferring unsupervised live bureau submission loops.

**Follow-up work:** Slice 4 — unredacted cross-org benchmark export scaffold or v5.13 sign-off.

### Decision: Unredacted cross-org benchmark export scaffold (Version 5.13 slice 4)

**Decision:** Ship admin-gated unredacted cross-org benchmark export audit
(`unredacted_cross_org_benchmark_export_runs` migration `076_unredacted_benchmark_export`),
reporting status/list/submit-from-benchmark-run/approve endpoints, and `@verdin/api-client` support behind
`ENABLE_UNREDACTED_CROSS_ORG_BENCHMARK_EXPORT` chained to cross-org benchmark analytics.

**Reason:** 5.13 reporting epic extends 5.12 aggregate benchmark analytics with operator-gated export
audit while deferring live unredacted CSV/JSON/blob generation and raw tenant PII export.

**Follow-up work:** v5.13 sign-off — capability matrix, release notes, and tag `v5.13.0`.

### Decision: Version 5.13 epic sign-off

**Decision:** Mark all four Version 5.13 epics **Partial ✅** in `version-5.13-scope.md`, add capability matrix 5.13 epic sign-off table, complete checklist exit criteria, and publish `docs/release-notes/v5.13.0.md`.

**Reason:** v5.13.0 completes native mobile depth scaffolds; live unredacted blob export, unsupervised autonomous filing loops, public marketplace listings, and native app store distribution remain deferred to 5.14+.

**Follow-up work:** Version 5.14 planning — production depth where compliance-approved.

### Decision: Version 5.14 kickoff (scope + checklist)

**Decision:** Publish `version-5.14-scope.md` and `version-5.14-completion-checklist.md` for Production
Distribution Depth — live unredacted blob export, unsupervised filing loops, public marketplace listings,
and native app store distribution readiness — with explicit 5.15+ deferrals.

**Reason:** v5.13.0 sign-off complete (`v5.13.0` tagged); deferred distribution and live export surfaces
need sequenced delivery before v5.14.0 release.

**Follow-up work:** Slice 2 — live unredacted benchmark blob export scaffold.

### Decision: Live unredacted benchmark blob export scaffold (Version 5.14 slice 2)

**Decision:** Ship admin-gated live unredacted benchmark blob export pipeline
(`live_unredacted_benchmark_blob_export_runs` migration `077_live_benchmark_blob_export`),
reporting status/list/submit-from-approved-unredacted-export/approve endpoints that write a redacted
placeholder JSON artifact to object storage, and `@verdin/api-client` support behind
`ENABLE_LIVE_UNREDACTED_BENCHMARK_BLOB_EXPORT`.

**Reason:** 5.14 reporting epic extends 5.13 unredacted export audit with a secure storage-reference
pipeline while deferring unrestricted cross-tenant PII dumps and public download links.

**Follow-up work:** Slice 3 — unsupervised autonomous filing loops scaffold.

### Decision: Unsupervised autonomous filing loops scaffold (Version 5.14 slice 3)

**Decision:** Ship operator-gated unsupervised autonomous filing loop audit
(`unsupervised_autonomous_filing_loop_runs` migration `078_unsupervised_filing_loops`),
compliance status/list/submit-from-executed-fully-autonomous-API-filing/approve endpoints with
timeline event `unsupervised_autonomous_filing_loop`, and `@verdin/api-client` support behind
`ENABLE_UNSUPERVISED_AUTONOMOUS_FILING_LOOPS`.

**Reason:** 5.14 disputes epic extends 5.13 fully autonomous API filing audit with an unsupervised
loop readiness scaffold while deferring fully unsupervised live bureau submission without kill-switch.

**Follow-up work:** Slice 4 — public OAuth marketplace listings scaffold.

### Decision: Public OAuth marketplace listings scaffold (Version 5.14 slice 4)

**Decision:** Ship admin-gated public OAuth marketplace listing audit
(`public_oauth_marketplace_listing_runs` migration `079_public_oauth_listings`),
org-admin status/list/submit-from-approved-publishing/approve endpoints with terminal status
`listed`, and `@verdin/api-client` support behind `ENABLE_PUBLIC_OAUTH_MARKETPLACE_LISTINGS`.

**Reason:** 5.14 platform epic extends 5.13 marketplace publishing audit with a public listing
readiness scaffold while deferring unreviewed third-party auto-approve.

**Follow-up work:** Slice 5 — native mobile app store distribution scaffold.

### Decision: Native mobile app store distribution scaffold (Version 5.14 slice 5)

**Decision:** Ship admin-gated native mobile app store distribution readiness audit
(`native_mobile_app_store_distribution_runs` migration `080_native_mobile_app_store`),
federation status/list/submit-from-approved-passkey-client/approve endpoints with terminal status
`ready`, and `@verdin/api-client` support behind `ENABLE_NATIVE_MOBILE_APP_STORE_DISTRIBUTION`.

**Reason:** 5.14 identity epic extends 5.13 native passkey client audit with app store distribution
readiness while deferring production App Store / Play Store release operations.

**Follow-up work:** Slice 6 — Version 5.14 capability matrix sign-off and `v5.14.0` tag.

### Decision: Version 5.14 epic sign-off

**Decision:** Mark all four Version 5.14 epics **Partial ✅** in `version-5.14-scope.md`, update
capability matrix and roadmap to Released, complete checklist exit criteria, and publish
`docs/release-notes/v5.14.0.md`.

**Reason:** v5.14.0 completes production distribution depth scaffolds; unrestricted PII dumps,
fully unsupervised live bureau loops, marketplace auto-approve, and production store release ops
remain deferred to 5.15+.

**Follow-up work:** Stop at `v5.14.0` tagged — do not start Version 5.15 without explicit kickoff.
