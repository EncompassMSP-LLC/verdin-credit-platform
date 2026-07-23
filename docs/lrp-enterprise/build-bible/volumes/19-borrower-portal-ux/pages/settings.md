# Page spec — Settings

| Field       | Value              |
| ----------- | ------------------ |
| Page name   | Settings           |
| Route       | `/portal/settings` |
| Volume      | 19                 |
| Status      | `draft`            |
| Actors      | Borrower           |
| Permissions | Own prefs          |

## 1. Purpose

Manage notification preferences, password/security, and legal links.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Profile, external legal URLs

## 3. Layout

1. Notifications toggles (email / SMS if offered)
2. Security (password change, MFA later)
3. Legal (privacy, terms)
4. Sign out

## 4. Fields

| ID          | Label         | Type | Required | Source | Validation     | PII |
| ----------- | ------------- | ---- | -------- | ------ | -------------- | --- |
| email_notif | Email updates | bool | y        | prefs  | —              | N   |
| sms_notif   | SMS updates   | bool | n        | prefs  | phone required | N   |

## 5. Actions

| ID              | Control         | Result        | API      | Audit | Errors |
| --------------- | --------------- | ------------- | -------- | ----- | ------ |
| save_prefs      | Save            | update prefs  | PATCH    | yes   | —      |
| change_password | Change password | auth flow     | auth API | yes   | —      |
| sign_out        | Sign out        | clear session | —        | —     | —      |

## 6. States

- Loading / save success / auth errors

## 7. Compliance copy

Link privacy policy / terms (Vol 17).

## 8. Analytics events

`portal_settings_save`

## 9. Open questions

- SMS provider readiness
