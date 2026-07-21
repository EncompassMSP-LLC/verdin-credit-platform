# Version 23.0 Scope & Deferrals

Formal scope for **Version 23.0 — Document Pipeline Recovery Depth (Compliance Intelligence Phase 22)**. Builds on shipped **v22.0.0** Document Pipeline Hardening (Phase 21).

**Kickoff date:** 2026-07-21  
**Target:** Close remaining non-blocked document-pipeline recovery gaps — an operator-gated **async metadata re-extract** enqueue (parity with credit-report re-parse, so staff can recover after schema/worker fixes without hanging the API), and a **case-level bulk re-parse** for eligible credit reports — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

22.0 fixed metadata column width and added single-document credit-report re-parse. Pilot ops still need (1) a non-blocking way to re-run metadata extract after failed/stale extracts, and (2) a case-scoped bulk re-parse so staff are not forced to click re-parse on every bureau PDF. Phase 22 stays on owned document surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                   | 23.0 target | Summary                                                                                 |
| ---- | --------------------------------------- | ----------- | --------------------------------------------------------------------------------------- |
| 1    | Operator async metadata re-extract      | Planned     | Staff enqueue `document_metadata_extract` when OCR exists; Document Detail action       |
| 2    | Case-level bulk credit-report re-parse  | Planned     | Staff enqueue parse for all eligible credit reports on a case; Case Documents UI action |
| 3    | Capability matrix / governance sign-off | Planned     | Scope, checklist, matrix rows, release notes                                            |

## Shipped from 22.0 (foundation — do not regress)

All v22.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — widened `payment_status`, single-document re-parse, and prior reporting/compliance surfaces. See [`version-22.0-scope.md`](version-22.0-scope.md).

## Explicit deferrals (not 23.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 24.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 24.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 24.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 24.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs    | 24.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export           | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse on worker restart            | 24.0+       | Ops preference; staff enqueue remains the recovery path        |

## Partial capability limits (23.0 targets)

### Operator async metadata re-extract (Planned)

**Included:** Authenticated staff endpoint to enqueue `document_metadata_extract` for an org-scoped document that has OCR text; Document Detail UI action; keep existing sync `POST .../metadata/extract` for immediate extract when desired.

**Not included:** Bulk metadata extract for all case documents; changing extraction rules; auto-retry loops.

### Case-level bulk credit-report re-parse (Planned)

**Included:** Authenticated staff endpoint to enqueue `document_credit_report_parse` for each case document that has OCR text and `document_type=credit_report`; Case Documents UI action summarizing queued/skipped counts.

**Not included:** Automatic re-parse on upload; re-parse of non-credit_report types; live bureau contact.

## Related documents

- [Version 23.0 completion checklist](../development/version-23.0-completion-checklist.md)
- [Version 22.0 scope](version-22.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
