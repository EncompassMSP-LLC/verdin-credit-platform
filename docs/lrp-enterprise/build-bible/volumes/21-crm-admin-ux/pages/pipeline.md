# Page spec — CRM Pipeline

| Field       | Value                      |
| ----------- | -------------------------- |
| Page name   | Pipeline                   |
| Route       | `/crm/pipeline`            |
| Volume      | 21                         |
| Status      | `review`                   |
| Actors      | Case manager, ops lead     |
| Permissions | Case write for stage moves |

## 1. Purpose

Board/table of borrowers by readiness stage for daily ops standups.

## 2. Entry / exit

- Entered from: nav, dashboard
- Navigates to: Borrower workspace

## 3. Layout

**Kanban** default (P2-2); assignee filter; partner filter. Stages: [STAGE-MODEL.md](../../../STAGE-MODEL.md).

## 4. Fields

| ID            | Label    | Type      | Required | Source    | Validation          | PII |
| ------------- | -------- | --------- | -------- | --------- | ------------------- | --- |
| borrower_name | Borrower | text      | y        | case      | —                   | Y   |
| stage         | Stage    | enum      | y        | case      | allowed transitions | N   |
| assignee      | Owner    | user      | n        | case      | —                   | N   |
| band          | Band     | enum/null | n        | readiness | —                   | N   |
| partner       | Partner  | text      | n        | referral  | —                   | N   |

## 5. Actions

| ID         | Control       | Result       | API   | Audit   | Errors      |
| ---------- | ------------- | ------------ | ----- | ------- | ----------- |
| move_stage | Drag / select | update stage | PATCH | **yes** | 409 invalid |
| open       | Card          | workspace    | —     | —       | —           |
| assign     | Assign        | set owner    | PATCH | yes     | —           |

## 6. States

Loading / empty / error

## 7. Compliance copy

Stage names must not say “Approved for loan.”

## 8. Analytics events

`crm_pipeline_view` · `crm_pipeline_stage_move`

## 9. Open questions

- [x] Canonical stage enum → [STAGE-MODEL.md](../../../STAGE-MODEL.md) (P0-3)
