# Version 26.0 Scope & Deferrals

Formal scope for **Version 26.0 — Document Pipeline Resolution & Operator Surfaces (Compliance Intelligence Phase 25)**. Builds on shipped **v25.0.0** Document Pipeline Recovery Bulk Closeout (Phase 24).

**Kickoff date:** 2026-07-21  
**Target:** Close remaining non-blocked document-pipeline **operator surface** gaps — a **Case Documents recovery panel** so bulk OCR/classify/metadata/re-parse actions are not gated on already-classified credit reports, and an operator-gated **async entity re-resolve** enqueue when metadata exists but resolution was missed or stale — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

25.0 closed case-scoped bulk recovery APIs, but Case Detail only mounts those controls inside Credit Report History (visible only when `document_type=credit_report` docs exist). Failed OCR and unclassified PDFs therefore cannot reach recovery UI. Staff also lack an async re-resolve control for entity resolution (sync `POST .../resolutions/resolve` only). Phase 25 stays on owned document surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                    | 26.0 target | Summary                                                                              |
| ---- | ---------------------------------------- | ----------- | ------------------------------------------------------------------------------------ |
| 1    | Case Documents recovery panel            | Shipped     | Case Detail panel hosting bulk recovery actions for any case documents               |
| 2    | Operator async entity re-resolve enqueue | Planned     | Staff enqueue `document_entity_resolve` when metadata exists; Document Detail action |
| 3    | Capability matrix / governance sign-off  | Planned     | Scope, checklist, matrix rows, release notes                                         |

## Shipped from 25.0 (foundation — do not regress)

All v25.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — case bulk re-classify, case bulk OCR retry, and prior recovery surfaces. See [`version-25.0-scope.md`](version-25.0-scope.md).

## Explicit deferrals (not 26.0)

| Capability                                        | Deferred to | Reason                                                         |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling          | 27.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution             | 27.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)         | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks   | 27.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing            | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead            | 27.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs      | 27.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export             | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse / re-extract on worker restart | 27.0+       | Ops preference; staff enqueue remains the recovery path        |
| Case-level bulk entity re-resolve                 | 27.0+       | Single-document async re-resolve first; bulk follows if needed |

## Partial capability limits (26.0 targets)

### Case Documents recovery panel (Shipped)

**Included:** Case Detail UI panel that lists case documents (or at least exposes recovery when any docs exist) and hosts staff bulk recovery actions already shipped (OCR retry, re-classify, metadata re-extract, credit-report re-parse) without requiring a classified credit report to be present.

**Not included:** Changing bulk API semantics; new worker jobs; live bureau contact.

### Operator async entity re-resolve enqueue (Planned)

**Included:** Authenticated staff endpoint to enqueue `document_entity_resolve` for an org-scoped document that has extracted metadata; Document Detail UI action; keep sync `POST .../resolutions/resolve`.

**Not included:** Case-level bulk re-resolve; forcing matches; unsupervised resolve loops; live bureau contact.

## Related documents

- [Version 26.0 completion checklist](../development/version-26.0-completion-checklist.md)
- [Version 25.0 scope](version-25.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
