# Release Notes — Lending Readiness Platform™ V1.1.0

**Edition:** Lending Readiness Platform™ (LRP) on the shared Verdin monorepo  
**Tag:** `lrp-platform-v1.1.0`  
**Commit:** `850e0430b34482abf0225833d38446a4fa938faf`  
**Date:** 2026-07-30  
**GitHub Release:** https://github.com/EncompassMSP-LLC/verdin-credit-platform/releases/tag/lrp-platform-v1.1.0  
**Checklist:** [`docs/development/lrp-platform-v1.1-completion-checklist.md`](../development/lrp-platform-v1.1-completion-checklist.md)  
**Prior:** [`lrp-platform-v1.0.0`](lrp-platform-v1.0.0.md)

## Summary

`lrp-platform-v1.1.0` closes the planned post–V1.0 product-depth sequence and is **formally released**.

```text
LRP-208A → LRP-208B → LRP-209A
```

Evidence-to-action workflow:

```text
Issue identified
→ supporting documents linked
→ activity recorded on the case timeline
→ unwanted-call incidents documented
→ advisory complaint guidance generated
→ staff reviews the draft
```

The edition remains a **shared-platform** Mortgage Partner / lending-readiness surface — not a fork — with staff-mediated workflows and no unsupervised bureau filing or automatic complaint submission.

## What shipped

| ID       | PR                                                                          | Deliverable                                                                                                                              |
| -------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| LRP-208A | [#414](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/414) | Evidence vault document↔issue links (`115_issue_evidence_links`); explainability `associated_documents`; CRO/CRM link-unlink             |
| LRP-208B | [#415](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/415) | Case action timeline reusing `timeline_events`; `ISSUE_EVIDENCE_LINKED`/`REMOVED`; `GET /timeline?source_id=`; CRO + CRM activity panels |
| LRP-209A | [#416](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/416) | Unwanted-call incidents (`116_unwanted_call_incidents`); prefs snapshot; advisory eligibility; staff-gated drafts; CRM borrower panel    |

## Migrations

| Revision                      | Purpose                           |
| ----------------------------- | --------------------------------- |
| `115_issue_evidence_links`    | Document↔issue vault associations |
| `116_unwanted_call_incidents` | Unwanted-call complaint incidents |

## Explicit non-goals (unchanged)

- Automatic FTC / CFPB / National DNC complaint submission (no outbound submit path; `external_submission_status` is staff attestation only)
- Liability, TCPA, or legal-outcome determinations from eligibility guidance
- Unsupervised dispute filing / auto-transmit of letters
- Live bureau soft-pull for lenders
- Forked Mortgage codebase

## Deferred backlog (not release blockers)

Tracked in [`product-backlog.md`](../lrp-enterprise/15-roadmap/product-backlog.md):

| ID     | Item                                                     |
| ------ | -------------------------------------------------------- |
| PB-011 | Draft workflow / delivery confirmation timeline emits    |
| PB-012 | Explicit issue-detected / issue-resolved timeline events |

V1.0 ops (security-officer signature + DR restore drill) remain on the [post-release hardening](../development/lrp-v1.0-post-release-hardening.md) checklist.

## Smoke validation

| Surface                               | Evidence                                                               |
| ------------------------------------- | ---------------------------------------------------------------------- |
| Evidence link/unlink + timeline emit  | `tests/documents/test_issue_evidence_links.py`                         |
| Issue-filtered timeline (`source_id`) | Covered by evidence-link timeline asserts + `GET /timeline?source_id=` |
| Unwanted-call CRUD + drafts           | `tests/clients/test_unwanted_call_incidents.py`                        |
| DNC-completed eligibility             | `call_after_dnc_completed` after `mark_dnc_completed` sets status      |
| Tenant isolation                      | Org-scoped repo queries; foreign-case document rejection tests         |
| CI                                    | Green on #414–#417 (including E2E)                                     |

## Related documents

- [V1.1 completion checklist](../development/lrp-platform-v1.1-completion-checklist.md)
- [V1.0 completion checklist](../development/lrp-platform-v1.0-completion-checklist.md)
- [Release roadmap](../lrp-enterprise/15-roadmap/release-roadmap.md)
- [Capability matrix](../governance/capability-matrix.md)
- [API reference](../api/reference.md)
- [Engineering changelog](../engineering/changelog.md)
- [Post-release hardening](../development/lrp-v1.0-post-release-hardening.md)
