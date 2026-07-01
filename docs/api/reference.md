# API Reference

# API Versioning

Base URL: `http://localhost:8000/api/v1`

All business endpoints are served under a version prefix (`/api/v1`, `/api/v2`, …). Multiple versions can run side by side during migration.

| Endpoint                   | Description                               |
| -------------------------- | ----------------------------------------- |
| `GET /api/versions`        | Discover supported API versions           |
| `GET /api/v1/docs`         | Swagger UI for v1 only                    |
| `GET /api/v1/openapi.json` | OpenAPI schema for v1 only                |
| `GET /docs`                | Combined API documentation (all versions) |
| `GET /openapi.json`        | Combined OpenAPI schema                   |

Interactive docs (all versions): `http://localhost:8000/docs`

Version-scoped docs: `http://localhost:8000/api/v1/docs`

## System

| Method | Path       | Auth   | Description  |
| ------ | ---------- | ------ | ------------ |
| GET    | `/health`  | Public | Health check |
| GET    | `/version` | Public | API version  |

## Authentication

| Method | Path            | Auth     | Description               |
| ------ | --------------- | -------- | ------------------------- |
| POST   | `/auth/login`   | Public   | Login with email/password |
| POST   | `/auth/refresh` | Public   | Refresh access token      |
| GET    | `/auth/me`      | Required | Get current user          |

### Login

```json
POST /api/v1/auth/login
{
  "email": "owner@verdin.demo",
  "password": "changeme123"
}
```

Response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Refresh Token

```json
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJ..."
}
```

### Current User

