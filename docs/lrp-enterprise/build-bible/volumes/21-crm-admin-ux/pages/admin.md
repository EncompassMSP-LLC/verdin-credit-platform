# Page spec — Org admin

| Field       | Value         |
| ----------- | ------------- |
| Page name   | Admin         |
| Route       | `/crm/admin`  |
| Volume      | 21            |
| Status      | `draft`       |
| Actors      | Owner / admin |
| Permissions | Org admin     |

## 1. Purpose

Org-level settings: branding links, feature flags, retention pointers, integration status.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Permissions, Automations

## 3. Layout

Sections: General · Features · Integrations · Danger zone (export/delete requests).

## 4. Fields

| ID            | Label            | Type | Required | Source | Validation | PII |
| ------------- | ---------------- | ---- | -------- | ------ | ---------- | --- |
| org_name      | Org display name | text | y        | org    | —          | N   |
| feature_flags | Flags            | map  | n        | org    | allowlist  | N   |

## 5. Actions

| ID   | Control | Result    | API     | Audit | Errors |
| ---- | ------- | --------- | ------- | ----- | ------ |
| save | Save    | PATCH org | **yes** | —     |

## 6. States

Loading / save success / error

## 7. Compliance copy

Feature flags cannot enable unsupervised filing.

## 8. Analytics events

`crm_admin_save`

## 9. Open questions

- Billing surface here vs separate
