# Page spec — Readiness Score

| Field       | Value               |
| ----------- | ------------------- |
| Page name   | Readiness Score     |
| Route       | `/portal/readiness` |
| Volume      | 19                  |
| Status      | `review`            |
| Actors      | Borrower            |
| Permissions | Own case            |

## 1. Purpose

Explain the advisory Lending Readiness Score™, drivers, and what moves next — never as FICO or approval.

## 2. Entry / exit

- Entered from: Dashboard, nav
- Navigates to: Tasks (driver CTAs), Reports, Learning

## 3. Layout

1. Score / band hero (numeric optional per Vol 22)
2. “What this means” advisory copy
3. Driver list (positive / attention)
4. Trend / history (if versions exist)
5. CTA: related tasks

## 4. Fields

| ID          | Label         | Type                          | Required | Source    | Validation      | PII |
| ----------- | ------------- | ----------------------------- | -------- | --------- | --------------- | --- |
| score_value | Score         | number/null                   | n/a      | readiness | pending allowed | N   |
| score_band  | Band          | enum                          | n/a      | readiness | —               | N   |
| drivers     | Drivers       | list{label,severity,task_id?} | n/a      | readiness | —               | N   |
| version     | Score version | string                        | n/a      | readiness | —               | N   |
| as_of       | As of         | datetime                      | n/a      | readiness | —               | N   |

## 5. Actions

| ID               | Control              | Result           | API | Audit | Errors |
| ---------------- | -------------------- | ---------------- | --- | ----- | ------ |
| open_driver_task | Work on this         | → Tasks filtered | —   | —     | —      |
| view_reports     | View reports summary | → Reports        | —   | —     | —      |

## 6. States

- Loading: skeleton
- Empty/pending: “Analysis in progress — we’ll notify you”
- Error: retry
- Success: published score

## 7. Compliance copy

Primary disclaimer above fold (short) + expand for full text. Forbidden: “approved,” “pre-approved,” “guaranteed.”

## 8. Analytics events

`portal_readiness_view` · `portal_readiness_driver_click`

## 9. Open questions

- [x] Show numeric score vs band-only for v1 → **band-only** (FOUNDER-REVIEW P0-1)
