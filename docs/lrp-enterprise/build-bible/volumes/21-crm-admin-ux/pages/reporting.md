# Page spec — CRM Reporting

| Field       | Value                      |
| ----------- | -------------------------- |
| Page name   | Reporting                  |
| Route       | `/crm/reporting`           |
| Volume      | 21                         |
| Status      | `draft`                    |
| Actors      | Ops lead, admin, read-only |
| Permissions | Reporting read             |

## 1. Purpose

Org-internal readiness ops reports (volume, stage aging, partner funnel) — no cross-tenant benchmarks.

## 2. Entry / exit

- Entered from: nav
- Navigates to: filtered pipeline

## 3. Layout

Date range · KPI · breakdown tables · export aggregate CSV (no full PII dumps).

## 4. Fields

| ID       | Label | Type | Required | Source | Validation    | PII |
| -------- | ----- | ---- | -------- | ------ | ------------- | --- |
| from/to  | Range | date | y        | query  | —             | N   |
| group_by | Group | enum | n        | query  | stage/partner | N   |

## 5. Actions

| ID     | Control           | Result     | API     | Audit | Errors |
| ------ | ----------------- | ---------- | ------- | ----- | ------ |
| run    | Apply             | GET report | —       | —     | —      |
| export | Export aggregates | GET csv    | **yes** | 403   |

## 6. States

Loading / empty / error

## 7. Compliance copy

Exports are aggregate; client-level exports use gated package flow.

## 8. Analytics events

`crm_reporting_view` · `crm_reporting_export`

## 9. Open questions

- Align with platform reporting module
