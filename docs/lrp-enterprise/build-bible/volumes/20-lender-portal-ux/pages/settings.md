# Page spec — Lender settings

| Field       | Value                      |
| ----------- | -------------------------- |
| Page name   | Settings                   |
| Route       | `/lender/settings`         |
| Volume      | 20                         |
| Status      | `draft`                    |
| Actors      | Branch admin (LO: limited) |
| Permissions | Admin for user mgmt        |

## 1. Purpose

Digest preferences, user invites, and partnership profile basics.

## 2. Entry / exit

- Entered from: nav
- Navigates to: —

## 3. Layout

Tabs: General · Users · Digests · Legal links.

## 4. Fields

| ID             | Label         | Type  | Required   | Source | Validation | PII |
| -------------- | ------------- | ----- | ---------- | ------ | ---------- | --- |
| digest_enabled | Weekly digest | bool  | y          | prefs  | —          | N   |
| digest_email   | Digest email  | email | if enabled | prefs  | email      | Y   |
| invite_email   | Invite LO     | email | on invite  | form   | email      | Y   |
| role           | Role          | enum  | on invite  | form   | —          | N   |

## 5. Actions

| ID          | Control     | Result       | API | Audit | Errors |
| ----------- | ----------- | ------------ | --- | ----- | ------ |
| save_digest | Save        | PATCH prefs  | yes | —     |
| invite      | Invite user | POST member  | yes | 409   |
| revoke      | Revoke      | PATCH member | yes | —     |

## 6. States

Loading / success / error

## 7. Compliance copy

Link partner terms / advisory notice.

## 8. Analytics events

`lender_settings_save` · `lender_user_invite`

## 9. Open questions

- SSO timing (later version)
