# Page spec — Reports

| Field       | Value                |
| ----------- | -------------------- |
| Page name   | Reports              |
| Route       | `/portal/reports`    |
| Volume      | 19                   |
| Status      | `review`             |
| Actors      | Borrower             |
| Permissions | Own report summaries |

## 1. Purpose

Show borrower-safe summaries of uploaded/analyzed credit reports (by bureau) and analysis status — not a raw Metro2 dump.

## 2. Entry / exit

- Entered from: nav, Readiness
- Navigates to: Documents (re-upload), Readiness

## 3. Layout

1. Bureau cards (EQ / EX / TU or available)
2. Analysis status
3. High-level counts (e.g. open collections) if product allows
4. Link to staff-mediated Q&A via Messages

## 4. Fields

| ID                    | Label   | Type     | Required | Source      | Validation    | PII |
| --------------------- | ------- | -------- | -------- | ----------- | ------------- | --- |
| bureau                | Bureau  | enum     | y        | reports API | —             | N   |
| pulled_or_uploaded_at | Date    | datetime | n        | reports     | —             | N   |
| analysis_status       | Status  | enum     | y        | reports     | pending/ready | N   |
| summary_metrics       | Metrics | object   | n        | reports     | redacted      | N   |

## 5. Actions

| ID     | Control               | Result      | API | Audit | Errors |
| ------ | --------------------- | ----------- | --- | ----- | ------ |
| upload | Upload report         | → Documents | —   | —     | —      |
| ask    | Question about report | → Messages  | —   | —     | —      |

No download of full bureau PDF to third parties from this page.

## 6. States

- Loading / empty (no reports) / error / partial bureau set

## 7. Compliance copy

“Summaries are for your readiness program and are not a credit score product from the bureaus.”

## 8. Analytics events

`portal_reports_view`

## 9. Open questions

- [x] Borrower download original bureau PDF → **no in v1; summaries only** (P2-6)
