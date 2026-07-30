# Release Roadmap — Lending Readiness Platform™

Planned product releases on the shared Verdin monorepo (edition, not fork).

| Field        | Value                                                                                                               |
| ------------ | ------------------------------------------------------------------------------------------------------------------- |
| Current      | **Phase 4 / V1.2** — Customer Experience ([checklist](../../development/lrp-platform-v1.2-completion-checklist.md)) |
| Prior        | [`lrp-platform-v1.1.0`](../../release-notes/lrp-platform-v1.1.0.md)                                                 |
| Master epic  | [#419](https://github.com/EncompassMSP-LLC/verdin-credit-platform/issues/419)                                       |
| Phases       | [`lrp-platform-maturity-phases.md`](../../development/lrp-platform-maturity-phases.md)                              |
| Last updated | 2026-07-30                                                                                                          |

---

## Timeline

```text
lrp-platform-v1.0.0  ← RELEASED — production launch (M1–M6)
        ↓
lrp-platform-v1.1.0  ← RELEASED — evidence vault + case timeline + unwanted-call
        ↓
lrp-platform-v1.2.0  ← IN PROGRESS — Customer Experience (extend existing /portal)
        ↓
lrp-platform-v1.3.0  — Automation & Integrations
        ↓
lrp-platform-v1.4.0  — Analytics & Intelligence
        ↓
lrp-platform-v2.0.0  — Enterprise Platform
```

---

## v1.0 — Production launch (released)

Tag `lrp-platform-v1.0.0` · [notes](../../release-notes/lrp-platform-v1.0.0.md)

---

## v1.1 — Evidence-to-action depth (released)

Tag `lrp-platform-v1.1.0` @ `850e0430` · [notes](../../release-notes/lrp-platform-v1.1.0.md)

---

## v1.2 — Customer Experience (active)

Extend existing borrower portal — do not rebuild.

| Theme         | Focus                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------- |
| Accounts      | Self-serve password reset; invite email on provision                                                       |
| Notifications | Dedicated feed + read state                                                                                |
| Messaging     | Attachments (staff-gated)                                                                                  |
| UX polish     | Dashboard / progress parity with Vol 19                                                                    |
| Checklist     | [`lrp-platform-v1.2-completion-checklist.md`](../../development/lrp-platform-v1.2-completion-checklist.md) |

Partner builder/attorney/advisor portals remain PB-001–003 unless promoted.

---

## v1.3 — Automation & Integrations

Credit refresh scheduler, reminder engine, workflow/SLA orchestration, eSignature/SMS/calendar (feature-flagged).

---

## v1.4 — Analytics & Intelligence

Portfolio dashboards, dispute success / TTR / team KPIs, mortgage partner reporting, advisory AI summaries / recommendations / QA / risk (ADR-012 gated).

---

## v2.0 — Enterprise Platform

Org management depth, white-label themes, regional compliance packs, advanced RBAC, public API / webhooks / API keys / developer portal.

---

## Later / never (platform policy)

Live bureau soft-pull, unsupervised filing, cross-tenant marketplace, product fork — **not** scheduled.
