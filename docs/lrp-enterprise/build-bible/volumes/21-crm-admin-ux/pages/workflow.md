# Page spec — Workflow

| Field       | Value                                 |
| ----------- | ------------------------------------- |
| Page name   | Workflow                              |
| Route       | `/crm/workflow`                       |
| Volume      | 21                                    |
| Status      | `draft`                               |
| Actors      | Ops lead, case managers               |
| Permissions | Workflow configure (lead); view (all) |

## 1. Purpose

Visualize standard readiness workflow stages and handoffs (intake → analysis → plan → partner update → package).

## 2. Entry / exit

- Entered from: nav
- Navigates to: Pipeline / SOPs docs link

## 3. Layout

Stage diagram · definition of done per stage · link to SOP IDs (Vol 14).

## 4. Fields

Read-only stage metadata unless admin edits labels (gated).

## 5. Actions

| ID        | Control     | Result       | API   | Audit | Errors |
| --------- | ----------- | ------------ | ----- | ----- | ------ |
| edit_meta | Edit labels | PATCH config | admin | yes   | —      |

## 6. States

Loading / error

## 7. Compliance copy

Stages cannot be named with guarantee language.

## 8. Analytics events

`crm_workflow_view`

## 9. Open questions

- Editable vs hardcoded v1
