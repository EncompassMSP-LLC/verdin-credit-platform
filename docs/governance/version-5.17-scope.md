# Version 5.17 Scope & Deferrals

Formal scope for **Version 5.17 — Dispute Response Intake & Reinvestigation Tracking (Compliance Intelligence Phase 10)**. Builds on shipped **v5.16.0** Identity-Theft Recovery Depth & §605B Evidence Bundling (Phase 9).

**Kickoff date:** 2026-07-15  
**Target:** Close the dispute loop after a letter is sent — capture auditable bureau/furnisher **responses**, track the FCRA §611 reinvestigation clock (including no-response / overdue), classify outcomes, and surface advisory re-dispute / escalation readiness — **without** live bureau response polling, automated re-dispute filing, or unsupervised escalation.

## Theme

Through 5.16 the platform detects issues, prepares §611 disputes and §605B packets, and tracks identity theft. Today a dispute response is only a boolean/outcome flag on the account (`verified | corrected | deleted`). Phase 10 turns that into an **auditable reinvestigation lifecycle**: each sent dispute letter gets persisted response records (outcome, response date, method, notes, optional linked correspondence document); the §611 30-day reinvestigation clock is computed and no-response/overdue cases are surfaced; outcomes roll up into a per-case reinvestigation read model; and results feed advisory re-dispute / CFPB / attorney escalation readiness grounded in existing litigation-strength and dispute-strategy signals.

All response recording is **staff-mediated** — operators enter what a consumer/office received by mail or portal. The platform never polls a bureau, never auto-files a re-dispute, and never escalates without a human.

## Epic outcomes (target)

| Epic | Theme                                          | 5.17 target | Summary                                                                        |
| ---- | ---------------------------------------------- | ----------- | ------------------------------------------------------------------------------ |
| 1    | Dispute response intake + persistence          | Planned     | Auditable per-letter response records (outcome, date, method, notes, doc link) |
| 2    | §611 reinvestigation clock & no-response       | Planned     | 30-day deadline computed from `sent_at`; overdue / awaiting-response detection |
| 3    | Reinvestigation outcome & re-dispute readiness | Planned     | Classify outcomes; advisory re-dispute / CFPB / attorney escalation signals    |
| 4    | Case reinvestigation summary read model + UI   | Planned     | Per-case reinvestigation dashboard (counts, deadlines, outcomes, next steps)   |
| 5    | Capability matrix / governance sign-off        | Planned     | Scope, checklist, matrix rows, release notes                                   |

## Shipped from 5.16 (foundation — do not regress)

All v5.16.0 APIs, feature flags, migrations, UI scaffolds, and `@verdin/api-client` functions remain production capabilities — §605B evidence exhibit bundling, mixed-file / personal-info variation signals, the §605B submission-readiness audit, and lock-aware dispute preparation. See [`version-5.16-scope.md`](version-5.16-scope.md).

## Explicit deferrals (not 5.17)

| Capability                                      | Deferred to | Reason                                                      |
| ----------------------------------------------- | ----------- | ----------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.18+       | Requires live bureau API access + legal/compliance sign-off |
| Automated re-dispute filing                     | 5.18+       | Depends on deferred live submission; stays a human gate     |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.18+       | Data governance and legal review not complete               |

## Partial capability limits (5.17 targets)

### Dispute response intake + persistence (Planned)

**Included:** A persisted `dispute_responses` audit table linked to a sent dispute letter (and its account/case), capturing outcome (`deleted | verified | updated | corrected | no_response | rejected`), response date, response method (`mail | portal | phone | email | other`), free-text notes, and an optional linked correspondence document; staff intake API + `@verdin/api-client` + Account/Case UI.

**Not included:** Automatic response capture from a bureau feed; parsing uploaded response letters with OCR/LLM (may be a later phase).

### §611 reinvestigation clock & no-response (Planned)

**Included:** Compute the FCRA §611 30-day (45-day where applicable) reinvestigation deadline from the letter `sent_at`; surface awaiting-response, due-soon, and overdue states; no-response handling as a first-class outcome.

**Not included:** Any automated action when a deadline passes; live reminders to bureaus.

### Reinvestigation outcome & re-dispute readiness (Planned)

**Included:** Classify recorded outcomes and derive advisory re-dispute / CFPB / attorney escalation readiness grounded in existing litigation-strength and dispute-strategy signals (e.g., verified-without-correction on a high-strength issue → escalation candidate).

**Not included:** Auto-generating or auto-filing the next dispute/escalation; overriding the identity-theft lock (5.16 lock-aware rules still apply).

### Case reinvestigation summary read model + UI (Planned)

**Included:** A per-case reinvestigation read model aggregating response records, deadlines, outcomes, and recommended next steps, with a Case Center surface.

**Not included:** Cross-case or cross-tenant analytics/benchmarks.

## Related documents

- [Version 5.17 completion checklist](../development/version-5.17-completion-checklist.md)
- [Version 5.16 scope](version-5.16-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
