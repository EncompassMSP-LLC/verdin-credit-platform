# Page spec — Borrower Dashboard

| Field       | Value                              |
| ----------- | ---------------------------------- |
| Page name   | Dashboard                          |
| Route       | `/portal` (or `/portal/dashboard`) |
| Volume      | 19                                 |
| Status      | `ready-for-build`                  |
| Actors      | Borrower                           |
| Permissions | Authenticated client; own org/case |

## 1. Purpose

Give the borrower a single glance at readiness band, next actions, and partner-aware progress without overwhelm.

## 2. Entry / exit

- Entered from: login, shell nav Home
- Navigates to: Readiness, Tasks, Documents, Learning, Messages

## 3. Layout

1. **Greeting** — first name + advisory one-liner
2. **Readiness summary** — band + last updated + CTA “View score”
3. **Next up** — top 1–3 open tasks
4. **Progress** — checklist % or task completion
5. **Learning nudge** — optional module card
6. **Messages preview** — unread count

No marketing promo strips in first viewport beyond brand shell.

## 4. Fields

| ID            | Label           | Type         | Required | Source          | Validation | PII |
| ------------- | --------------- | ------------ | -------- | --------------- | ---------- | --- |
| greet_name    | First name      | text         | n/a      | profile         | —          | Y   |
| score_band    | Readiness band  | enum display | n/a      | readiness API   | —          | N   |
| score_updated | Last updated    | datetime     | n/a      | readiness API   | —          | N   |
| next_tasks    | Next tasks      | list         | n/a      | tasks API       | max 3      | N   |
| progress_pct  | Progress        | percent      | n/a      | checklist/tasks | 0–100      | N   |
| unread        | Unread messages | int          | n/a      | messages API    | ≥0         | N   |

## 5. Actions

| ID       | Control           | Result                | API | Audit | Errors |
| -------- | ----------------- | --------------------- | --- | ----- | ------ |
| go_score | View score        | → Readiness           | —   | —     | —      |
| go_task  | Task row          | → Task detail / Tasks | —   | —     | —      |
| go_docs  | Upload docs       | → Documents           | —   | —     | —      |
| go_learn | Continue learning | → Learning            | —   | —     | —      |

## 6. States

- Loading: skeleton for summary + task list
- Empty (new): “We’re preparing your readiness view” + docs CTA
- Error: retry banner
- Success: n/a (read view)

## 7. Compliance copy

Footer/link: “Lending Readiness Score™ is advisory and not a loan approval or underwriting decision.”

## 8. Analytics events

`portal_dashboard_view` · `portal_dashboard_cta_score` · `portal_dashboard_cta_task`

## 9. Open questions

- [x] Exact band labels → Vol 22 / STAGE-MODEL
- [x] Partner name on dashboard → **yes, referring partner display name if present** (P2-3)
