# Page spec — Calendar

| Field       | Value               |
| ----------- | ------------------- |
| Page name   | Calendar            |
| Route       | `/crm/calendar`     |
| Volume      | 21                  |
| Status      | `draft`             |
| Actors      | Staff               |
| Permissions | Calendar read/write |

## 1. Purpose

Schedule check-ins, partner calls, and review deadlines tied to cases.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Borrower workspace

## 3. Layout

Week/month view · event create · case link.

## 4. Fields

| ID        | Label | Type     | Required | Source | Validation | PII |
| --------- | ----- | -------- | -------- | ------ | ---------- | --- |
| title     | Title | text     | y        | form   | —          | N   |
| starts_at | Start | datetime | y        | form   | —          | N   |
| case_id   | Case  | uuid     | n        | form   | —          | N   |

## 5. Actions

| ID     | Control   | Result | API | Audit | Errors |
| ------ | --------- | ------ | --- | ----- | ------ |
| create | New event | POST   | yes | —     |
| edit   | Edit      | PATCH  | yes | —     |

## 6. States

Loading / empty / conflict

## 7. Compliance copy

—

## 8. Analytics events

`crm_calendar_view`

## 9. Open questions

- External Google/Outlook sync later
