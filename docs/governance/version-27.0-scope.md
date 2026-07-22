# Version 27.0 Scope & Deferrals

Formal scope for **Version 27.0 — Dispute Playbook Depth & Case Entity Re-resolve (Compliance Intelligence Phase 26)**. Builds on shipped **v26.0.0** Document Pipeline Resolution & Operator Surfaces (Phase 25) and the post-sign-off Case Dispute Playbook page.

**Kickoff date:** 2026-07-22  
**Target:** Close remaining non-blocked **investigator playbook** and **case-scoped entity recovery** gaps — deepen the Case Dispute Playbook with finding deep-links by `source_id`, and add **case-level bulk entity re-resolve** enqueue for documents with extracted metadata — **without** live bureau polling execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, or cross-tenant data sharing.

## Theme

26.0 shipped single-document async entity re-resolve and Case Documents recovery. The Dispute Playbook page (shipped immediately after) composes strategy + strength + reinvestigation summary, but investigators still cannot jump from a ranked issue to its Metro2/FCRA (or related) finding panel, and staff lack case-scoped bulk entity re-resolve when many documents missed the resolve job. Phase 26 stays on owned surfaces.

Everything remains **staff-mediated and advisory**. The platform still never polls a bureau without an explicit compliance gate, never auto-files a re-dispute, never escalates without a human, never files suit, and never shares data across tenants.

## Epic outcomes (target)

| Epic | Theme                                     | 27.0 target | Summary                                                                             |
| ---- | ----------------------------------------- | ----------- | ----------------------------------------------------------------------------------- |
| 1    | Playbook finding deep-links               | Shipped     | From playbook issues, link into Case Detail finding panels by `source_id` / anchors |
| 2    | Case-level bulk entity re-resolve enqueue | Shipped     | Staff enqueue `document_entity_resolve` for case docs with extracted metadata       |
| 3    | Capability matrix / governance sign-off   | Shipped     | Scope, checklist, matrix rows, release notes                                        |

## Shipped from 26.0 (+ playbook foundation — do not regress)

All v26.0.0 APIs/UI remain production capabilities. The Case Dispute Playbook (`/cases/{id}/dispute-playbook`) is treated as foundation for Phase 26 polish. See [`version-26.0-scope.md`](version-26.0-scope.md).

## Explicit deferrals (not 27.0)

| Capability                                        | Deferred to | Reason                                                         |
| ------------------------------------------------- | ----------- | -------------------------------------------------------------- |
| Live bureau response ingestion / polling          | 28.0+       | Requires live bureau API access + legal/compliance sign-off    |
| Automated re-dispute filing execution             | 28.0+       | Depends on deferred live submission; stays a human gate        |
| Unsupervised escalation (CFPB / attorney)         | Never       | Escalation is an advisory signal; a human decides and files    |
| Cross-tenant reinvestigation-outcome benchmarks   | 28.0+       | Data governance and legal review not complete                  |
| Automated litigation filing / e-filing            | Never       | The packet/export is a human handoff; the platform never files |
| Org-specific litigation PDF letterhead            | 28.0+       | Branding / template product decision                           |
| Automatic scheduled benchmark recompute jobs      | 28.0+       | Staff on-demand read models are sufficient                     |
| Response-level / PII benchmark export             | Never       | Aggregate rates only; no client/account IDs in export          |
| Automatic re-parse / re-extract on worker restart | 28.0+       | Ops preference; staff enqueue remains the recovery path        |
| New dispute scoring / LLM playbook engine         | 28.0+       | Compose existing engines first; no new recommendation backend  |

## Partial capability limits (27.0 targets)

### Playbook finding deep-links (Shipped)

**Included:** From Case Dispute Playbook issue rows, navigate to Case Detail finding anchors (`#metro2-findings`, `#fcra-findings`, etc.) with `finding_source` query param where panels can highlight or scroll; keep advisory tone.

**Not included:** New scoring engines; auto-file; unsupervised escalation.

### Case-level bulk entity re-resolve enqueue (Shipped)

**Included:** Authenticated staff endpoint to enqueue `document_entity_resolve` for each case document with extracted metadata; queued/skipped counts; Case Documents recovery (or Document) UI action; keep single-document `POST .../resolutions/reresolve`.

**Not included:** Forcing matches; unsupervised resolve loops; live bureau contact.

## Related documents

- [Version 27.0 completion checklist](../development/version-27.0-completion-checklist.md)
- [Version 26.0 scope](version-26.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
