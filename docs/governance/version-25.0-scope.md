# Version 25.0 Scope & Deferrals

Formal scope for **Version 25.0 — Document Pipeline Recovery Bulk Closeout (Compliance Intelligence Phase 24)**. Builds on shipped **v24.0.0** Document Pipeline Recovery Parity (Phase 23).

**Kickoff date:** 2026-07-21  
**Target:** Close remaining non-blocked **case-scoped bulk** document-pipeline recovery gaps — a **case-level bulk re-classify** enqueue (parity with single-document re-classify and other case bulk recovery actions), and a **case-level bulk OCR retry** for failed eligible documents — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

24.0 shipped case bulk metadata re-extract and single-document re-classify. Staff still lack (1) case-scoped bulk re-classify after OCR completes without usable types across many PDFs, and (2) a case-scoped bulk OCR retry so failed extracts are not one-click-per-document. Phase 24 stays on owned document surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                   | 25.0 target | Summary                                                                    |
| ---- | --------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| 1    | Case-level bulk re-classify enqueue     | Shipped     | Staff enqueue `document_classify` for OCR'd docs on a case; Case UI action |
| 2    | Case-level bulk OCR retry (failed docs) | Shipped     | Staff enqueue OCR retry for failed eligible docs on a case; Case UI action |
| 3    | Capability matrix / governance sign-off | Shipped     | Scope, checklist, matrix rows, release notes                               |

## Shipped from 24.0 (foundation — do not regress)

All v24.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — case bulk metadata re-extract, single-document re-classify, and prior recovery surfaces. See [`version-24.0-scope.md`](version-24.0-scope.md).

## Explicit deferrals (not 25.0)

| Capability                                        | Deferred to | Reason                                                         |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling          | 26.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution             | 26.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)         | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks   | 26.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing            | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead            | 26.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs      | 26.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export             | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse / re-extract on worker restart | 26.0+       | Ops preference; staff enqueue remains the recovery path        |

## Partial capability limits (25.0 targets)

### Case-level bulk re-classify enqueue (Shipped)

**Included:** Authenticated staff endpoint to enqueue `document_classify` for each case document that has OCR text; Case Detail UI action summarizing queued/skipped counts; soft-skip documents without OCR; 503 when classification disabled.

**Not included:** Forcing a specific document type; unsupervised reclassification loops; live bureau contact.

### Case-level bulk OCR retry for failed documents (Shipped)

**Included:** Authenticated staff endpoint to re-enqueue OCR for each case document that is OCR-eligible and in a failed processing state; Case Detail UI action summarizing queued/skipped counts; soft-skip ineligible or non-failed docs.

**Not included:** Retrying successful OCR by default; unsupervised retry loops; changing OCR engines; live bureau contact.

## Related documents

- [Version 25.0 completion checklist](../development/version-25.0-completion-checklist.md)
- [Version 24.0 scope](version-24.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
