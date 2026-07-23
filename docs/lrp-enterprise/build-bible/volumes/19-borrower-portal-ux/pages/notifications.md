# Page spec — Notifications

| Field       | Value                   |
| ----------- | ----------------------- |
| Page name   | Notifications           |
| Route       | `/portal/notifications` |
| Volume      | 19                      |
| Status      | `draft`                 |
| Actors      | Borrower                |
| Permissions | Own notifications       |

## 1. Purpose

List system and staff notifications; mark read; deep-link to source pages.

## 2. Entry / exit

- Entered from: shell bell, nav
- Navigates to: Tasks, Documents, Messages, Readiness

## 3. Layout

List + mark all read; unread emphasis.

## 4. Fields

| ID    | Label | Type  | Required | Source    | Validation    | PII |
| ----- | ----- | ----- | -------- | --------- | ------------- | --- |
| title | Title | text  | y        | notif API | —             | N   |
| body  | Body  | text  | n        | notif API | —             | N   |
| read  | Read  | bool  | y        | notif API | —             | N   |
| href  | Link  | route | n        | notif API | internal only | N   |

## 5. Actions

| ID       | Control       | Result               | API   | Audit | Errors |
| -------- | ------------- | -------------------- | ----- | ----- | ------ |
| open     | Row click     | navigate + mark read | PATCH | —     | —      |
| mark_all | Mark all read | batch                | PATCH | —     | —      |

## 6. States

- Loading / empty / error

## 7. Compliance copy

Notification templates use claim library (Vol 18).

## 8. Analytics events

`portal_notif_open` · `portal_notif_mark_all`

## 9. Open questions

- Push/email prefs live on Settings
