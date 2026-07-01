# Version 4.5 Completion Checklist

Ordered path to **v4.5.0** — **complete**. Next milestone: **4.8 Operations**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “4.5 done”

- [x] All four epics below are **✅ or explicitly deferred to 4.8/5.0** with docs updated — see [`version-4.5-scope.md`](../governance/version-4.5-scope.md)
- [x] Capability matrix rows for 4.5 show **✅** (or **Partial** with written scope limits)
- [x] `v4.5.0` release notes + tag — [`docs/release-notes/v4.5.0.md`](../release-notes/v4.5.0.md), tag `v4.5.0`
- [x] E2E covers import → account → dispute draft → letter lifecycle
- [x] No **Planned** items remain that were promised for 4.5 in `docs/roadmap/README.md` (deferred items documented)

---

## Phase 1 — Recommended order (complete)

| Order | Slice                                    | Epic     | PR      |
| ----- | ---------------------------------------- | -------- | ------- |
| 1–12  | Dispute lifecycle + import wizard polish | 2–5, 1.8 | #61–#72 |

---

## Phase 2 — Recommended order (complete)

| Order | Slice                                           | Epic | Status |
| ----- | ----------------------------------------------- | ---- | ------ |
| 1     | E2E import → account → dispute letter lifecycle | 5.3  | ✅ #73 |
| 2     | Historical report comparison UI on account/case | 1.9  | ✅ #74 |
| 3     | Duplicate report detection UX                   | 1.10 | ✅ #75 |
| 4     | Capability matrix 4.5 sign-off + deferrals      | 5.4  | ✅ #76 |
| 5     | `docs/release-notes/v4.5.0.md`                  | 5.5  | ✅ #77 |
| 6     | Tag `v4.5.0`                                    | 5.6  | ✅ #78 |

LLM slices (4.6–4.8) require explicit approval or deferral before shipping.

---

## Explicitly not 4.5 (→ 4.8 / 5.0)

| Capability                         | Version | Why defer        |
| ---------------------------------- | ------- | ---------------- |
| Client portal                      | 4.8     | Roadmap          |
| Full reporting / ops dashboards    | 4.8     | Roadmap          |
| Notifications center (email/SMS)   | 4.8     | Infra            |
| SSO / MFA                          | 5.0     | Enterprise       |
| Compliance center / consent engine | 5.0     | Legal            |
| Autonomous dispute filing          | 5.0+    | Compliance gates |
