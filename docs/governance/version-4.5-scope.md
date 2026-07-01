# Version 4.5 Scope & Deferrals

Formal sign-off for **v4.5.0 release candidate** scope. Capabilities marked **Partial** below are complete for the stated limits; remaining work is explicitly deferred.

**Sign-off date:** 2026-06-30  
**Release tag:** `v4.5.0` — [`docs/release-notes/v4.5.0.md`](../release-notes/v4.5.0.md)

## Epic outcomes

| Epic | Theme                      | v4.5.0 outcome | Summary                                                                                 |
| ---- | -------------------------- | -------------- | --------------------------------------------------------------------------------------- |
| 1    | Credit Report Intelligence | **✅ Shipped** | Import wizard, bureau parsers, comparison UI, duplicate detection, account candidates   |
| 2    | Workflow Automation        | **Partial**    | Event-driven auto-tasks; no BPM engine, cron scheduler, or notification delivery        |
| 3    | Dispute Generation         | **Partial**    | Rule-based letters, staff workflow through CRA outcome, text/PDF export; no auto-filing |
| 4    | AI Assistance              | **Partial**    | Heuristic + rules intelligence; LLM summaries and draft augmentation deferred           |
| —    | Client Experience          | **Deferred**   | Client portal, messaging, notifications → **4.8**                                       |

## Shipped in v4.5.0 (by capability)

| Capability                  | Status  | Scope included in v4.5.0                                                                  |
| --------------------------- | ------- | ----------------------------------------------------------------------------------------- |
| Credit Report Import Wizard | ✅      | Upload, OCR/classify pipeline tracking, parser review, comparison, duplicate UX, retry    |
| Bureau report parsers       | ✅      | Equifax, Experian, TransUnion structured parse + metadata bridge                          |
| Workflow auto-tasks         | Partial | Dispute draft/letter review, CRA follow-up, overdue investigation, parsed-report review   |
| Dispute letter lifecycle    | Partial | Draft → review → approve → send → awaiting response → outcome; furnisher template; export |
| AI recommendations          | Partial | Risk/readiness, dispute reason suggestions, missing evidence detector (rules)             |
| E2E automation gate         | ✅      | Import → account → dispute letter lifecycle in CI (`tests/e2e`)                           |

## Explicit deferrals

| Capability                         | Deferred to | Reason                                                         |
| ---------------------------------- | ----------- | -------------------------------------------------------------- |
| Client portal                      | 4.8         | Operations theme; requires auth and messaging infra            |
| Notifications (email/SMS/in-app)   | 4.8         | No delivery infrastructure in 4.5                              |
| Full workflow / BPM engine         | 4.8         | Event-driven tasks sufficient for RC; BPM is operations scale  |
| Scheduled jobs / SLA cron          | 4.8         | Overdue escalation uses read-time checks + tasks for RC        |
| `packages/job-orchestrator/`       | 4.8 / 5.0   | Worker jobs remain Redis-based; orchestration package deferred |
| LLM case summaries                 | 4.8         | Requires provider approval and PII policy                      |
| LLM document summaries             | 4.8         | Same as case summaries                                         |
| LLM dispute draft augmentation     | 4.8         | Rules remain default; LLM optional enhancement                 |
| LLM document classification        | 4.8         | Rules classifier shipped in 4.3; LLM augmentation deferred     |
| Innovis / secondary bureau parser  | 4.8         | Optional; Equifax/Experian/TransUnion cover primary bureaus    |
| Autonomous dispute filing          | 5.0+        | Compliance gates and consent engine required                   |
| SSO / MFA                          | 5.0         | Enterprise edition                                             |
| Compliance center / consent engine | 5.0         | Enterprise edition                                             |

## Partial capability limits (still ✅ for v4.5.0 RC)

### Workflow Automation (Partial)

**Included:** Task auto-creation from dispute drafts, saved letters, letter send, overdue CRA investigations, and parsed credit report review (`source_module` filters in UI).

**Not included:** Generic workflow definitions, scheduled reminder engine, in-app notification center, or cross-organization SLA dashboards.

### Dispute Generation (Partial)

**Included:** CRA and furnisher templates, persisted letters, review/approve/send/void, account `dispute_status` sync, response outcomes, text/PDF export, Playwright smoke.

**Not included:** Certified mail integration, autonomous filing, compliance checklist enforcement gate before send.

### AI Assistance (Partial)

**Included:** Heuristic intelligence scores, structured dispute reason suggestions, missing evidence flags on drafts.

**Not included:** Any external LLM calls, AI audit metadata for model/version (required when LLM ships in 4.8).

## Related documents

- [Capability matrix](capability-matrix.md) — layer readiness columns
- [Version 4.5 completion checklist](../development/version-4.5-completion-checklist.md) — release gate
- [Product roadmap](../roadmap/README.md) — version milestones
