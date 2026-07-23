# Volume 25 — Implementation backlog & Cursor prompts

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Status       | `ready-for-build`                                                     |
| Stage        | 5                                                                     |
| Owner        | Engineering                                                           |
| Last updated | 2026-07-22                                                            |
| Depends on   | Founder accepted P0–P2 ([FOUNDER-REVIEW.md](../../FOUNDER-REVIEW.md)) |

---

## 1. Rule

Implement only from volumes/pages marked **`ready-for-build`**. Cite the volume in every PR.

## 2. Suggested build order

| Epic                         | Cite      | Status          | Notes                                                          |
| ---------------------------- | --------- | --------------- | -------------------------------------------------------------- |
| E0 Tokens + shells           | Vol 23    | **done** (#346) | CSS tokens, light-only, advisory banner on portal/lender/CRM   |
| E1 Auth realms               | Vol 24    | **done** (#347) | Portal JWT + CRM/lender staff JWT with demo fallback           |
| E2 Borrower core             | Vol 19    | **done** (#348) | Dashboard, band-only readiness, tasks, docs                    |
| E3 Analysis pipeline         | Vol 22    | **done** (#350) | Credit-analysis runs + portal readiness publish                |
| E4 Lender referrals          | Vol 20    | **partial**     | E4.1 pipeline + E4.2 status PATCH/queue; new-referral deferred |
| E5 CRM workspace             | Vol 21    | **partial**     | E5.1 referral queue + E5.2 borrower list; workspace next       |
| E6 Partner digests / exports | Vol 20–21 | queued          | Gated exports + digests                                        |
| E7 Learning                  | Vol 19    | queued          | Static modules                                                 |
| E8 Automations (safe)        | Vol 21    | queued          | Allowlist only                                                 |
| E9 Hardening                 | Vol 18·24 | queued          | Audit, lint, DR drills                                         |

## 3. Slice template (per PR)

```text
Spec: Vol __ / page or section __
Keep | Refactor | Replace: __
API: __
UI: __
Tests: __
Docs: capability-matrix + api reference if needed
```

## 4. Cursor prompt starter

```text
Implement only what is specified in docs/lrp-enterprise/build-bible/volumes/<vol>/...
Do not add unsupervised bureau filing or guarantee copy.
Follow apps/api layered architecture and existing mortgage_partner patterns where applicable.
Cite the page spec in the PR body.
```

## 5. Definition of done (slice)

- [ ] Spec citation in PR
- [ ] Tests for API changes
- [ ] api-client updated if contract changes
- [ ] Compliance copy present where required
- [ ] Checklist / capability matrix updated when shipping

## 6. E0 acceptance notes

- Tokens: `apps/lrp-web/src/styles/tokens.css` + `tailwind.config.ts`
- Enums: `apps/lrp-web/src/lib/design-tokens.ts`
- Shells: Portal / Lender / CRM + advisory disclaimer
- Dark mode: forced light (P2-13)
