# Page spec — Ops dashboard

| Field       | Value                      |
| ----------- | -------------------------- |
| Page name   | Ops dashboard              |
| Route       | `/crm/dashboard`           |
| Volume      | 21                         |
| Status      | `draft`                    |
| Actors      | All staff (scoped metrics) |
| Permissions | Reporting read             |

## 1. Purpose

At-a-glance ops health: open cases, SLA risks, referral backlog, review queue depth.

## 2. Entry / exit

- Entered from: login, nav
- Navigates to: Pipeline, Tasks, Referrals, Borrower workspace

## 3. Layout

KPI tiles · “Needs attention” lists · optional partner digest status.

## 4. Fields

| ID               | Label             | Type | Required | Source  | Validation | PII |
| ---------------- | ----------------- | ---- | -------- | ------- | ---------- | --- |
| open_cases       | Open borrowers    | int  | n/a      | metrics | —          | N   |
| sla_breach       | SLA at risk       | int  | n/a      | metrics | —          | N   |
| review_queue     | Pending reviews   | int  | n/a      | metrics | —          | N   |
| referral_backlog | Unacked referrals | int  | n/a      | metrics | —          | N   |

## 5. Actions

| ID         | Control    | Result        | API | Audit | Errors |
| ---------- | ---------- | ------------- | --- | ----- | ------ |
| open_queue | Tile / row | filtered list | —   | —     | —      |

## 6. States

Loading / empty org / error

## 7. Compliance copy

No “approvals this week” vanity metrics.

## 8. Analytics events

`crm_dashboard_view`

## 9. Open questions

- Align tiles with Vol 06 KPIs
