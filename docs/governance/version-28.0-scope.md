# Version 28.0 Scope & Deferrals

Formal scope for **Version 28.0 — Monitoring Report Parser Depth (Compliance Intelligence Phase 27)**. Builds on shipped **v27.0.0** Dispute Playbook Depth & Case Entity Re-resolve (Phase 26) and the IdentityIQ monitoring-report parser shipped immediately after.

**Kickoff date:** 2026-07-22  
**Target:** Close remaining non-blocked **client-sourced monitoring report** gaps — harden IdentityIQ parsing with a golden fixture / expected-JSON regression, and add a **SmartCredit** monitoring / tri-merge parser sibling — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

CRO workflows rely on client-uploaded monitoring PDFs (IdentityIQ, SmartCredit, and similar), not bureau soft-pull APIs. IdentityIQ parsing shipped after 27.0, but lacks a golden expected-JSON regression and does not cover the common SmartCredit layout. Phase 27 stays on owned parser surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                     | 28.0 target | Summary                                                                             |
| ---- | ----------------------------------------- | ----------- | ----------------------------------------------------------------------------------- |
| 1    | IdentityIQ golden fixture regression      | Planned     | Golden OCR fixture + expected JSON so IdentityIQ parse regressions are caught in CI |
| 2    | SmartCredit monitoring / tri-merge parser | Released    | Detect SmartCredit branding; expand tri-bureau columns into per-bureau tradelines   |
| 3    | Capability matrix / governance sign-off   | Planned     | Scope, checklist, matrix rows, release notes                                        |

## Shipped from 27.0 (+ IdentityIQ foundation — do not regress)

All v27.0.0 APIs/UI remain production capabilities. The IdentityIQ parser (`identityiq` in `packages/report-parsers`) is treated as foundation for Phase 27 depth. See [`version-27.0-scope.md`](version-27.0-scope.md).

## Explicit deferrals (not 28.0)

| Capability                                        | Deferred to | Reason                                                         |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling          | 29.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution             | 29.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)         | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks   | 29.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing            | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead            | 29.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs      | 29.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export             | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse / re-extract on worker restart | 29.0+       | Ops preference; staff enqueue remains the recovery path        |
| New dispute scoring / LLM playbook engine         | 29.0+       | Compose existing engines first; no new recommendation backend  |
| IdentityIQ / SmartCredit live B2B pull APIs       | Never       | Not offered to CROs; client PDF import remains the path        |
| MyScoreIQ / other monitoring siblings             | 29.0+       | SmartCredit first; expand only after golden coverage exists    |

## Partial capability limits (28.0 targets)

### IdentityIQ golden fixture regression (Planned)

**Included:** Checked-in OCR (or synthetic) fixture plus expected `ParsedCreditReport` JSON (or equivalent assertions) exercised in CI so IdentityIQ layout/extract regressions fail loudly.

**Not included:** Live IdentityIQ portal scraping; API pulls; changing production parse semantics beyond fixture-driven fixes.

### SmartCredit monitoring / tri-merge parser (Released)

**Included:** SmartCredit-specific parser registered ahead of single-bureau parsers; detect branding / layout signals; expand tri-bureau account columns into per-bureau tradelines; force Experian/Equifax/TransUnion confidence to `0` on SmartCredit docs; unit tests + docs.

**Not included:** Live SmartCredit API integration; unsupervised import; PII export changes.

## Related documents

- [Version 28.0 completion checklist](../development/version-28.0-completion-checklist.md)
- [Version 27.0 scope](version-27.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
