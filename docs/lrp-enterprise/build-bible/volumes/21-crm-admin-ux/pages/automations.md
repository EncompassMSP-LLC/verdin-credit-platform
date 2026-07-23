# Page spec — Automations

| Field       | Value              |
| ----------- | ------------------ |
| Page name   | Automations        |
| Route       | `/crm/automations` |
| Volume      | 21                 |
| Status      | `draft`            |
| Actors      | Ops lead, admin    |
| Permissions | Automation admin   |

## 1. Purpose

Configure **safe** automations: reminders, digest sends, task nudges — never unsupervised bureau filing or score promises.

## 2. Entry / exit

- Entered from: nav
- Navigates to: automation detail

## 3. Layout

Rule list · enable/disable · audit of last runs.

## 4. Fields

| ID      | Label   | Type | Required | Source | Validation | PII |
| ------- | ------- | ---- | -------- | ------ | ---------- | --- |
| name    | Name    | text | y        | config | —          | N   |
| trigger | Trigger | enum | y        | config | allowlist  | N   |
| action  | Action  | enum | y        | config | allowlist  | N   |
| enabled | Enabled | bool | y        | config | —          | N   |

**Allowlist examples:** task due reminder; weekly partner digest; doc upload ack.  
**Denylist:** auto-file dispute; auto-publish score without review gate; guarantee emails.

## 5. Actions

| ID       | Control | Result  | API     | Audit        | Errors |
| -------- | ------- | ------- | ------- | ------------ | ------ |
| toggle   | Enable  | PATCH   | **yes** | 403 denylist |
| run_test | Test    | dry-run | POST    | yes          | —      |

## 6. States

Loading / empty / last-run error

## 7. Compliance copy

Page banner: “Automations cannot file disputes or promise approvals.”

## 8. Analytics events

`crm_automation_toggle`

## 9. Open questions

- [x] v1 → **allowlist toggles only; no rule builder** (P2-11)
