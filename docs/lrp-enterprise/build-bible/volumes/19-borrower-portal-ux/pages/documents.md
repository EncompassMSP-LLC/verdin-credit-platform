# Page spec — Documents

| Field       | Value               |
| ----------- | ------------------- |
| Page name   | Documents           |
| Route       | `/portal/documents` |
| Volume      | 19                  |
| Status      | `draft`             |
| Actors      | Borrower            |
| Permissions | Own documents       |

## 1. Purpose

Upload and track documents requested for readiness / identity / dispute support.

## 2. Entry / exit

- Entered from: Dashboard, Tasks, nav
- Navigates to: Tasks

## 3. Layout

1. Requested checklist (missing / received / rejected)
2. Upload control
3. Uploaded list (name, type, date, status)

## 4. Fields

| ID       | Label  | Type | Required    | Source    | Validation       | PII |
| -------- | ------ | ---- | ----------- | --------- | ---------------- | --- |
| file     | File   | file | y on upload | client    | type/size limits | Y   |
| doc_type | Type   | enum | y           | checklist | —                | N   |
| status   | Status | enum | n/a         | API       | —                | N   |

## 5. Actions

| ID      | Control | Result               | API           | Audit | Errors  |
| ------- | ------- | -------------------- | ------------- | ----- | ------- |
| upload  | Upload  | create doc + process | POST document | yes   | 413/415 |
| replace | Replace | new version          | POST          | yes   | —       |

No delete of staff-locked evidence without request-to-staff.

## 6. States

- Empty checklist / upload in progress / virus/scan fail / success

## 7. Compliance copy

“Uploads are used to support your readiness file. Do not upload others’ documents.”

## 8. Analytics events

`portal_doc_upload_start` · `portal_doc_upload_success`

## 9. Open questions

- Max file size / types (align platform docs module)
