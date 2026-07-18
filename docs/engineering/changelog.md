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

## Compliance intelligence — widen metadata payment_status (Phase 21)

**Decision:** Widen `document_metadata.payment_status` from varchar(50) to varchar(255) via migration `093_widen_meta_pay_status`, and align API `DocumentMetadata` + worker metadata table definitions.

**Reason:** Bureau status narratives (charged-off / past-due text) exceeded 50 characters and caused metadata extract writes to fail during pilot OCR.

**Guardrails:** Schema-only widen; no truncation of existing values; no PII export change.

**Follow-up work:** Slice 3 — operator re-parse; Slice 4 — Version 22.0 sign-off.

## Compliance intelligence — Version 22.0 scope (Phase 21)

**Decision:** Scope Version 22.0 as Document Pipeline Hardening — widen `document_metadata.payment_status` and add an operator-gated credit-report re-parse enqueue. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 23.0+ or never.

**Reason:** After 21.0 and pilot uploads, metadata extract failures on long payment-status text and missed parse jobs (stale worker / no staff re-enqueue) are the next non-blocked hardening gaps.

**Follow-up work:** Slice 2 — widen payment_status; Slice 3 — operator re-parse; Slice 4 — sign-off.

## Compliance intelligence — Version 21.0 sign-off (Phase 20)

**Decision:** Close Phase 20 as shipped `v21.0.0` after per-recipient benchmark window defaults and ingestion audit bureau/status list filters. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 22.0+ or never.

**Reason:** Non-blocked configuration and audit-filter polish over owned surfaces is complete; remaining items need legal/compliance or product decisions.

**Follow-up work:** Tag `v21.0.0`; next gated live-integration phase only with explicit legal/compliance sign-off.

## Compliance intelligence — ingestion audit bureau/status list filters (Phase 20)

**Decision:** Add optional `bureau_target` and `status` query params on `GET /compliance/bureau-response-ingestion/runs`, with matching Compliance Center filter controls. Invalid `status` values return 422; start-run remains always-deferred.

**Reason:** Operators already store bureau target and status on each audit row; list filtering completes the audit surface without enabling live polling.

**Guardrails:** Org-scoped only; no change to deferred start semantics; live polling stays deferred.

**Follow-up work:** Slice 4 — Version 21.0 sign-off + release notes.

## Compliance intelligence — per-recipient benchmark window defaults (Phase 20)

**Decision:** Add optional `reinvestigation_benchmark_recipient_windows` on dispute settings (`credit_bureau` / `furnisher`) with the same merge/null-clear semantics as bureau windows. Reporting resolves recipient override → bureau override → org → platform when `recipient` is set on benchmarks.

**Reason:** After 20.0 recipient breakdown, CRA vs furnisher clocks often need different trailing windows than the org-wide pair.

**Guardrails:** Org-scoped only; invalid recipient keys → 422; recent ≤ baseline.

**Follow-up work:** Slice 3 — ingestion audit bureau/status list filters.

## Compliance intelligence — Version 21.0 scope (Phase 20)

**Decision:** Scope Version 21.0 as Reinvestigation Operations Filters — per-recipient benchmark window defaults and ingestion audit bureau/status list filters. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 22.0+ or never.

**Reason:** After 20.0 recipient breakdown and CSV export, CRA vs furnisher window configuration and ingestion list filter parity are the next non-blocked polish gaps.

**Follow-up work:** Slice 2 — per-recipient window defaults; Slice 3 — ingestion list filters; Slice 4 — sign-off.

## Compliance intelligence — Version 20.0 sign-off (Phase 19)

**Decision:** Close Phase 19 as shipped `v20.0.0` after benchmarks `group_by=recipient` and aggregate rates CSV export. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 21.0+ or never.

**Reason:** Non-blocked benchmark parity over owned analytics and operator-gated aggregate export is complete; remaining items need legal/compliance or product decisions.

**Follow-up work:** Tag `v20.0.0`; next non-blocked polish or gated live-integration phase only with explicit sign-off.

## Compliance intelligence — org-internal benchmarks aggregate CSV export (Phase 19)

**Decision:** Add `GET /reporting/reinvestigation-outcomes/benchmarks/export?format=csv` and a Download CSV control on Outcome benchmarks. Export org aggregate + optional breakdown rows using the same query params as the JSON endpoint.

**Reason:** Staff need a handoff artifact for advisory rate comparisons without response-level PII.

**Guardrails:** Counts/rates only; no client/account IDs; org-scoped; `format=csv` only.

**Follow-up work:** Slice 4 — sign-off and `v20.0.0` tag.

## Compliance intelligence — outcome benchmarks per-recipient breakdown (Phase 19)

**Decision:** Add optional `group_by=recipient` to `GET /reporting/reinvestigation-outcomes/benchmarks` returning `by_recipient` entries with per-recipient baseline/recent analytics and advisory rate deltas. Reporting Center adds a Bureau/Recipient breakdown control (parity with outcome analytics).

**Reason:** After 19.0 bureau breakdown, CRA vs furnisher benchmark comparison still required switching surfaces or multiple round-trips.

**Guardrails:** Org-scoped only; same windows as the aggregate; unlinked responses bucket as `unknown`; invalid `group_by` → 422.

**Follow-up work:** Slice 3 — aggregate rates CSV export; Slice 4 — sign-off.

## Compliance intelligence — Version 20.0 scope (Phase 19)

**Decision:** Scope Version 20.0 as Reinvestigation Benchmark Parity — outcome benchmarks `group_by=recipient` and an operator-gated aggregate rates CSV export (no PII). Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 21.0+ or never.

**Reason:** After 19.0 bureau breakdown, CRA vs furnisher benchmark comparison and staff handoff download are the next non-blocked parity gaps over owned analytics.

**Follow-up work:** Slice 2 — benchmarks `group_by=recipient`; Slice 3 — aggregate rates CSV export; Slice 4 — sign-off.

## E2E — Poll awaiting-response before CRA outcome (2026-07-17)

**Decision:** After `dispute-awaiting-response`, poll GET account until `dispute_status=awaiting_response` before `dispute-response-received` (same pattern as post-send).

**Reason:** Live ASGI can return the awaiting-response body before `get_db` commits; the next POST then reads stale `dispute_sent` and 422s. Artifact timing showed ~5ms between success and failure.

**Follow-up:** Consider committing the session before the response body is finalized for mutation endpoints (larger change).

## Compliance intelligence — Version 19.0 sign-off (Phase 18)

**Decision:** Close Phase 18 as shipped `v19.0.0` after per-bureau window defaults and benchmarks `group_by=bureau`. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 20.0+ or never.

**Reason:** Non-blocked benchmark depth over owned configuration and analytics is complete; remaining items need legal/compliance or product decisions.

**Follow-up work:** Tag `v19.0.0`; next non-blocked polish or gated live-integration phase only with explicit sign-off.

## Compliance intelligence — outcome benchmarks per-bureau breakdown (Phase 18)

**Decision:** Add optional `group_by=bureau` to `GET /reporting/reinvestigation-outcomes/benchmarks` returning `by_bureau` entries with per-bureau baseline/recent analytics and advisory rate deltas. Reporting Center always requests the breakdown.

**Reason:** Outcome analytics already supported single-call bureau comparison; benchmarks required N round-trips.

**Guardrails:** Org-scoped only; same windows as the aggregate; no cross-tenant data; invalid `group_by` → 422.

**Follow-up work:** 19.0 sign-off and release notes.

## Compliance intelligence — per-bureau benchmark window defaults (Phase 18)

**Decision:** Persist optional Equifax/Experian/TransUnion window overrides in `reinvestigation_benchmark_bureau_windows` JSONB on `organization_dispute_settings`. When `GET /reporting/reinvestigation-outcomes/benchmarks` omits window params and includes `bureau=`, resolve override → org-wide → platform 90/30.

**Reason:** Explicit 18.0 “Not included”; Reporting bureau filter previously always used the single org-wide pair.

**Guardrails:** Only three CRA keys; `null` clears an override; recent ≤ baseline per bureau; org-scoped only.

**Follow-up work:** Outcome benchmarks `group_by=bureau` (slice 3); 19.0 sign-off.

## Compliance intelligence — Version 19.0 kickoff (Phase 18)

**Decision:** Scope Version 19.0 as Reinvestigation Benchmark Depth — per-bureau window defaults and outcome benchmarks `group_by=bureau` breakdown. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 20.0+ or never.

**Reason:** 18.0 closed org-wide window defaults and ingestion case/account scope; operators still need bureau-specific windows and single-call bureau comparison on the benchmarks read model.

**Follow-up work:** Implement checklist slices 2–4 toward `v19.0.0`.

## Compliance intelligence — Version 18.0 sign-off (Phase 17)

**Decision:** Close Phase 17 as shipped `v18.0.0` after org benchmark window defaults and ingestion case/account scope UI. Keep live bureau polling, automated filing, unsupervised escalation, litigation e-filing, and cross-tenant benchmarks deferred to 19.0+ or never.

**Reason:** Operator polish over owned configuration and staff surfaces is complete; remaining items need legal/compliance or product decisions outside this phase.

**Follow-up work:** Tag `v18.0.0`; next non-blocked polish or gated live-integration phase only with explicit sign-off.

## Compliance intelligence — cross-bureau high_balance / credit_limit (Phase 14)

