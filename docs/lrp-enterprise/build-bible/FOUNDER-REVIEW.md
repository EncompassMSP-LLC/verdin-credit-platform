# Founder / compliance review packet

| Field    | Value                                                                              |
| -------- | ---------------------------------------------------------------------------------- |
| Status   | `accepted` (P0–P2)                                                                 |
| Created  | 2026-07-22                                                                         |
| Accepted | 2026-07-22 — founder: “accept and continue”                                        |
| Purpose  | Collapse open decisions so volumes can move `draft` → `review` → `ready-for-build` |

P0–P2 **Accepted** as proposed defaults. P3 remains parallel (counsel/ops).

---

## P0 — Blocks product identity & Stage 5

| ID   | Decision                     | Proposed default                                                                   | Accept / Change / Defer | Notes            |
| ---- | ---------------------------- | ---------------------------------------------------------------------------------- | ----------------------- | ---------------- |
| P0-1 | Borrower score display v1    | **Band-only** for borrowers; numeric optional for staff                            | **Accept**              | Vol 22           |
| P0-2 | Score bands                  | Building → Progressing → Near ready → Lending Ready                                | **Accept**              | Vol 22           |
| P0-3 | Canonical case stages        | See [STAGE-MODEL.md](./STAGE-MODEL.md)                                             | **Accept**              | Vol 14 / 21 / 22 |
| P0-4 | Compliance posture one-pager | Vol 18 text as written                                                             | **Accept**              | Sign Vol 18      |
| P0-5 | Unsupervised bureau filing   | **Never** in LRP v1–vN without new Bible amendment                                 | **Accept**              | Locked           |
| P0-6 | Stack                        | Edition on shared Verdin/`apps/api` + `apps/lrp-web` — **not** Supabase greenfield | **Accept**              | Vol 24           |
| P0-7 | Primary brand string         | Lending Readiness Partners                                                         | **Accept**              | Vol 16           |
| P0-8 | Product mark                 | Lending Readiness Score™ (advisory)                                                | **Accept**              | Vol 16           |

## P1 — Blocks GTM / commercial

| ID   | Decision                             | Proposed default                                        | Accept / Change / Defer | Notes       |
| ---- | ------------------------------------ | ------------------------------------------------------- | ----------------------- | ----------- |
| P1-1 | Website CTA                          | Book demo (Calendly or equivalent)                      | **Accept**              | Vol 07      |
| P1-2 | Public pricing page                  | Sales-led until 3 design partners live; then 3 tiers    | **Accept**              | Vol 04      |
| P1-3 | Borrower-direct purchase             | **No** in v1 (partner/operator referred only)           | **Accept**              | Vol 04      |
| P1-4 | Realtor access fee                   | Free to realtor when tied to paying lender/operator     | **Accept**              | Vol 04      |
| P1-5 | Beachhead geography                  | Founder home MSA first (fill name)                      | **Accept** (name TBD)   | Vol 01 / 07 |
| P1-6 | Co-brand with Ultimate Credit Repair | LRP = GTM brand; “Powered by” optional in footer        | **Accept**              | Vol 16      |
| P1-7 | Entity path                          | CPA/attorney consult this month; Georgia LLC hypothesis | **Accept**              | Vol 17      |

## P2 — Blocks UX build slices

| ID    | Decision                           | Proposed default                                                       | Accept / Change / Defer | Notes  |
| ----- | ---------------------------------- | ---------------------------------------------------------------------- | ----------------------- | ------ |
| P2-1  | Lender pipeline UI                 | **Table** default; kanban later                                        | **Accept**              | Vol 20 |
| P2-2  | CRM pipeline UI                    | **Kanban** default                                                     | **Accept**              | Vol 21 |
| P2-3  | Partner name on borrower dashboard | Show referring partner display name if present                         | **Accept**              | Vol 19 |
| P2-4  | Learning content v1                | Static modules in repo (markdown/JSON)                                 | **Accept**              | Vol 19 |
| P2-5  | Borrower messages                  | Single thread with staff                                               | **Accept**              | Vol 19 |
| P2-6  | Borrower report PDF download       | **No** full bureau PDF download in v1; summaries only                  | **Accept**              | Vol 19 |
| P2-7  | Task due dates borrower-editable   | **No**                                                                 | **Accept**              | Vol 19 |
| P2-8  | Export package                     | Watermarked PDF + audit; password optional later                       | **Accept**              | Vol 20 |
| P2-9  | CRM email v1                       | Templates + compliance lint; **block** forbidden phrases (no override) | **Accept**              | Vol 21 |
| P2-10 | CRM SMS v1                         | Defer live SMS until consent + provider; UI stub OK                    | **Accept**              | Vol 21 |
| P2-11 | Automations v1                     | Allowlist toggles only (digests, reminders); no rule builder           | **Accept**              | Vol 21 |
| P2-12 | LLM on day one                     | Deterministic-only path; LLM explain text **off** until org policy     | **Accept**              | Vol 22 |
| P2-13 | Dark mode                          | **No** for v1                                                          | **Accept**              | Vol 23 |
| P2-14 | Design tokens location             | App-local in `lrp-web` first; extract package if shared                | **Accept**              | Vol 23 |

## P3 — Ops / counsel (parallel; not coding blockers)

| ID   | Decision               | Proposed default                           | Accept / Change / Defer | Notes  |
| ---- | ---------------------- | ------------------------------------------ | ----------------------- | ------ |
| P3-1 | Domain                 | Fill primary + defensives                  | Open                    | Vol 16 |
| P3-2 | Federal TM filing      | After search clear — yes if budget allows  | Open                    | Vol 16 |
| P3-3 | Retention periods      | Counsel; interim follow platform policy    | Open                    | Vol 14 |
| P3-4 | CRO state licensing    | Counsel memo before public CRO advertising | Open                    | Vol 18 |
| P3-5 | Cloud region / RPO-RTO | TBD with eng; draft RPO/RTO ≤24h           | Open                    | Vol 24 |
| P3-6 | Error tracking         | Sentry (or equiv.) when staging stands up  | Open                    | Vol 24 |
| P3-7 | Named compliance owner | Founder until hire                         | **Accept**              | Vol 18 |

---

## Decision log

| Date       | ID         | Decision                                   | Decided by |
| ---------- | ---------- | ------------------------------------------ | ---------- |
| 2026-07-22 | P0-1…P0-8  | Accept all proposed                        | Founder    |
| 2026-07-22 | P1-1…P1-7  | Accept all proposed (MSA name TBD)         | Founder    |
| 2026-07-22 | P2-1…P2-14 | Accept all proposed                        | Founder    |
| 2026-07-22 | P3-7       | Accept founder as interim compliance owner | Founder    |

## Build gate

Stage 5 Epic **E0** (Vol 23 tokens + shells) is **`ready-for-build`**. Proceed per [Vol 25](./volumes/25-implementation-backlog/).
