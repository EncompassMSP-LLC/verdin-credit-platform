# Version 24.0 Scope & Deferrals

Formal scope for **Version 24.0 — Document Pipeline Recovery Parity (Compliance Intelligence Phase 23)**. Builds on shipped **v23.0.0** Document Pipeline Recovery Depth (Phase 22).

**Kickoff date:** 2026-07-21  
**Target:** Close remaining non-blocked document-pipeline recovery parity gaps — a **case-level bulk metadata re-extract** (parity with case bulk credit-report re-parse), and an operator-gated **re-classify** enqueue when OCR exists but classification was missed or stale — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

23.0 shipped single-document async metadata re-extract and case-level bulk credit-report re-parse. Staff still lack (1) case-scoped bulk metadata re-extract after schema/worker fixes, and (2) a recovery control to re-enqueue classification when OCR completed but type was never set. Phase 23 stays on owned document surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                   | 24.0 target | Summary                                                                            |
| ---- | --------------------------------------- | ----------- | ---------------------------------------------------------------------------------- |
| 1    | Case-level bulk metadata re-extract     | Shipped     | Staff enqueue `document_metadata_extract` for OCR'd docs on a case; Case UI action |
| 2    | Operator re-classify document enqueue   | Shipped     | Staff enqueue `document_classify` when OCR exists; Document Detail action          |
| 3    | Capability matrix / governance sign-off | Planned     | Scope, checklist, matrix rows, release notes                                       |

## Shipped from 23.0 (foundation — do not regress)

All v23.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — async metadata re-extract, case bulk credit-report re-parse, and prior reporting/compliance surfaces. See [`version-23.0-scope.md`](version-23.0-scope.md).

## Explicit deferrals (not 24.0)

| Capability                                        | Deferred to | Reason                                                         |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling          | 25.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution             | 25.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)         | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks   | 25.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing            | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead            | 25.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs      | 25.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export             | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse / re-extract on worker restart | 25.0+       | Ops preference; staff enqueue remains the recovery path        |

## Partial capability limits (24.0 targets)

### Case-level bulk metadata re-extract (Shipped)

**Included:** Authenticated staff endpoint to enqueue `document_metadata_extract` for each case document that has OCR text; Case Detail UI action summarizing queued/skipped counts; soft-skip documents without OCR.

**Not included:** Changing extraction rules; auto-retry loops; live bureau contact.

### Operator re-classify document enqueue (Shipped)

**Included:** Authenticated staff endpoint to enqueue `document_classify` for an org-scoped document that has OCR text; Document Detail UI action; no live bureau contact.

**Not included:** Bulk re-classify for all case documents; forcing a specific document type; unsupervised reclassification loops.

## Related documents

- [Version 24.0 completion checklist](../development/version-24.0-completion-checklist.md)
- [Version 23.0 scope](version-23.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
