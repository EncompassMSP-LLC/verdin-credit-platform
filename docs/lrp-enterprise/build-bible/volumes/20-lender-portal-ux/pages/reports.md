# Page spec — Lender reports

| Field       | Value             |
| ----------- | ----------------- |
| Page name   | Reports           |
| Route       | `/lender/reports` |
| Volume      | 20                |
| Status      | `draft`           |
| Actors      | Branch admin, LO  |
| Permissions | Partnership       |

## 1. Purpose

Operational reports: referrals by stage, aging, package requests — aggregate where possible.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Pipeline filtered

## 3. Layout

Date range · KPI tiles · simple tables.

## 4. Fields

| ID           | Label  | Type   | Required | Source        | Validation | PII |
| ------------ | ------ | ------ | -------- | ------------- | ---------- | --- |
| from/to      | Range  | date   | y        | query         | —          | N   |
| stage_counts | Counts | object | n/a      | reporting API | —          | N   |

## 5. Actions

| ID  | Control     | Result  | API | Audit | Errors |
| --- | ----------- | ------- | --- | ----- | ------ |
| run | Apply range | refresh | GET | —     | —      |

## 6. States

Loading / empty period / error

## 7. Compliance copy

No outcome guarantees in report titles.

## 8. Analytics events

`lender_reports_view`

## 9. Open questions

- Align metrics with Vol 06