```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Cases

All case endpoints require authentication. Users are scoped to their organization.

| Method | Path               | Min role     | Description        |
| ------ | ------------------ | ------------ | ------------------ |
| POST   | `/cases`           | case_manager | Create a case      |
| GET    | `/cases`           | read_only    | List cases         |
| GET    | `/cases/{case_id}` | read_only    | Get case by ID     |
| PATCH  | `/cases/{case_id}` | case_manager | Update a case      |
| DELETE | `/cases/{case_id}` | admin        | Soft-delete a case |

### List query parameters

`page`, `page_size`, `search`, `status`, `stage`, `priority`, `assigned_user_id`, `sort_by`, `sort_order`

### Enums

- **status:** `open`, `active`, `on_hold`, `resolved`, `closed`
- **stage:** `intake`, `review`, `evidence_gathering`, `dispute_preparation`, `awaiting_response`, `monitoring`, `complete`
- **priority:** `low`, `medium`, `high`, `critical`

### Case accounts

| Method | Path                        | Min role  | Description              |
| ------ | --------------------------- | --------- | ------------------------ |
| GET    | `/cases/{case_id}/accounts` | read_only | List accounts for a case |

## Accounts

Credit tradeline accounts with intelligence scoring. All endpoints require authentication and organization scoping.

| Method | Path                                                             | Min role     | Description                               |
| ------ | ---------------------------------------------------------------- | ------------ | ----------------------------------------- |
| POST   | `/accounts`                                                      | case_manager | Create a credit account                   |
| GET    | `/accounts`                                                      | read_only    | List accounts                             |
| GET    | `/accounts/intelligence/summary`                                 | read_only    | Organization intelligence                 |
| GET    | `/accounts/{account_id}`                                         | read_only    | Get account by ID                         |
| GET    | `/accounts/{account_id}/dispute-draft`                           | read_only    | Preview rule-based dispute draft          |
|        | Query: `recipient_type` (`credit_bureau`, `furnisher`)           |              |                                           |
| GET    | `/accounts/{account_id}/dispute-letters`                         | read_only    | List saved dispute letter drafts          |
| GET    | `/accounts/{account_id}/dispute-letters/{letter_id}`             | read_only    | Get saved dispute letter details          |
| POST   | `/accounts/{account_id}/dispute-draft/letters`                   | case_manager | Save generated dispute draft              |
|        | Query: `recipient_type` (`credit_bureau`, `furnisher`)           |              |                                           |
| POST   | `/accounts/{account_id}/dispute-draft/review-task`               | case_manager | Create or reuse dispute draft review task |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/review-task` | case_manager | Create or reuse saved letter review task  |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/approve`     | case_manager | Approve a saved letter in review          |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/send`        | case_manager | Mark an approved letter as sent           |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/void`        | case_manager | Void an in-flight letter                  |
| POST   | `/accounts/{account_id}/dispute-awaiting-response`               | case_manager | Mark account awaiting CRA response        |
| PATCH  | `/accounts/{account_id}`                                         | case_manager | Update an account                         |
| DELETE | `/accounts/{account_id}`                                         | admin        | Soft-delete an account                    |

### List query parameters

`page`, `page_size`, `search`, `case_id`, `bureau`, `account_type`, `account_status`, `payment_status`, `dispute_status`, `min_risk_score`, `max_risk_score`, `min_readiness_score`, `dispute_ready`, `sort_by`, `sort_order`

### Intelligence summary query parameters

`case_id` (optional) — scope summary to a single case

### Enums

- **bureau:** `equifax`, `experian`, `transunion`, `innovis`, `unknown`
- **account_type:** `mortgage`, `auto`, `credit_card`, `collection`, `personal_loan`, `student_loan`, `medical`, `utility`, `telecom`, `other`
- **account_status:** `open`, `closed`, `collection`, `charge_off`, `repossession`, `foreclosure`, `transferred`, `paid`, `settled`, `deleted`, `unknown`
- **payment_status:** `current`, `late_30`, `late_60`, `late_90`, `late_120`, `charge_off`, `collection`, `repossession`, `foreclosure`, `unknown`
- **dispute_status:** `not_started`, `evidence_needed`, `ready_for_dispute`, `dispute_sent`, `awaiting_response`, `verified`, `corrected`, `deleted`, `escalated`, `monitoring`
- **investigation_status:** `none`, `pending`, `completed`, `overdue`, `escalated`

### Intelligence fields

Accounts automatically compute `risk_score`, `readiness_score`, `next_eligible_dispute_date`, and `ai_recommended_next_action` on create/update via `api/modules/accounts/intelligence.py`.

### Dispute draft preview

`GET /accounts/{account_id}/dispute-draft` returns a rule-based dispute draft for either a CRA tradeline investigation (`recipient_type=credit_bureau`, default) or a direct furnisher dispute (`recipient_type=furnisher`). The response includes structured `dispute_reason_suggestions`, `evidence_ready` / `missing_evidence` flags comparing the checklist to account and case fields, disputed item list, requested action, evidence checklist, and compliance notes for staff review. Drafts are generated on demand and are not persisted in this foundation slice.

`POST /accounts/{account_id}/dispute-draft/review-task` creates or reuses an active high-priority task linked to the account and draft source, giving staff an explicit workflow item before any dispute is sent.

`POST /accounts/{account_id}/dispute-draft/letters` saves the current rule-based preview as a `draft` dispute letter artifact. `GET /accounts/{account_id}/dispute-letters` lists saved drafts for the account. `GET /accounts/{account_id}/dispute-letters/{letter_id}` returns the full letter body, checklists, and metadata for a single artifact.

`POST /accounts/{account_id}/dispute-letters/{letter_id}/review-task` creates or reuses an active high-priority task for a saved letter, transitions `draft` letters to `review`, and links the task to the letter artifact.

`POST /accounts/{account_id}/dispute-letters/{letter_id}/approve` transitions a saved letter from `review` to `approved` and emits a timeline event. Letters already approved are returned idempotently; letters not in `review` return `422`.

`POST /accounts/{account_id}/dispute-letters/{letter_id}/send` transitions an approved letter to `sent`, records `sent_at`, updates the linked account to `dispute_sent` (including `last_dispute_date`, `dispute_round`, and `cra_dispute`), auto-creates a follow-up task (`accounts.dispute_letter_followup`) to track the CRA response, and emits timeline events. Letters already sent are returned idempotently and ensure the follow-up task exists; letters not in `approved` return `422`.

`POST /accounts/{account_id}/dispute-letters/{letter_id}/void` voids a letter in `draft`, `review`, or `approved`. Sent letters return `422`; already voided letters are idempotent.

`POST /accounts/{account_id}/dispute-awaiting-response` transitions an account from `dispute_sent` to `awaiting_response`, sets `investigation_status` to `pending` when unset, and emits a timeline event. Already `awaiting_response` accounts are idempotent; other statuses return `422`.

## Documents

Secure document storage with MinIO, SHA-256 hashing, versioning, and duplicate detection. See [`docs/epics/document-intelligence-platform.md`](../epics/document-intelligence-platform.md).

| Method | Path                                                               | Min role     | Description                                     |
| ------ | ------------------------------------------------------------------ | ------------ | ----------------------------------------------- |
| POST   | `/documents`                                                       | case_manager | Upload document (multipart)                     |
| GET    | `/documents`                                                       | read_only    | List documents                                  |
| GET    | `/documents/{document_id}`                                         | read_only    | Get document with versions                      |
| GET    | `/documents/{document_id}/duplicates`                              | read_only    | Get exact-hash duplicate group                  |
| PATCH  | `/documents/{document_id}`                                         | case_manager | Update metadata                                 |
| DELETE | `/documents/{document_id}`                                         | admin        | Soft-delete document                            |
| GET    | `/documents/{document_id}/ocr`                                     | read_only    | OCR status and extracted text                   |
| POST   | `/documents/{document_id}/ocr/retry`                               | case_manager | Re-queue OCR for failed document                |
| GET    | `/documents/{document_id}/download`                                | read_only    | Download file (optional `version`)              |
| POST   | `/documents/{document_id}/versions`                                | case_manager | Upload new version                              |
| GET    | `/documents/{document_id}/versions`                                | read_only    | List version history                            |
| GET    | `/documents/{document_id}/metadata`                                | read_only    | Get extracted metadata                          |
| POST   | `/documents/{document_id}/metadata/extract`                        | case_manager | Extract metadata from OCR text                  |
| GET    | `/documents/{document_id}/parsed-credit-report/account-candidates` | read_only    | Build account candidates from parsed tradelines |
| GET    | `/documents/{document_id}/parsed-credit-report/comparison`         | read_only    | Compare against previous report                 |
| POST   | `/documents/{document_id}/parsed-credit-report/review-task`        | case_manager | Create or reuse account candidate review task   |
| GET    | `/documents/{document_id}/resolutions`                             | read_only    | List entity resolution results                  |
| POST   | `/documents/{document_id}/resolutions/resolve`                     | case_manager | Run entity resolution                           |
| POST   | `/documents/{document_id}/resolutions/{resolution_id}/confirm`     | case_manager | Confirm or manually select match                |
| POST   | `/documents/{document_id}/resolutions/{resolution_id}/reject`      | case_manager | Reject proposed match                           |

**List query parameters:** `metadata_status` (`pending`, `extracted`, `failed`), `resolution_status` (`matched`, `ambiguous`, `unmatched`, `confirmed`, `rejected`).

### Upload (multipart form)

Fields: `file` (required), `title` (required), `case_id` (required), `description`, `account_id`

### List query parameters

`page`, `page_size`, `search`, `case_id`, `account_id`, `is_duplicate`, `sort_by`, `sort_order`

Duplicate detection: uploading a file with the same SHA-256 hash as an existing org document sets `is_duplicate: true` and `duplicate_of_id`. Use `GET /documents/{document_id}/duplicates` to review the canonical document and exact duplicate copies in the same organization.

Parsed credit report comparison: `GET /documents/{document_id}/parsed-credit-report/comparison` compares the selected report to the previous parsed report for the same case and bureau, matching tradelines by creditor plus masked account number.

Parsed tradeline account candidates: `GET /documents/{document_id}/parsed-credit-report/account-candidates` converts parser tradelines into normalized account-create candidates for staff review.

Parsed report review task: `POST /documents/{document_id}/parsed-credit-report/review-task` creates or reuses an active task linked to the document and parsed report, giving staff a workflow item for account candidate review.

## Timeline

| Method | Path             | Role      | Description                       |
| ------ | ---------------- | --------- | --------------------------------- |
| GET    | `/timeline`      | read_only | List timeline events (filterable) |
| GET    | `/timeline/{id}` | read_only | Get a single timeline event       |

**List query parameters:** `case_id`, `account_id`, `document_id`, `event_type`, `event_category`, `performed_by`, `occurred_from`, `occurred_to`, `sort_by`, `sort_order`.

Timeline events are **append-only** — no update or delete endpoints.

## Tasks

| Method | Path                   | Role         | Description                      |
| ------ | ---------------------- | ------------ | -------------------------------- |
| POST   | `/tasks`               | case_manager | Create a task                    |
| GET    | `/tasks`               | read_only    | List tasks (filterable)          |
| GET    | `/tasks/{id}`          | read_only    | Get task details                 |
| PATCH  | `/tasks/{id}`          | case_manager | Update a task                    |
| POST   | `/tasks/{id}/complete` | case_manager | Mark task completed              |
| POST   | `/tasks/{id}/reopen`   | case_manager | Reopen a completed/canceled task |
| DELETE | `/tasks/{id}`          | admin        | Soft-delete a task               |

**List query parameters:** `status`, `priority`, `case_id`, `account_id`, `document_id`, `assigned_user_id`, `source_module`, `due_before`, `due_after`, `overdue`, `search`, `sort_by`, `sort_order`, `page`, `page_size`.

Task lifecycle events (`TASK_CREATED`, `TASK_UPDATED`, `TASK_COMPLETED`, `TASK_REOPENED`, `TASK_DELETED`) are published to the timeline via the event bus.

## Dashboard

| Method | Path         | Role      | Description                         |
| ------ | ------------ | --------- | ----------------------------------- |
| GET    | `/dashboard` | read_only | Mission Control operations snapshot |

Returns a single payload with `overview`, `cases`, `accounts`, `documents`, `timeline`, `tasks`, `processing`, `performance`, and `alerts`. The response includes `generated_at` and `refresh_seconds` (default 30) for polling clients; the contract is designed for future WebSocket push without breaking changes.

**Card groups surfaced in the UI:**

| Section      | Metrics                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------- |
| Operations   | Open cases, active accounts, documents, tasks due today, overdue tasks                    |
| Processing   | OCR queue, OCR failed, classification/metadata/entity resolution pending                  |
| Performance  | Cases created/closed today, avg resolution time, docs/accounts per case                   |
| Intelligence | Classification confidence, entity resolution confidence, AI-ready, unresolved             |
| Timeline     | Recent activity with case and document context                                            |
| Alerts       | OCR failures, unmatched entities, documents requiring review, high-priority overdue tasks |

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

| Status | Meaning                           |
| ------ | --------------------------------- |
| 401    | Invalid or missing authentication |
| 403    | Insufficient permissions          |
| 404    | Resource not found                |
| 409    | Conflict (e.g., duplicate email)  |
| 422    | Validation error                  |