**Decision:** Extend litigation-packet cross-bureau comparison to include stored `high_balance` and `credit_limit` on sibling tradelines. New discrepancy kinds `high_balance_conflict` and `credit_limit_conflict` use the same $1.00 monetary tolerance as balance and past-due.

**Reason:** Phase 13 added past-due and date-reported fields but left high-balance and credit-limit unused despite being stored on accounts — closing documented 5.20 tech debt.

**Guardrails:** Read-only comparison of data already on the platform; no live bureau contact; tolerance remains a module constant (org-configurable tolerance deferred to 5.22+).

**Alternatives considered:** Reusing `balance_conflict` for high balance (rejected — distinct FCRA reinvestigation signals); comparing only when both fields are non-null with strict equality (rejected — inconsistent with existing tolerance band for monetary fields).

**Technical debt:** Fields depend on parsed report ingestion quality; missing values are skipped rather than flagged.

**Follow-up work:** 5.21 sign-off and release notes.

## Compliance intelligence — ingestion audit case/account scope UI (Phase 17)

**Decision:** Extend the Compliance Center Response ingestion tab so start and list filters accept optional `case_id` / `account_id` (already supported by the Phase 15 API). History table shows scoped IDs when present.

**Reason:** Phase 16 UI could only start org-wide deferred runs; operators need to scope audit intent to a case or account without live polling.

**Guardrails:** UUID validation client-side; start still always records `status=deferred`; no bureau API calls.

**Follow-up work:** 18.0 sign-off and release notes.

## Compliance intelligence — org-configurable benchmark window defaults (Phase 17)

**Decision:** Persist `reinvestigation_benchmark_baseline_days` (default 90) and `reinvestigation_benchmark_recent_days` (default 30) on `organization_dispute_settings`. Omit window query params on `GET /reporting/reinvestigation-outcomes/benchmarks` to apply org defaults. Org Admin dispute settings and Reporting Center Outcome benchmarks consume the same values.

**Reason:** Phase 16 hard-coded 90/30 in the UI; operators need org-level defaults without editing every query.

**Guardrails:** Admin write; recent ≤ baseline; org-scoped only; no cross-tenant data.

**Follow-up work:** Ingestion audit case/account scope UI (slice 3); 18.0 sign-off.

## Compliance intelligence — Version 17.0 sign-off (Phase 16)

**Decision:** Mark Version 17.0 / Compliance Intelligence Phase 16 as shipped with release notes `v17.0.0` and tag `v17.0.0`. Flip capability matrix, roadmap, scope epic outcomes, and checklist exit criteria to released.

**Reason:** Reporting Center benchmarks UI and Compliance Center ingestion audit UI are merged; governance docs must match production state.

**Follow-up work:** 18.0+ live bureau polling / automated filing only after legal/compliance sign-off.

## Compliance intelligence — Compliance Center ingestion audit UI (Phase 16)

**Decision:** Add a Compliance Center **Response ingestion** tab that lists scaffold status, paginated audit runs, and starts deferred runs via the Phase 15 API (always `status=deferred`).

**Reason:** Phase 15 shipped the ingestion audit API without a staff surface.

**Guardrails:** Start never polls a bureau; UI surfaces blockers and deferral reasons.

**Follow-up work:** 17.0 sign-off and release notes.

## Compliance intelligence — Reporting Center org-internal benchmarks UI (Phase 16)

**Decision:** Add an "Outcome benchmarks" tab on the Enterprise reporting page that calls `GET /reporting/reinvestigation-outcomes/benchmarks`, showing baseline/recent windows, advisory rate deltas, and optional bureau filter.

**Reason:** Phase 15 shipped the read model without a staff surface; operators need in-product access to org-internal baselines.

**Guardrails:** Org-scoped only; no cross-tenant data; read-only; no live bureau contact.

**Follow-up work:** Compliance Center ingestion audit UI (slice 3); 17.0 sign-off.

## Compliance intelligence — Version 16.0 sign-off (Phase 15)

**Decision:** Mark Version 16.0 / Compliance Intelligence Phase 15 as shipped with release notes `v16.0.0` and tag `v16.0.0`. Flip capability matrix, roadmap, scope epic outcomes, and checklist exit criteria to released.

**Reason:** All Phase 15 slices (org tolerance, ingestion audit scaffold, org-internal benchmarks) are merged; governance docs must match production state.

**Follow-up work:** 17.0+ live bureau polling / automated filing only after legal/compliance sign-off.

## Compliance intelligence — org-internal reinvestigation benchmarks (Phase 15)

**Decision:** Add `GET /reporting/reinvestigation-outcomes/benchmarks` returning trailing org-scoped `baseline` (default 90 days) and nested `recent` (default 30 days) analytics plus advisory `rate_deltas` (recent − baseline). Reuses the existing outcome analytics computation — no new tables.

**Reason:** Operators need in-org historical context when reading deletion/verification rates without waiting on cross-tenant benchmark governance (17.0+).

**Guardrails:** `scope` is always `organization`; no cross-tenant rows; no live bureau contact; `recent_days` must be ≤ `baseline_days`.

**Follow-up work:** 16.0 sign-off and release notes.

## Compliance intelligence — bureau response ingestion audit scaffold (Phase 15)

**Decision:** Add `bureau_response_ingestion_runs` with status/list/get/start under `/compliance/bureau-response-ingestion`. Starting a run always records `status=deferred` with an explicit deferral reason — no external bureau API calls.

**Reason:** Operators need an auditable trail of intended ingestion checks before live polling is approved (17.0+).

**Guardrails:** Staff-mediated only; `ready`/`live_polling_enabled` stay false; write requires case_manager+.

**Follow-up work:** Org-internal reinvestigation benchmarks (slice 4); 16.0 sign-off.

## Compliance intelligence — org-configurable cross-bureau tolerance (Phase 15)

**Decision:** Store per-org `cross_bureau_balance_tolerance` in `organization_dispute_settings` (default $1.00, range $0.01–$100.00). Expose GET/PATCH on `/org-admin/dispute-settings`; litigation-packet cross-bureau evidence resolves the org value at read time.

**Reason:** Phase 14 left tolerance as a module constant; operators need org-level control without cross-tenant configuration.

**Guardrails:** Admin-only org-admin gate; no live bureau contact; tolerance applies only to monetary cross-bureau fields (balance, past-due, high_balance, credit_limit).

**Follow-up work:** Bureau response ingestion audit scaffold (slice 3); org-internal benchmarks (slice 4).

## Compliance intelligence — structured PDF litigation export layout (Phase 14)

**Decision:** Replace the litigation-packet PDF's plain wrapped-text canvas with a reportlab platypus `SimpleDocTemplate` layout: title/subtitle, spaced section headings, and bullet lists for tradeline, Section 611 clock, assessment, indicators, cross-bureau discrepancies, mailed rounds, and recorded responses.

**Reason:** Phase 13 shipped PDF export as a simple text dump on canvas — hard to scan for attorneys. Structured sections close documented 5.20 tech debt without changing packet content or the text export.

**Guardrails:** Same disclaimer and fields as `build_litigation_packet_text`; no branding/templates per org; no auto-filing or transmission.

**Alternatives considered:** Reusing dispute-letter canvas helpers (rejected — litigation packet has many sections); HTML-to-PDF (rejected — adds dependency and diverges from existing reportlab stack).

**Technical debt:** PDF still substitutes "Section 611" for the § glyph (Helvetica limitation); org-specific letterhead deferred.

**Follow-up work:** 5.21 sign-off and release notes.

## Compliance intelligence — per-recipient reinvestigation analytics breakdown (Phase 14)

**Decision:** Extend `GET /reporting/reinvestigation-outcomes` so `group_by=recipient` returns a `by_recipient` array of `{recipient, analytics}` entries. Recipient is taken from the linked dispute letter's `recipient_type`; responses without a linked letter are bucketed as `unknown`. Existing `group_by=bureau` behavior is unchanged. The Reporting Center adds a "Break down by" control (Bureau / Recipient).

**Reason:** Phase 13 only supported `group_by=bureau`. Operators also need to compare credit-bureau vs furnisher response rates without N filtered calls — closing the documented bureau-only `group_by` tech debt.

**Guardrails:** Read model only — org-scoped, no cross-tenant data, no live bureau contact. Top-level `analytics` remains the filtered aggregate. Invalid `group_by` values still return `422`.

**Alternatives considered:** Always emitting both `by_bureau` and `by_recipient` (rejected — keeps payloads smaller and matches the existing single-dimension pattern); filtering by recipient as a query param instead of a roll-up (rejected — does not close the single-call comparison gap).

**Technical debt:** Unlinked responses (no `dispute_letter_id`) always land in `unknown`, which can dilute recipient rates when staff record outcomes without linking the letter.

**Follow-up work:** 5.21 sign-off and release notes.

## Compliance intelligence — cross-bureau discrepancy depth (Phase 13)

**Decision:** Give `detect_cross_bureau_discrepancies` a default `$1.00` balance/past-due tolerance (`DEFAULT_BALANCE_TOLERANCE`, overridable via `balance_tolerance`) so trivial rounding differences no longer flag as conflicts, and compare two additional stored fields — `past_due_amount` (`past_due_conflict`) and `date_reported` (`date_reported_conflict`). `BureauTradelineView` and the litigation-packet assembly pass those fields through from the account model.

