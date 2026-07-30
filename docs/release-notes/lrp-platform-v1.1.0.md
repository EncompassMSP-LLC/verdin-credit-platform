# Release Notes — Lending Readiness Platform™ V1.1.0

**Edition:** Lending Readiness Platform™ (LRP) on the shared Verdin monorepo  
**Tag:** `lrp-platform-v1.1.0`  
**Date:** 2026-07-30  
**Checklist:** [`docs/development/lrp-platform-v1.1-completion-checklist.md`](../development/lrp-platform-v1.1-completion-checklist.md)  
**Prior:** [`lrp-platform-v1.0.0`](lrp-platform-v1.0.0.md)

## Summary

`lrp-platform-v1.1.0` closes the planned post–V1.0 product-depth sequence:

```text
LRP-208A → LRP-208B → LRP-209A
```

The edition remains a **shared-platform** Mortgage Partner / lending-readiness surface — not a fork — with staff-mediated workflows and no unsupervised bureau filing or automatic complaint submission.

## What shipped

| ID       | PR                                                                          | Deliverable                                                                                                                              |
| -------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| LRP-208A | [#414](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/414) | Evidence vault document↔issue links (`115_issue_evidence_links`); explainability `associated_documents`; CRO/CRM link-unlink             |
| LRP-208B | [#415](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/415) | Case action timeline reusing `timeline_events`; `ISSUE_EVIDENCE_LINKED`/`REMOVED`; `GET /timeline?source_id=`; CRO + CRM activity panels |
| LRP-209A | [#416](https://github.com/EncompassMSP-LLC/verdin-credit-platform/pull/416) | Unwanted-call incidents (`116_unwanted_call_incidents`); prefs snapshot; advisory eligibility; staff-gated drafts; CRM borrower panel    |

## Explicit non-goals (unchanged)

- Automatic FTC / CFPB / National DNC complaint submission
- Liability, TCPA, or legal-outcome determinations from eligibility guidance
- Unsupervised dispute filing / auto-transmit of letters
- Live bureau soft-pull for lenders
- Forked Mortgage codebase

## Deferred (only if real workflow gaps appear)

| Item                                                     | Notes                                                                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Draft workflow / delivery confirmation timeline emits    | Existing CASE_/DOCUMENT_/DISPUTE_LETTER_/TASK_ events already appear on the case feed                   |
| Explicit issue-detected / issue-resolved timeline events | Optional enrichment — do not expand without demonstrated operator need                                  |
| V1.0 ops: security-officer signature + DR restore drill  | Still open on the [post-release hardening](../development/lrp-v1.0-post-release-hardening.md) checklist |

## Smoke validation

- API: `tests/documents/test_issue_evidence_links.py`, `tests/clients/test_unwanted_call_incidents.py`, timeline `source_id` coverage
- CI: full suite green on merge of #414–#416 (including E2E workflow)

## Related documents

- [V1.1 completion checklist](../development/lrp-platform-v1.1-completion-checklist.md)
- [V1.0 completion checklist](../development/lrp-platform-v1.0-completion-checklist.md)
- [Capability matrix](../governance/capability-matrix.md)
- [API reference](../api/reference.md)
- [Post-release hardening](../development/lrp-v1.0-post-release-hardening.md)
