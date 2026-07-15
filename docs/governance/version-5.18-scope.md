# Version 5.18 Scope & Deferrals

Formal scope for **Version 5.18 — Reinvestigation Depth & Litigation Readiness (Compliance Intelligence Phase 11)**. Builds on shipped **v5.17.0** Dispute Response & Reinvestigation Tracking (Phase 10).

**Kickoff date:** 2026-07-15  
**Target:** Deepen the reinvestigation lifecycle shipped in 5.17 — track each dispute **round** on its own §611 clock (keyed off the letter `sent_at`), model the extended 45-day reinvestigation window, roll recorded outcomes into staff-facing trend analytics, and assemble an operator-gated litigation-readiness evidence packet for attorney handoff — **without** live bureau response polling, automated re-dispute filing, unsupervised escalation, or cross-tenant benchmarks.

## Theme

5.17 closed the dispute loop with per-account response records, a computed §611 clock, advisory re-dispute readiness, and a per-case summary. Two known limitations remain: the clock keys off the account's `last_dispute_date` (so only the latest round is reflected) and the base 30-day window ignores the FCRA §611(a)(1)(B) 45-day extension when documents are added mid-investigation. Phase 11 addresses both, then builds two depth surfaces on top: **outcome analytics** (how disputes resolve over time within an organization) and a **litigation-readiness packet** that bundles the §611/§623 willful-noncompliance evidence trail for a human attorney handoff.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau, never auto-files a re-dispute, never escalates without a human, and never shares data across tenants. Litigation-readiness packets are operator-gated exports — assembling evidence for a person to review and file, never filing anything.

## Epic outcomes (target)

| Epic | Theme                                        | 5.18 target | Summary                                                                             |
| ---- | -------------------------------------------- | ----------- | ----------------------------------------------------------------------------------- |
| 1    | Per-letter multi-round reinvestigation clock | Planned     | Track each sent dispute round on its own `sent_at`-keyed §611 deadline              |
| 2    | Extended 45-day reinvestigation window       | Planned     | Model the §611 45-day extension when supporting documents are added mid-window      |
| 3    | Reinvestigation outcome analytics read model | Planned     | Per-org outcome trends (deletion/verify/correction rates, time-to-resolution)       |
| 4    | Litigation-readiness evidence packet         | Planned     | Operator-gated §611/§623 willful-noncompliance evidence bundle for attorney handoff |
| 5    | Capability matrix / governance sign-off      | Planned     | Scope, checklist, matrix rows, release notes                                        |

## Shipped from 5.17 (foundation — do not regress)

All v5.17.0 APIs, migrations, UI, and `@verdin/api-client` functions remain production capabilities — dispute response intake/persistence (`dispute_responses`), the §611 reinvestigation clock, advisory re-dispute / escalation readiness, and the per-case reinvestigation summary. See [`version-5.17-scope.md`](version-5.17-scope.md).

## Explicit deferrals (not 5.18)

| Capability                                      | Deferred to | Reason                                                      |
| ----------------------------------------------- | ----------- | ----------------------------------------------------------- |
| Live bureau response ingestion / polling        | 5.19+       | Requires live bureau API access + legal/compliance sign-off |
| Automated re-dispute filing                     | 5.19+       | Depends on deferred live submission; stays a human gate     |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files |
| Cross-tenant reinvestigation-outcome benchmarks | 5.19+       | Data governance and legal review not complete               |
| Automated litigation filing / e-filing          | Never       | The packet is a human handoff; the platform never files     |

## Partial capability limits (5.18 targets)

### Per-letter multi-round reinvestigation clock (Planned)

**Included:** Compute the §611 deadline from each sent `dispute_letters.sent_at` so multi-round disputes each carry their own clock; the case clock/readiness read models reflect the latest open round while retaining prior rounds' history.

**Not included:** Any change to how disputes are sent; live reminders to bureaus.

### Extended 45-day reinvestigation window (Planned)

**Included:** Model the FCRA §611(a)(1)(B) 45-day extension when supporting documents are recorded during the reinvestigation window; the clock reflects the extended deadline where applicable.

**Not included:** Automatically deciding the extension applies without a recorded document trigger.

### Reinvestigation outcome analytics read model (Planned)

**Included:** A per-organization read model summarizing recorded outcomes over time — deletion / verification / correction rates, no-response frequency, and average time-to-resolution — with a staff-facing surface.

**Not included:** Cross-tenant benchmarks or any comparison against other organizations' data.

### Litigation-readiness evidence packet (Planned)

**Included:** An operator-gated export that bundles the reinvestigation evidence trail (sent letters, recorded responses, clock/deadline history, cross-bureau discrepancies) into a §611/§623 willful-noncompliance packet for a human attorney to review; builds on the 5.17 `escalate_attorney` readiness signal.

**Not included:** Auto-generating legal pleadings, auto-filing, or transmitting anything to a court, bureau, or attorney without a human action.

## Related documents

- [Version 5.18 completion checklist](../development/version-5.18-completion-checklist.md)
- [Version 5.17 scope](version-5.17-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