**Reason:** Phase 12 flagged any balance difference, including $0.01 rounding noise that cluttered the packet. Past-due amount and date-reported are high-signal FCRA accuracy fields already on the tradeline model but were unused in the comparison.

**Guardrails:** Read-only comparison over stored parsed-report data; no new bureau collection; tolerance applies only to monetary fields (status/outcome/date still exact-match). Findings remain advisory for attorney review.

**Alternatives considered:** Percentage-based tolerance (rejected — absolute $1.00 is simpler and matches typical CRA rounding); exposing tolerance as a query param (rejected for this slice — constant is enough; the kwarg keeps it unit-testable).

**Technical debt:** Tolerance is a module constant, not org-configurable. High-balance / credit-limit fields are still not compared.

**Follow-up work:** Capability matrix 5.20 sign-off + release notes (slice 6).

## Compliance intelligence — PDF litigation evidence export (Phase 13)

**Decision:** Extend `GET /accounts/{account_id}/litigation-packet/export` to accept `format=pdf` alongside the existing `text` default. `build_litigation_packet_pdf_bytes` renders the same attorney-review content as the text export via reportlab (mirroring `dispute_letter_export.py`). The web packet panel offers both Download .txt and Download .pdf. Guardrails unchanged: write-permission gate, disclaimer at top, never auto-transmitted.

**Reason:** Phase 12 shipped text-only. Attorneys commonly prefer PDF for handoff and archival; reusing the dispute-letter reportlab pipeline keeps the slice small and consistent.

**Guardrails:** Operator-gated (`case_manager`+); formats limited to `text`/`pdf` (`422` otherwise); platform never files, drafts pleadings, or transmits the file.

**Alternatives considered:** HTML-to-PDF via WeasyPrint (rejected — heavier dependency when reportlab is already in-tree); PDF-only default (rejected — keeps greppable text as the default).

**Technical debt:** PDF layout is a simple wrapped-text canvas (no tables/styles); Section markers substitute for § glyphs that Helvetica lacks.

**Follow-up work:** Cross-bureau discrepancy depth (slice 5).

## Compliance intelligence — per-recipient extended-window accuracy (Phase 13)

**Decision:** Compute the §611(a)(1)(B) 45-day `extended` flag independently for each recipient sub-clock in `_build_recipient_clocks`, using that recipient's own `clock_start_date` and the shared account/case document dates. The tradeline-level `extended` flag (derived from the latest overall sent round) is unchanged. The clock panel shows a per-recipient §611(a)(1)(B) badge when a sub-clock is extended.

**Reason:** Phase 12 applied one tradeline-level `extended` boolean to every recipient sub-clock. A document uploaded during an early bureau round incorrectly stretched a later furnisher deadline (or vice versa). Evaluating the window against each recipient's start date closes that documented tech debt.

**Guardrails:** Read model only — no new document collection, no writes, no live bureau contact. Case-level documents still apply to every tradeline; account-linked documents still apply only to that tradeline. Attribution of which document "belongs" to which recipient is not attempted — only the timing relative to each recipient's clock start matters.

**Alternatives considered:** Linking documents to a specific dispute letter / recipient (rejected — documents are not currently recipient-scoped, and inventing that linkage is out of scope); leaving the shared flag (rejected — the inaccurate deadlines were the bug this slice fixes).

**Technical debt:** Documents are still not recipient-tagged; a furnisher-only supplemental upload that happens to fall inside an earlier bureau window will still extend the bureau clock.

**Follow-up work:** PDF litigation evidence export (slice 4); cross-bureau discrepancy depth (slice 5).

## Compliance intelligence — per-bureau reinvestigation analytics breakdown (Phase 13)

**Decision:** Add an optional `group_by=bureau` query param to `GET /reporting/reinvestigation-outcomes`. When set, the response includes a `by_bureau` array of `{bureau, analytics}` entries — each carrying the same analytics shape as the top-level aggregate — so operators can compare Equifax / Experian / TransUnion in a single call. The repository now returns `bureau` with each raw row; the service groups and reuses `compute_reinvestigation_outcome_analytics`. Invalid `group_by` values return `422`. The Reporting Center always requests `group_by=bureau` and renders a per-bureau rates table under the org aggregate.

**Reason:** Phase 12 only filtered one bureau at a time. Comparing bureaus required N round-trips and client-side join logic; a single-call roll-up closes that documented tech debt without changing the existing filter semantics.

**Guardrails:** Read model only — computed over stored dispute responses, org-scoped, no cross-tenant data and no live bureau contact. Top-level `analytics` remains the filtered aggregate so existing consumers keep working when `group_by` is omitted (`by_bureau` defaults to `[]`).

**Alternatives considered:** Always emitting `by_bureau` without a query param (rejected — keeps the default payload smaller for consumers that only need the org aggregate); a separate `/reinvestigation-outcomes/by-bureau` endpoint (rejected — duplicates filter semantics and auth).

**Technical debt:** Only `bureau` is supported as a `group_by` dimension; per-recipient (bureau vs furnisher) roll-ups remain out of scope for this slice.

**Follow-up work:** Per-recipient extended-window accuracy (slice 3); PDF litigation evidence export (slice 4); cross-bureau discrepancy depth (slice 5).

## Compliance intelligence — operator-gated litigation evidence export (Phase 12)

**Decision:** Add `GET /accounts/{account_id}/litigation-packet/export?format=text`, returning the assembled litigation packet as a downloadable `text/plain` attachment. A new pure formatter `litigation_packet_export.py` (`build_litigation_packet_text(packet)`) renders the packet; `AccountService.export_litigation_packet` calls the existing `get_account_litigation_packet` (reusing its `case_manager`+ write-permission gate) then formats it. The web packet panel gains a "Download evidence (.txt)" button that fetches the blob and triggers a browser download, reusing the case dispute-export download pattern.

**Reason:** The 5.18/5.19 packet was screen-only. Attorneys work from documents; operators need a portable evidence artifact to forward for review. Text keeps the slice small and the artifact diff-friendly/greppable.

