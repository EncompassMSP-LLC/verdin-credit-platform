# Version 22.0 Scope & Deferrals

Formal scope for **Version 22.0 — Document Pipeline Hardening (Compliance Intelligence Phase 21)**. Builds on shipped **v21.0.0** Reinvestigation Operations Filters (Phase 20).

**Kickoff date:** 2026-07-18  
**Target:** Close non-blocked document-pipeline gaps found in pilot operations — widen `document_metadata.payment_status` so bureau status narratives persist, and add an operator-gated **re-parse credit report** action so staff can recover when OCR/classify completed but parse never ran — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

21.0 closed configuration and ingestion-list filter polish. Pilot use then exposed two owned-surface gaps: metadata extraction fails when bureau payment-status text exceeds `varchar(50)`, and there is no staff control to re-enqueue `document_credit_report_parse` after a missed worker run. Phase 21 is non-blocked hardening over the document pipeline the platform already owns.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                   | 22.0 target | Summary                                                                                      |
| ---- | --------------------------------------- | ----------- | -------------------------------------------------------------------------------------------- |
| 1    | Widen metadata payment_status           | Planned     | `document_metadata.payment_status` → varchar(255); models/worker tables aligned              |
| 2    | Operator re-parse credit report         | Planned     | Staff POST to enqueue parse when OCR text exists and document is classified as credit_report |
| 3    | Capability matrix / governance sign-off | Planned     | Scope, checklist, matrix rows, release notes                                                 |

## Shipped from 21.0 (foundation — do not regress)

All v21.0.0 APIs, UI, and `@verdin/api-client` functions remain production capabilities — per-recipient benchmark windows, ingestion bureau/status filters, and prior reporting surfaces. See [`version-21.0-scope.md`](version-21.0-scope.md).

## Explicit deferrals (not 22.0)

| Capability                                      | Deferred to | Reason                                                         |
| ----------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling        | 23.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution           | 23.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)       | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks | 23.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing          | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead          | 23.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs    | 23.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export           | Never       | Aggregate rates only; no client/account IDs in export          |

## Partial capability limits (22.0 targets)

### Widen metadata payment_status (Planned)

**Included:** Alembic widen of `document_metadata.payment_status` to 255 characters; API + worker column definitions updated so bureau status narratives (e.g. charged-off text) persist.

**Not included:** Normalizing payment status into enums; changing account import payment-status mapping.

### Operator re-parse credit report (Planned)

**Included:** Authenticated staff endpoint to enqueue `document_credit_report_parse` for an org-scoped document that has OCR text and `document_type=credit_report`; document detail UI action; no live bureau contact.

**Not included:** Bulk re-parse all case documents; automatic re-parse on worker restart; changing classifier output.

## Related documents

- [Version 22.0 completion checklist](../development/version-22.0-completion-checklist.md)
- [Version 21.0 scope](version-21.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
