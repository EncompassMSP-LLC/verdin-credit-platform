# Page spec — Permissions

| Field       | Value              |
| ----------- | ------------------ |
| Page name   | Permissions        |
| Route       | `/crm/permissions` |
| Volume      | 21                 |
| Status      | `draft`            |
| Actors      | Admin / owner      |
| Permissions | RBAC admin         |

## 1. Purpose

Assign CRM roles and capability flags to staff users.

## 2. Entry / exit

- Entered from: nav, Admin
- Navigates to: —

## 3. Layout

User table · role select · capability matrix (read-only help).

## 4. Fields

| ID      | Label | Type | Required | Source | Validation | PII |
| ------- | ----- | ---- | -------- | ------ | ---------- | --- |
| user_id | User  | uuid | y        | form   | —          | Y   |
| role    | Role  | enum | y        | form   | —          | N   |

## 5. Actions

| ID     | Control      | Result | API     | Audit | Errors |
| ------ | ------------ | ------ | ------- | ----- | ------ |
| save   | Save role    | PATCH  | **yes** | 403   |
| invite | Invite staff | POST   | yes     | —     |

## 6. States

Loading / error / success

## 7. Compliance copy

Least privilege; dispute approve separate from case manager if policy requires.

## 8. Analytics events

`crm_permissions_change`

## 9. Open questions

- Map 1:1 to platform roles vs CRM-specific