**Guardrails:** The export is a **manual** attorney handoff — the platform assembles and hands the operator a file; it never transmits it to a court, bureau, or attorney, and never files or drafts pleadings. Read-only, operator-gated (inherits the packet's write-permission check — read-only roles get `403`). The disclaimer is reproduced at the top of every export. `format` accepts only `text` (else `422`).

**Alternatives considered:** PDF export (deferred — reportlab is already a dependency for dispute letters, but text ships the capability now and a PDF renderer can layer on later); a server-side "send to attorney" transmission (explicitly rejected — transmission stays a human action, consistent with the never-auto-file posture).

**Technical debt:** Text-only for now (no PDF/branding). The formatter reflects only fields already on `AccountLitigationPacket`; richer narrative (e.g. per-round timeline prose) is future work.

**Follow-up work:** Capability matrix 5.19 sign-off + release notes + `v5.19.0` tag (slice 6).

## Compliance intelligence — litigation packet cross-bureau evidence (Phase 12)

**Decision:** Fold cross-bureau discrepancy evidence into the litigation-readiness packet. A new pure module `cross_bureau.py` (`detect_cross_bureau_discrepancies(target, siblings)`) compares a tradeline to the same creditor's copies at _other_ bureaus in the case, returning typed `CrossBureauDiscrepancy` findings (`outcome_conflict`, `dispute_status_conflict`, `account_status_conflict`, `payment_status_conflict`, `balance_conflict`). `AccountService._build_cross_bureau_evidence` loads the case tradelines + recorded responses, matches siblings on normalized creditor name (plus masked account number when both present) and a different bureau, reduces each to its latest outcome/status/balance, and runs the detector. The packet gains a `cross_bureau` block, and `LitigationReadinessInputs` gains `cross_bureau_conflicts` / `cross_bureau_outcome_conflict` so `build_litigation_readiness` scores the signal (+25 for an outcome conflict, +10 for lesser divergences).

**Reason:** A single furnisher item deleted at one bureau but verified at another cannot be simultaneously accurate everywhere — it is a textbook FCRA reinvestigation-failure signal. The 5.18 packet graded each bureau's tradeline in isolation and missed this cross-bureau pattern (documented as follow-up work).

**Guardrails:** Read model only — compares data already stored on the platform (case tradelines + recorded responses); no live bureau contact, no writes, and still operator-gated behind `case_manager`+ write permission. Sibling matching stays conservative (same creditor **and** matching masked account number when both carry one) so distinct tradelines from the same creditor are not conflated. The detector is pure and independently unit-tested.

**Alternatives considered:** Reusing the existing `intelligence_context` cross-bureau report comparison (rejected — that surface compares raw report fields for discrepancy scoring, not dispute _outcomes_; the litigation angle needs outcome-level conflicts and its own auditable grading). Matching siblings on creditor name only (rejected — would conflate multiple tradelines from the same lender); matching on account number only (rejected — many imports lack a masked number).

**Technical debt:** Sibling latest-outcome reuses `_latest_response_outcome` (recorded response first, else terminal `dispute_status`), so a sibling with neither yields no outcome signal. Balance conflicts flag any difference (no tolerance band). Matching is per-case only — the same creditor across different cases is never compared (correct for now; cases are per-consumer).

**Follow-up work:** Operator-gated litigation evidence export (slice 5).

## Compliance intelligence — per-recipient reinvestigation clock splits (Phase 12)

**Decision:** Add a `recipients` array to each `GET /accounts/reinvestigation-clock` entry, splitting the §611 clock by recipient (credit bureau vs furnisher) when a tradeline is disputed with more than one. `AccountService._recipient_rounds_by_account` groups sent `dispute_letters` by `(account_id, recipient_type)` to compute each recipient's latest sent round + round count, and also returns a `dispute_letter_id → recipient_type` map. `_build_recipient_clocks` runs the existing `compute_reinvestigation_clock` helper per recipient, attributing recorded responses to a recipient via the response's `dispute_letter_id` — so a bureau response resolves only the bureau sub-clock. Each `AccountReinvestigationRecipientClock` carries its own `clock_start_date`, `dispute_round_count`, `deadline`, `days_remaining`, `state`, `extended`, and `response_count`. The clock panel renders the split as sub-rows only when there is more than one recipient.

**Reason:** The 5.18 clock reported a single recipient-agnostic `dispute_round_count` and one deadline per tradeline (documented tech debt). A tradeline disputed with both a bureau and the furnisher actually carries two independent §611 clocks; collapsing them hid whether one recipient had gone overdue while the other responded.

**Guardrails:** Read model only — computed over stored sent letters and recorded responses, no live bureau contact and no writes. Response attribution requires a linked `dispute_letter_id`; unlinked responses do not resolve any recipient sub-clock (they still count toward the account-level `response_received`). The top-level clock fields are unchanged for single-recipient tradelines, so existing consumers keep working.

**Alternatives considered:** Attributing responses to recipients heuristically by date proximity (rejected — brittle and non-auditable; the `dispute_letter_id` link is explicit); always emitting a `recipients` array even for single-recipient tradelines (rejected for now — the UI only needs the split when it disambiguates, and the top-level fields already cover the common case).

**Technical debt:** Recipients without a linked response never leave `awaiting`/`overdue` even if the consumer heard back off-platform. The `extended` flag is computed once per tradeline (document-in-window) and applied to every recipient sub-clock rather than per recipient.

**Follow-up work:** Litigation packet cross-bureau discrepancy evidence (slice 4); operator-gated evidence export (slice 5).

## Compliance intelligence — reinvestigation analytics slicing (Phase 12)

**Decision:** Add optional `start` / `end` (by response day, inclusive) and `bureau` filters to `GET /reporting/reinvestigation-outcomes`. `OperationsReportingRepository.get_reinvestigation_outcomes(org, start, end, bureau)` applies the `bureau` filter in SQL (`Account.bureau == bureau`) and the date-range filter in Python over the computed response day (which uses a `recorded_at` fallback, so an all-SQL predicate would need a `coalesce`). The service echoes the applied filters back under a new `filters` block (`ReinvestigationOutcomeFilters`), and the Reporting Center "Reinvestigation outcomes" tab gains from/to date inputs and a bureau select.

**Reason:** The 5.18 analytics covered all-time, all-bureau data (documented tech debt). Operators need to scope trends to a period (e.g. a quarter) or a single bureau to compare bureau behavior — both derivable from data already stored, with no new collection.

**Guardrails:** Still org-scoped only — no cross-tenant benchmarks. Read-only aggregate; no writes, no live bureau contact. The date-range filter is applied on the same response day used for time-to-response (response date, else `recorded_at`), keeping the window semantics consistent.

**Alternatives considered:** Pushing the date-range into SQL with `func.coalesce(response_date, recorded_at::date)` (rejected for now — the Python filter reuses the exact response-day logic already in the loop and stays trivially correct); adding a `group_by=bureau` breakdown in one call (deferred — a single-bureau filter is simpler and matches the per-recipient split coming in slice 3).

**Technical debt:** No per-bureau breakdown in a single response yet (callers filter one bureau at a time). Favorable = deleted + corrected is unchanged.

**Follow-up work:** Per-recipient reinvestigation clock splits (slice 3); cross-bureau litigation evidence (slice 4); operator-gated evidence export (slice 5).

## Compliance intelligence — litigation-readiness evidence packet (Phase 11)

**Decision:** Add an operator-gated litigation-readiness evidence packet at `GET /accounts/{account_id}/litigation-packet`. A pure `build_litigation_readiness(inputs)` helper (in `accounts/litigation_packet.py`) grades willful-noncompliance evidence into an advisory `{ eligible, strength, score, indicators, summary }` assessment. `AccountService.get_account_litigation_packet(...)` assembles the tradeline's reinvestigation trail — all dispute `letters` and recorded `responses` — with the current §611 clock state (reusing the slice 2–3 `sent_at`-keyed start and 45-day extension logic), the latest outcome, and the advisory re-dispute recommendation. Shipped with `@verdin/api-client` types and an on-demand "Litigation-readiness packet" panel on the account detail page.

**Reason:** The 5.17 readiness engine already surfaces an `escalate_attorney` signal, but operators had no consolidated evidence view to hand an attorney. Scoring the reinvestigation record (missed deadlines, verification of well-documented disputes, repeated rounds) turns that signal into a reviewable bundle while keeping the math pure and unit-testable like the other reinvestigation helpers.

**Guardrails:** Operator-gated — requires `case_manager`+ write permission (`ACCOUNT_WRITE_ROLE`), so read-only users get `403`. Read-only computation over stored data; no writes, no bureau contact. The packet always carries a `disclaimer`: the platform never drafts pleadings, files suit, e-files, or transmits to a court/attorney — a licensed attorney independently decides whether to litigate. A recorded response stops the §611 clock, so a resolved (deleted/corrected) tradeline grades `not_ready` and a lone verified round only reaches `weak`.

**Alternatives considered:** Persisting packet snapshots (rejected — the assessment is a live derivation over evidence that keeps changing; a stored snapshot would drift and implies a filing artifact we explicitly do not produce); auto-generating the packet on the case dashboard (rejected — it is account-scoped and write-gated, and fetching on demand avoids surfacing a litigation grade to read-only viewers); folding the grade into the existing readiness endpoint (rejected — readiness is a per-case advisory queue; the packet is a per-account evidence bundle with a distinct permission gate).

**Technical debt:** The score weights are heuristic (no calibration data yet) and do not yet incorporate cross-bureau discrepancy evidence or per-recipient (bureau vs furnisher) letter splits. Indicators are English-only.

**Follow-up work:** Capability-matrix / governance sign-off + release notes (slice 6). Deferred: automated litigation filing / e-filing stays permanently out of scope.

## Compliance intelligence — reinvestigation outcome analytics (Phase 11)

**Decision:** Add a per-org reinvestigation outcome analytics read model. A pure `compute_reinvestigation_outcome_analytics(rows)` helper (in `accounts/reinvestigation_analytics.py`) rolls recorded `dispute_responses` into per-outcome counts, derived rates (deletion / verification / correction / favorable / no-response), and time-to-response stats (avg / median). `OperationsReportingRepository.get_reinvestigation_outcomes(org)` supplies the rows — a left join over `dispute_responses → dispute_letters` (for `sent_at`) and `→ accounts` (for `last_dispute_date`), computing elapsed days from the clock start to the response date. Exposed at `GET /reporting/reinvestigation-outcomes` with `@verdin/api-client` types and a "Reinvestigation outcomes" tab on the Reporting Center.

**Reason:** The clock (slice 2–3) and readiness (5.17) surfaces are per-case. Operators need an org-level view of how disputes actually resolve — deletion vs. verification rates and how long bureaus take — to steer strategy. Keeping the math in a pure helper mirrors the existing reinvestigation helpers and keeps it unit-testable.

**Guardrails:** Org-scoped only — no cross-tenant benchmarks (those stay deferred behind the enterprise `cross-org-benchmarks` gate). Read-only aggregate; no writes, no live bureau contact. Time-to-response ignores `no_response` rows (no meaningful elapsed time) and negative elapsed values (data-entry guard). `_require_read` (READ_ONLY) gates the endpoint.

**Alternatives considered:** A materialized view like bureau/team reporting (deferred — recorded-response volume is low, a live aggregate is simpler and always fresh; can promote to an MV later if needed); computing rates in SQL (rejected — a pure Python helper is far easier to unit-test and reuse); measuring time-to-response from `recorded_at` only (rejected — the linked letter `sent_at` is the statutory clock start, with `last_dispute_date` as a fallback).

**Technical debt:** No date-range filter yet (analytics cover all recorded responses for the org). Favorable = deleted + corrected; `updated` is treated as partial and excluded from the favorable rate.

**Follow-up work:** Litigation-readiness evidence packet (slice 5); optional date-range / per-bureau slicing.

## Compliance intelligence — extended 45-day reinvestigation window (Phase 11)

**Decision:** Model the FCRA §611(a)(1)(B) 45-day reinvestigation window. `compute_reinvestigation_clock(...)` gains an `extended` flag that swaps the base 30-day window for 45 days (and carries the flag onto the returned `ReinvestigationClock`). A new pure `document_extends_window(clock_start_date, document_dates)` helper flags the extension when a case/account document was uploaded strictly after the clock start and on or before the initial 30-day deadline. `AccountService._case_document_dates(...)` projects `(account_id, created_at)` per case via a new lightweight `DocumentRepository.list_case_document_dates(...)`, and both the clock and readiness endpoints pass `extended` through. `AccountReinvestigationClock` gains `extended: bool`; the clock summary gains `extended_windows`.

**Reason:** §611(a)(1)(B) extends the CRA's reinvestigation window to 45 days when the consumer supplies additional relevant information during the initial 30-day period. Modeling this keeps the overdue/due-soon classification legally accurate — a tradeline that received supplemental documents mid-reinvestigation is not flagged overdue at day 31.

**Guardrails:** Still pure computation over stored data — no writes, no bureau contact. Case-level documents (no `account_id`) apply to every tradeline; account-linked documents apply only to that tradeline. Documents uploaded before the clock start, on the mailing day itself (treated as part of the initial packet), or after the 30-day deadline do not trigger the extension.

**Alternatives considered:** A per-account boolean/date column signalling the extension (rejected — derivable from existing document timestamps, avoids a migration + drift); loading full `Document` rows via `list_documents` (rejected — a `(account_id, created_at)` projection avoids pulling metadata for a read model); requiring an explicit staff toggle (deferred — auto-detection from uploaded documents is the least-surprising default; an explicit override can layer on later).

**Technical debt:** The extension signal is any case/account document in the window; it does not yet inspect document type (e.g. only counting evidence/identity docs) or link to the specific dispute letter that was answered. `dispute_round_count` still counts sent letters regardless of recipient.

**Follow-up work:** Per-org reinvestigation outcome analytics (slice 4); litigation-readiness evidence packet (slice 5).

## Compliance intelligence — per-letter multi-round reinvestigation clock (Phase 11)

**Decision:** Key the §611 reinvestigation clock off each actually-sent dispute letter's `sent_at` instead of the account's single `last_dispute_date`. A shared `AccountService._sent_letter_rounds_by_account(...)` helper returns, per account, the latest sent `sent_at` date and the count of sent letters. Both `get_case_reinvestigation_clock` and `get_case_redispute_readiness` now derive the clock start from `latest_sent_date or last_dispute_date`. `AccountReinvestigationClock` gains `clock_start_date` (the effective date the clock runs from) and `dispute_round_count` (number of sent rounds); readiness uses `max(observed_rounds, account.dispute_round)`.

**Reason:** Phase 10 slice 3 keyed the clock off `last_dispute_date`, so multi-round disputes only reflected the account's single stored date — a fresh re-dispute did not reset the 30-day window and old rounds could not be distinguished. Keying off the newest sent letter makes each round carry its own deadline (the documented slice-3 tech debt) and lets the readiness engine see the true round count.

**Guardrails:** Still pure computation over stored data — no writes, no bureau contact. Only `status == sent` letters with a non-null `sent_at` count; drafts and voided letters are ignored. When no letter has been sent the clock falls back to `last_dispute_date`, so existing behavior is preserved.

**Alternatives considered:** Persisting a `clock_start_date` column on the account (rejected — derivable from sent letters, avoids a migration + drift); using `created_at` of the letter (rejected — the mail date, not draft date, starts the statutory window); recomputing in each endpoint separately (rejected — a shared helper keeps the clock and readiness consistent, which the summary read model depends on).

**Technical debt:** The 45-day extended reinvestigation window is still not modeled (Phase 11 slice 3). `dispute_round_count` counts sent letters regardless of recipient (bureau vs furnisher), so a mixed set is not split per recipient.

**Follow-up work:** Extended 45-day window modeling (slice 3); per-org reinvestigation outcome analytics (slice 4); litigation-readiness evidence packet (slice 5).

## Compliance intelligence — per-case reinvestigation summary (Phase 10)

**Decision:** Add an aggregated per-case reinvestigation dashboard read model. `GET /accounts/reinvestigation-summary?case_id=` (service `get_case_reinvestigation_summary`) rolls up the §611 clock (slice 3), advisory readiness (slice 4), and recorded responses (slice 2) into one payload: totals (`total_accounts`, `disputed_accounts`, `total_responses`), the per-state `clock` summary, the per-action `readiness` summary, the earliest still-open `next_deadline` (+ account/creditor), `most_overdue_days`, and the high-priority `action_items`. Shipped `@verdin/api-client` types/helper and a `CaseReinvestigationSummaryCard` at the top of the case reinvestigation section.

**Reason:** After slices 2–4 the case detail page had three separate panels (responses, clock, readiness) but no single glance-able triage header. Operators needed one card answering "how many overdue, what's due next, what needs action" without scanning each panel. Aggregating the existing computations keeps a single source of truth.

**Guardrails:** Pure aggregation over the slice 3/4 read models — no new writes, no bureau contact. It reuses the same `AccountService` methods, so classification stays consistent with the detail panels.

**Alternatives considered:** A brand-new query that recomputes clock + readiness inline (rejected — duplicates slice 3/4 logic and risks drift); a materialized/persisted summary table (rejected — derivable and small, avoids a migration + staleness); putting the endpoint under `/cases/{id}` (rejected — the computation lives in `AccountService` alongside slices 3–4, so a `/accounts` query param keeps cohesion).

**Technical debt:** The summary calls `get_case_reinvestigation_clock` and `get_case_redispute_readiness` sequentially, so accounts + responses are queried twice per request; acceptable for typical case sizes but could be folded into a single pass if it becomes hot. `action_items` includes all high-priority entries with no cap.

**Follow-up work:** Version 5.17 governance sign-off + release notes + tag (slice 6). Live bureau response ingestion and automated re-dispute filing remain deferred to 5.18+.

## Compliance intelligence — re-dispute / escalation readiness (Phase 10)

**Decision:** Add an advisory re-dispute / escalation readiness read model. A pure `compute_redispute_readiness(...)` helper (in `accounts/redispute_readiness.py`) maps the §611 clock state, the latest recorded response outcome, the dispute round, and the account `risk_score` to a recommended `action` (`wait | prepare_initial | redispute | escalate_cfpb | escalate_attorney | resolved`) with a `priority` and human-readable `reason`. `GET /accounts/redispute-readiness?case_id=` returns a per-account list (high-priority first) plus a per-action `summary`. Shipped `@verdin/api-client` types/helper and a `CaseRedisputeReadinessPanel` on the case detail page.

**Reason:** The clock (slice 3) shows _when_ a reinvestigation is overdue but not _what to do next_. Operators had to eyeball the clock state and each response outcome to decide between re-disputing, filing a CFPB complaint, or consulting an attorney. A computed recommendation collapses that judgment into a triage list without adding state or automating any action.

**Guardrails (advisory only):** Pure computation over stored data — no writes, no bureau contact, and it never files a dispute or escalation. It only suggests a next step; a human always acts. `latest_outcome` falls back to the account's terminal `dispute_status` so legacy accounts (recorded via `dispute-response-received`) still yield a signal.

**Alternatives considered:** Coupling readiness to the full parsed-report litigation-strength model (rejected — requires ≥2 parsed reports; `risk_score` is always present and a good-enough strength proxy); persisting a recommendation column (rejected — derivable, avoids drift); folding it into the clock endpoint (rejected — keeps each payload focused and independently cacheable).

**Technical debt:** The attorney-vs-CFPB threshold is a single `risk_score ≥ 80` heuristic, not a calibrated model. Multi-round nuance is coarse (`dispute_round ≥ 2`), and MOV/§623 furnisher-direct paths are described in `reason` text rather than distinct actions.

**Follow-up work:** Per-case reinvestigation summary dashboard aggregating clock + readiness (slice 5); governance sign-off (slice 6).

## Compliance intelligence — §611 reinvestigation clock (Phase 10)

**Decision:** Add a computed FCRA §611 reinvestigation clock. A pure `compute_reinvestigation_clock(...)` helper (in `accounts/reinvestigation.py`) classifies a tradeline as `not_sent | awaiting | due_soon | overdue | responded` from its `last_dispute_date` and whether a real response was recorded. `GET /accounts/reinvestigation-clock?case_id=` returns a per-account list (deadline, days-remaining, state, response count) plus a per-state `summary`, sorted overdue-first. Shipped `@verdin/api-client` types/helper and a `CaseReinvestigationClockPanel` on the case detail page.

**Reason:** Slice 2 persists responses but nothing surfaced _when_ the 30-day reinvestigation window elapses or which tradelines need attention. Operators had only the per-account `overdue_investigation_scan` (task-based) and no case-level view. A read model over existing dispute dates + Phase 10 response records gives a live triage surface without new state.

**Guardrails:** Pure computation over stored data — no live bureau polling and no writes. `no_response` outcomes never count as `responded`, so a bureau that ignored a dispute still reads as `overdue`.

**Alternatives considered:** Persisting a per-account deadline column (rejected — derivable from `last_dispute_date`, avoids migration + drift); extending the worker `overdue_investigation_scan` (rejected — that mutates state and is per-account, not a read model); computing on the account list endpoint (rejected — a dedicated endpoint keeps the payload focused and cacheable).

**Technical debt:** The 45-day extended reinvestigation window (documents added mid-investigation) is not modeled — only the base 30 days. The clock keys off `last_dispute_date`, not the specific sent `dispute_letters.sent_at`, so multi-round disputes reflect only the latest round.

**Follow-up work:** Re-dispute / escalation readiness grounded in this clock + litigation strength (slice 4); per-case reinvestigation dashboard (slice 5).

## Compliance intelligence — dispute response intake & persistence (Phase 10)

**Decision:** Add an auditable dispute response record. `POST /accounts/{id}/dispute-responses` persists a row in a new `dispute_responses` table (migration `087_dispute_responses`) capturing `outcome` (`deleted | verified | updated | corrected | no_response | rejected`), `response_method` (`mail | portal | phone | email | other`), `response_date`, free-text `notes`, and optional links to a sent `dispute_letters` row and a case `documents` row. Terminal outcomes sync the account (`dispute_status`, `response_received`, `investigation_status`) and emit the existing `account_dispute_status_changed` timeline event; `GET /accounts/{id}/dispute-responses` lists records newest-first. Shipped `@verdin/api-client` types/helpers and an `AccountDisputeResponsesPanel` on the account detail page.

**Reason:** Before Phase 10 a dispute response was only a boolean `response_received` + a single `dispute_status` on the account, with the strict `AWAITING_RESPONSE → terminal` transition on `dispute-response-received`. That erased history (no per-letter record, no method/date/notes) and could not express `no_response` or `rejected`. A dedicated audit table gives the reinvestigation lifecycle (Phase 10 slices 3–5: §611 clock, re-dispute readiness, case dashboard) a durable, queryable foundation.

**Guardrails (staff-mediated):** Every record is entered by an operator; nothing is polled from a bureau. The new intake is additive — the legacy `dispute-response-received` transition is untouched. `no_response` never flips `response_received`.

**Alternatives considered:** Extending the account row with more response columns (rejected — no history, no per-letter granularity); reusing `dispute-response-received` with a wider enum (rejected — its strict `AWAITING_RESPONSE` precondition and idempotency semantics do not fit a free-form audit log); a JSONB blob on the account (rejected — not queryable for the upcoming §611 clock/read models).

**Technical debt:** The account-state sync maps `updated` to `CORRECTED` (no distinct tradeline-updated status yet). The intake path does not yet enforce that a linked letter is actually `sent`. Slice 3 will add the §611 reinvestigation-deadline computation on top of these records.

**Follow-up work:** §611 reinvestigation clock & no-response detection (slice 3); re-dispute / escalation readiness (slice 4); per-case reinvestigation dashboard (slice 5).

## Compliance intelligence — lock-aware dispute preparation (Phase 9)

**Decision:** Make bulk dispute preparation identity-theft-lock-aware. `prepare_case_credit_report_disputes` and `prepare_case_dispute_strategy_stage` now consult a new non-raising `DocumentService.identity_theft_lock_reason(...)` helper and _skip_ tradelines paused by an identity-theft indicator or a confirmed §605B claim, recording them in a `locked` array (`match_key`, `creditor_name`, `reason`) on `PrepareCreditReportDisputesResponse` / `PrepareDisputeStrategyStageResponse`. `assert_ordinary_dispute_allowed_for_account` was refactored to delegate to the same helper so the single-draft path keeps its `409`.

**Reason:** `create_dispute_letter_draft` already raised `409` for locked accounts, but the bulk prepare paths created an account first and then aborted the _entire_ batch on the first locked tradeline — leaving orphaned READY_FOR_DISPUTE accounts and blocking preparation of the remaining valid tradelines. Skipping locked tradelines (and surfacing them for §605B handling) keeps ordinary §611 accuracy disputes flowing while preventing identity-theft accounts from being mixed into the accuracy path.

**Guardrails:** Locked tradelines are never prepared as ordinary disputes; the response steers operators to the Identity Theft Case Center (§605B). No account is created for a locked tradeline. Behavior is advisory-surfacing only — it does not confirm or auto-label identity theft.

**Alternatives considered:** Keeping the batch-wide `409` (rejected — one locked account should not block unrelated disputes); silently dropping locked tradelines (rejected — operators need to see why); checking the lock only after account creation (rejected — leaves orphaned accounts).

**Technical debt:** The lock check runs per tradeline (one `list_account_reviews` read each) rather than batching a single lookup for the whole prepare call.

**Follow-up work:** Batch the lock lookup; capability-matrix 5.16 sign-off (checklist slice 6).

## Compliance intelligence — §605B submission-readiness audit (Phase 9)

**Decision:** Add an operator-gated §605B submission-readiness audit. `POST /cases/{case_id}/identity-theft/605b-readiness-runs` assesses the packet (confirmed-theft account count, attestation recorded, per-bureau coverage, and outstanding evidence-checklist items), persists the outcome to a new `identity_theft_605b_readiness_runs` table (`is_ready`, `packet_readiness`, `confirmed_count`, `attestation_recorded`, plus a JSONB `payload` snapshot with `bureaus`, `missing_evidence`, and `blocking_reasons`), and returns it; `GET .../605b-readiness-runs/latest` returns the most recent run (`404` if none). The Case Center surfaces a "Run §605B submission-readiness audit" action with a ready/not-ready badge and blocking-reason list.

**Reason:** Slice 2 lets operators bundle evidence and the Phase 8 manifest already computed a readiness percentage, but nothing recorded _when_ an investigator judged a packet submission-ready or _why_ it was not. An audit trail behind an explicit operator action gives compliance a reviewable record without ever contacting a bureau.

**Guardrails (audit only):** The run reuses the same completeness heuristics as the packet manifest and never submits to a bureau, never files, and never auto-classifies an account. It only records a staff-triggered assessment; live bureau submission remains deferred (5.17+).

**Alternatives considered:** Computing readiness inline on the packet download only (rejected — no persisted audit trail); a scheduled/unsupervised readiness sweep (rejected — must stay operator-gated); storing readiness on the incident row (rejected — a dedicated run table preserves history and matches the dispute-strategy-run pattern).

**Technical debt:** Blocking-reason strings are English and not yet localized. The run does not snapshot the exact exhibit selection (exhibit selection is still stateless per download).

**Follow-up work:** Lock-aware dispute preparation (checklist slice 5); optional readiness-run history list endpoint (schema `Fcra605bReadinessRunListResponse` already defined); capability-matrix 5.16 sign-off.

## Compliance intelligence — mixed-file / personal-info variation detection (Phase 9)

**Decision:** Add advisory mixed-file / personal-info variation detection to the identity-theft engine. `evaluate_identity_theft` now inspects `personal_information`, `consumer`, and `addresses` for multiple unmasked SSNs, multiple dates of birth, distinct surname variations, and a high number of address variations, emitting findings with a new `PERSONAL_INFO` detection source (rule IDs `identity_theft.personal_info.*`). A `summary.personal_info_indicators` counter surfaces the count in the Case Center.

**Reason:** Phase 8 detected fraud alerts, freezes, and tradeline warning signs but not commingled-identity signals. Mixed files are a distinct FCRA problem from identity theft and are resolved on the §611 path, so these findings must stay advisory and must **not** lock ordinary disputes (mixed_file is an unlock choice) or trip the identity-theft banner.

**Alternatives considered:** Reusing `REPORT_TEXT` (rejected — would flip the fraud-alert banner and lock disputes); auto-classifying as identity theft (rejected — confirmation stays a human gate).

**Technical debt:** Heuristics rely on parser field-name conventions; masked SSNs are ignored to avoid false positives. Address variation threshold is a fixed constant (5).

**Follow-up work:** Cross-bureau personal-info reconciliation; per-signal consumer confirmation UX.

## Compliance intelligence — §605B evidence exhibit bundling (Phase 9)

**Decision:** Extend the staff-mediated FCRA §605B block packet so operators can bundle staff-selected, case-scoped evidence documents into an `exhibits/` folder via repeated `document_id` query params on `GET /cases/{case_id}/identity-theft/605b-packet.zip`. Attachment is gated by MIME type (PDF/images/plain text), per-file size (15 MB), and total size (40 MB); skipped or missing documents are recorded with a reason in the packet manifest instead of failing the export.

**Reason:** Phase 8 shipped block letters plus a readiness manifest but only tracked evidence in a checklist. Investigators need the actual proof (police report, FTC report, ID) traveling with the packet, while keeping the "nothing auto-attached / nothing auto-submitted" guardrails.

**Alternatives considered:** Auto-bundle every case document (rejected — unreviewed PII exposure); a separate exhibits endpoint (rejected — packet should be a single reviewable artifact); storing an exhibit selection on the incident (deferred — query params keep the download stateless).

**Technical debt:** Exhibit selection is not persisted; size gating reads `file_size` then verifies actual bytes on fetch. No de-duplication across exhibits.

**Follow-up work:** Persisted exhibit sets; §605B submission-readiness audit (checklist slice 4); optional exhibit ordering.

## Compliance intelligence — Identity Theft Detection & Recovery (Phase 8)

**Decision:** Add Phase 8 as a first-class Compliance Intelligence Engine component with report/tradeline detection, consumer confirmation + attestation gates, Identity Theft Case Center persistence, FCRA §605B readiness (separate from §611), fraud-alert/freeze tracking, and ordinary dispute-letter pause (`409`) while indicators or confirmed claims lock an account.

**Reason:** Identity theft changes legal workflow, evidence, letter types, and remedy; mixing “not mine” with ordinary accuracy disputes is unsafe. Indicators must never auto-label accounts or generate sworn claims without consumer confirmation.

**Alternatives considered:** Fold into Metro 2 severity; portal-only confirmation later; defer Case Center persistence.

**Technical debt:** Some tradeline heuristics remain soft signals; bureau-specific freeze detection still relies on staff upsert + report phrases; portal consumer self-service confirmation deferred.

**Follow-up work:** Richer personal-info variation / mixed-file rules; wire prepare-disputes skip for locked match keys; optional §605B evidence exhibit bundling.

## Portal — identity-theft consumer confirmation

**Decision:** Expose read + confirm-only portal endpoints (`GET/POST /portal/cases/{id}/identity-theft-*`) that reuse the Phase 8 confirmation engine with portal case scoping and portal-user audit ids. Do not expose staff protection/incident write APIs to the portal.

**Reason:** Consumers must attest before confirmed identity-theft claims; staff-only Case Center remains for investigators.

**Alternatives considered:** Reuse staff `/cases` JWT endpoints from portal; defer portal entirely until §605B packet export.

**Technical debt:** Portal UI surfaces tradeline findings only (report-level banner still shown).

**Follow-up work:** Capability matrix 5.15 sign-off (checklist slice 5).

## Disputes — FCRA §605B block packet export

**Decision:** Add staff-mediated `GET /cases/{id}/identity-theft/605b-packet.zip` that emits a ZIP with README readiness manifest and per-bureau §605B block letters after consumer-confirmed identity theft (+ attestation). Returns `409` when no confirmed claims exist. Does not call bureau APIs.

**Reason:** Investigators need mail-ready block letters distinct from §611 dispute packets once theft is confirmed.

**Alternatives considered:** Reuse §611 mail-packet builder; auto-create dispute letter rows; live bureau submission.

**Technical debt:** Evidence documents are checklist-tracked, not yet auto-bundled as ZIP exhibits.

**Follow-up work:** Optional evidence exhibit bundling; live §605B filing deferred to 5.16+.

## Governance — Version 5.15 capability matrix sign-off

**Decision:** Mark v5.15.0 complete with scope doc, release notes, capability-matrix rows, checklist exit criteria, and roadmap release entry. §605B packet remains **Partial** (no live bureau calls).

**Reason:** Phase 8 product gates and docs must be discoverable as a shipped milestone after portal + packet slices.

**Alternatives considered:** Hold release notes until 5.16 live filing; fold §605B into dispute-letter lifecycle.

**Technical debt:** None new.

**Follow-up work:** 5.16 kickoff for deferred live §605B submission / evidence bundling when legal sign-off allows.

## Compliance intelligence — nest checklist PDF in packet ZIP

**Decision:** Always include the printable checklist PDF alongside the markdown root file in CFPB/attorney packet.zip exports (same checklist_export_filename(..., export_format="pdf") bytes as standalone /export?format=pdf).

**Reason:** Investigators downloading exhibit packets still needed a printable checklist without a second /export call.

**Alternatives considered:** Opt-in query flag; PDF-only packets; nest PDF under exhibits/.

**Technical debt:** Packet builds both markdown and PDF every time (small cost).

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — checklist PDF export

**Decision:** Add ormat=md|pdf (default md) on CFPB/attorney checklist /export endpoints, with reportlab PDF rendering and UI download buttons alongside markdown.

**Reason:** Investigators needed printable checklist PDFs without downloading the full exhibit packet ZIP.

**Alternatives considered:** Always PDF; nest checklist PDF only inside packet.zip; print-from-browser CSS.

**Technical debt:** PDF is plain wrapped text, not a typeset layout; packet ZIP still embeds markdown checklist only.

**Follow-up work:** Optional checklist.pdf inside packet.zip (done); OCR line refs; counsel transmit (deferred).

## Compliance intelligence — prepare tradeline via finding source refs

**Decision:** Carry source_document_id / radeline_index on strategy prep targets by parsing finding source_id refs (kind:bureau:rule#index@{document_id}), and prefer indexed tradeline lookup before creditor/masked matching when creating direct accounts.

**Reason:** Creditor match alone can collide when multiple similar tradelines exist; Metro 2/FCRA findings already encode the exact report index.

**Alternatives considered:** Creditor match only; require account-candidate import; store full tradeline snapshot on strategy rows.

**Technical debt:** Cross-bureau source ids still lack document refs; falls back to creditor matching.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — prepare metadata from parsed tradelines

**Decision:** When strategy stage prepare creates direct (non-match-key) accounts, resolve ccount_type / ccount_status / payment_status from a matching parsed tradeline when available, falling back to rule-ID heuristics for unknown fields.

**Reason:** Rule-only inference left many direct accounts as OTHER/UNKNOWN even when the case already had parsed report fields.

**Alternatives considered:** Require account-candidate import first; persist tradeline snapshot on strategy targets; document_id-only lookup without creditor match.

**Technical debt:** Match is creditor+masked (+bureau prefer); does not use finding radeline_index yet.

**Follow-up work:** Prefer document_id/tradeline_index from finding source refs (done); OCR line refs.

## Compliance intelligence — shared page-map lookup helper

**Decision:** Lift cache/locate/write-through into radeline_page_map.lookup_or_locate_tradeline_pages (plus lookup_cached_tradeline_pages / page_map_update_from_scan) and use it from compliance evidence links; excerpt path keeps cache-only + single-pass redact.

**Reason:** Evidence-link and excerpt builders duplicated page-map cache/merge logic.

**Alternatives considered:** Keep dual implementations; force evidence links through excerpt builder.

**Technical debt:** Evidence links still call locate_tradeline_pages separately from excerpt redaction.

**Follow-up work:** OCR line refs.

## Compliance intelligence — single-pass excerpt scan+redact

**Decision:** On page-map cache miss, uild_redacted_tradeline_excerpt discovers pages and redacts in one pdfplumber open, exposing scanned_page_numbers for write-through via page_map_update_from_scan. Cache hits still skip discovery.

**Reason:** Miss path previously called locate_tradeline_pages then opened pdfplumber again inside the excerpt builder.

**Alternatives considered:** Keep dual open; return page objects across helpers; merge evidence-link locate into excerpt API.

**Technical debt:** Evidence-link path still uses separate locate_tradeline_pages opens.

**Follow-up work:** OCR line refs; share single-pass helper with evidence links (done).

## Compliance intelligence — excerpt page-map write-through

**Decision:** On report-excerpt / mail-packet cache miss, call locate_tradeline_pages once, persist via merge_page_map_entry onto document_parsed_credit_reports.tradeline_page_map, and pass the located pages into uild_redacted_tradeline_excerpt as known_page_numbers.

**Reason:** Excerpt builders previously only read the page map; cache misses re-scanned without contributing back to the shared cache used by evidence links.

**Alternatives considered:** Write only on successful matches; keep dual scan inside excerpt builder; no-op when parsed-report row missing.

**Technical debt:** Locate + redaction still open pdfplumber separately; no write when parsed credit report row is absent.

**Follow-up work:** OCR line refs; coalesce locate/redact into one pdfplumber pass (done).

## Compliance intelligence — excerpt builder page-map reuse

**Decision:** Pass cached `tradeline_page_map` page numbers into `build_redacted_tradeline_excerpt` via optional `known_page_numbers`, skipping rediscovery scans when evidence-link page maps already exist for the document hash.

**Reason:** Report-excerpt / mail-packet attachments were re-scanning PDFs independently of the persisted page map.

**Alternatives considered:** Always re-scan; duplicate locate helpers; write-through from excerpt builder.

**Technical debt:** Excerpt path still opens pdfplumber for redaction geometry on known pages; empty cached maps force full-report fallback.

**Follow-up work:** OCR line refs; write-through from excerpt scans on cache miss (done).

## Compliance intelligence — persisted tradeline page maps

**Decision:** Persist on-demand tradeline page-scan results in `document_parsed_credit_reports.tradeline_page_map` (JSONB) keyed by document `file_hash`. Write-through cache in `GET /cases/{id}/compliance-evidence-links` when `include_page_scan=true`.

**Reason:** Repeated PDF downloads and text scans dominated evidence-link latency for large cases.

**Alternatives considered:** New page-map table; store on `document_metadata`; worker precompute; serve cache when scan skipped.

**Technical debt:** Map is document-scoped JSON; no per-entry index.

**Follow-up work:** OCR line refs; share cache with report-excerpt builder (done).

## Compliance intelligence — evidence page-scan query flag

**Decision:** Expose `include_page_scan` (default true) on `GET /cases/{case_id}/compliance-evidence-links` so investigators can skip on-demand PDF tradeline scans on large cases. When false, report links keep `page_confidence=deferred`.

**Reason:** Page scan was already optional inside the service (dispute strategy uses false) but the public endpoint always scanned.

**Alternatives considered:** Auto-skip above N findings; separate lightweight endpoint.

**Technical debt:** UI toggle is per-panel session only; no persisted preference.

**Follow-up work:** Persist page maps (done); OCR line refs.

## Compliance intelligence — checklist packet report-excerpt merge

**Decision:** Add opt-in include_report_excerpts=true on checklist packet.zip that merges consent-gated report-excerpt PDFs under exhibits/report-excerpts/ via AccountService.collect_case_report_excerpt_files. Missing signed consents return 422.

**Reason:** Investigators needed tradeline report excerpts alongside checklist handoff materials without defaulting consent gates onto basic exhibit packets.

**Alternatives considered:** Always merge; nest case-report-excerpts.zip; combine with mail-packet flag.

**Technical debt:** Requires a dispute letter on the account (same gate as standalone excerpt export).

**Follow-up work:** Counsel transmit workflow (deferred).

## Compliance intelligence — checklist packet mail-packet merge

**Decision:** Add opt-in include_mail_packets=true on checklist packet.zip that merges consent-gated mail-packet PDFs under exhibits/mail-packets/ via AccountService.collect_case_mail_packet_files. Missing signed consents return 422.

**Reason:** Investigators needed letterhead mail packets inside the checklist handoff ZIP without making consent a default gate for basic exhibit packets.

**Alternatives considered:** Always merge; soft-skip without consent; nest a second ZIP.

**Technical debt:** One latest letter per account; attachment resolution reused from mail export.

**Follow-up work:** Report-excerpt merge option; counsel transmit workflow.

## Compliance intelligence — checklist packet letter PDF format

**Decision:** Add letter_format=text|pdf (default ext) to checklist packet.zip letter exhibits. PDF uses the existing dispute-letter export renderer; mail-packet merge and consent gates remain deferred.

**Reason:** Investigators sometimes need printable letter PDFs in the handoff ZIP without opting into mail-packet consent flows.

**Alternatives considered:** Always PDF; mail-packet merge; separate download button only.

**Technical debt:** Letter PDFs are simple reportlab renders, not letterhead mail packets.

**Follow-up work:** Optional mail-packet PDF merge behind explicit consent (done).

## Compliance intelligence — checklist packet dispute-letter text

**Decision:** Include best-effort plain-text dispute letter exports under `exhibits/dispute-letters/` in checklist `packet.zip` when `include_letters=true` (default). Void letters are skipped; mail PDF / consent gates are not used.

**Reason:** Investigators needed correspondence in the handoff archive without inventing counsel transmission or mail-packet merging.

**Alternatives considered:** Always-on PDF letters; require mail consents; separate letters ZIP.

**Technical debt:** Text only (not letterhead PDF); capped at 50 letters per case.

**Follow-up work:** Optional mail-packet PDF merge behind explicit consent.

## Compliance intelligence — checklist override notes

**Decision:** Add optional `note` on `PUT .../checklist-overrides` (stored on `dispute_strategy_checklist_overrides`) and surface it as `override_note` on checklist items and markdown exports when `completion_source=staff`.

**Reason:** Investigators needed a short reason when marking items complete outside evidence heuristics.

**Alternatives considered:** Separate notes API; mandatory notes; free-form item comments.

**Technical debt:** Notes are soft-deleted with the override; no note history.

**Follow-up work:** Optional letter inclusion in packet ZIP (done).

## Compliance intelligence — checklist exhibit packet ZIP

**Decision:** Add `GET …/cfpb-checklist/packet.zip` and `GET …/attorney-checklist/packet.zip` that ZIP the enriched markdown checklist plus best-effort exhibits (identity, proof of address, credit reports, bureau responses).

**Reason:** Investigators needed a single handoff archive without inventing letter PDF rendering or auto-send.

**Alternatives considered:** Replace `.md` export; include dispute letters; single `?kind=` route.

**Technical debt:** Exhibit set is typed-document based; missing storage objects are skipped silently.

**Follow-up work:** Optional mail-packet PDF merge behind explicit consent.

## Compliance intelligence — checklist staff mark-complete overrides

**Decision:** Persist staff overrides in `dispute_strategy_checklist_overrides` and merge them into CFPB/attorney checklist GETs/exports via `completion_source=staff`. `PUT /cases/{case_id}/dispute-strategy/checklist-overrides` upserts or clears.

**Reason:** Investigators needed to mark items complete when evidence heuristics miss artifacts, without inventing a full checkbox workflow.

**Alternatives considered:** Two tables; free-text notes; bulk mark-all.

**Technical debt:** Overrides keyed by strategy `account_key`/`item_id` strings; orphaned if catalog changes.

**Follow-up work:** Override notes (done).

## Compliance intelligence — checklist packet markdown export

**Decision:** Add `GET …/cfpb-checklist/export` and `GET …/attorney-checklist/export` that download staff-mediated markdown packets from the same enriched checklist payloads as the JSON endpoints.

**Reason:** Investigators needed a copy/paste handoff file without inventing PDF layout or bundling exhibits.

**Alternatives considered:** ZIP of exhibits; reportlab PDF; single `?kind=` endpoint.

**Technical debt:** Export is text-only; narratives remain advisory until real artifacts exist.

**Follow-up work:** Override notes.

## Compliance intelligence — checklist completion status

**Decision:** Enrich CFPB and attorney checklist items at read time with `completion_status` (`present` | `missing` | `unknown`) derived from case exhibits, typed documents, parsed reports, and dispute letters. No migration or staff override API.

**Reason:** Investigators needed to see which packet items already exist on the case without inventing a checkbox store.

**Alternatives considered:** Persisted checklist_completions table; PDF packet export only.

**Technical debt:** Heuristic only; narratives and CFPB escalation files stay `unknown` until artifacts exist.

**Follow-up work:** Optional exhibit ZIP composition.

## Compliance intelligence — attorney-preserve checklist

**Decision:** Add `GET /cases/{case_id}/dispute-strategy/attorney-checklist` that lists required/optional packet items for strategy accounts (attorney_preserve is always recommended as hygiene). Near-ceiling scores are escalation-flagged.

**Reason:** Attorney-preserve was advisory only; investigators needed a concrete handoff checklist without transmitting materials to counsel automatically.

**Alternatives considered:** PDF packet export only; merge into CFPB checklist endpoint.

**Technical debt:** Checklist is heuristic; does not verify which exhibits are already on the case.

**Follow-up work:** Mark checklist items complete against case documents; optional packet PDF export (done).

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

**Follow-up work:** Pull status from parsed tradeline when document_id is known (done via creditor match); attorney-preserve packet export.

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

**Follow-up work:** Persist page maps; OCR line refs; optional query flag to skip scan on large cases (done).

## Compliance intelligence — dispute strategy generator

**Decision:** Add `GET /cases/{case_id}/dispute-strategy` that groups litigation-strength ranked issues by account and emits a deterministic four-stage plan (CRA dispute → furnisher → CFPB if warranted → attorney preserve). Reuses evidence checklist hints when available.

**Reason:** Phase 7 of the Consumer Credit Litigation Intelligence stack needs a tailored multi-stage plan, not a single generic letter.

**Alternatives considered:** LLM-generated freeform strategy; auto-creating dispute letter drafts per stage.

**Technical debt:** Stage thresholds are heuristic; CFPB/attorney gates are score-based only.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — per-account strategy stage prepare

**Decision:** Wire recommended CRA/furnisher stage rows to `POST /cases/{case_id}/dispute-strategy/prepare` with `account_keys` so investigators can prepare a single account’s letter from the plan card. Bulk CRA/furnisher buttons remain for all recommended accounts.

**Reason:** Changelog follow-up from the dispute strategy generator; stage actions should land in dispute letter prep without requiring a separate screen.

**Alternatives considered:** Only bulk prepare; auto-create letters without staff click.

**Technical debt:** CFPB/attorney stages stay advisory (checklist/packet flows only). Per-account prepare disabled while replaying a stored run.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — dispute strategy run audit

**Decision:** Persist each `GET /cases/{case_id}/dispute-strategy` response in `dispute_strategy_runs` (JSONB payload, org/case scoping, generator user, counts). Expose `GET /cases/{case_id}/dispute-strategy/runs/latest` for investigator audit replay.

**Reason:** Changelog follow-up from the dispute strategy generator slice; investigators need a durable record of what plan was generated and when.

**Alternatives considered:** Persist only on explicit POST; store only summary counts without full payload.

**Technical debt:** Checklist/prepare paths regenerate strategy without persisting additional runs.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — dispute strategy run UI audit

**Decision:** Show persisted `generated_at` and short `run_id` in the case dispute strategy panel when the API returns audit fields.

**Reason:** Changelog follow-up from strategy run persistence; investigators need visible proof of when the plan was generated.

**Alternatives considered:** Full run history table in UI (deferred); separate audit page.

**Technical debt:** UI shows latest load only, not historical runs.

**Follow-up work:** Replay prior run in panel (done via run history Replay).

## Compliance intelligence — dispute strategy run history

**Decision:** Add paginated `GET /cases/{case_id}/dispute-strategy/runs` returning summary rows (counts, generator, timestamps) without full strategy payloads.

**Reason:** Changelog follow-up from strategy run audit; investigators need to see prior generations without replaying full JSONB payloads.

**Alternatives considered:** Full payload in list; unbounded array on latest endpoint.

**Technical debt:** UI list shows summaries only until Replay fetches full payload.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

## Compliance intelligence — dispute strategy run replay

**Decision:** Add `GET /cases/{case_id}/dispute-strategy/runs/{run_id}` for org/case-scoped full-run replay, and wire a staff Replay action in the case strategy panel that overlays the stored plan without creating a new audit row.

**Reason:** Changelog follow-up from run history; investigators need to inspect prior plans without regenerating and re-persisting.

**Alternatives considered:** Replay only via latest; duplicate payload into browser cache.

**Technical debt:** Prepare/checklist actions still use live generation while replaying.

**Follow-up work:** OCR line refs; counsel transmit (deferred).

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
