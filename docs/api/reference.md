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

| Method | Path                           | Min role     | Description               |
| ------ | ------------------------------ | ------------ | ------------------------- |
| POST   | `/cases`                       | case_manager | Create a case             |
| GET    | `/cases`                       | read_only    | List cases                |
| GET    | `/cases/{case_id}`             | read_only    | Get case by ID            |
| PATCH  | `/cases/{case_id}`             | case_manager | Update a case             |
| DELETE | `/cases/{case_id}`             | admin        | Soft-delete a case        |
| POST   | `/cases/{case_id}/llm-summary` | case_manager | Generate LLM case summary |

### List query parameters

`page`, `page_size`, `search`, `status`, `stage`, `priority`, `assigned_user_id`, `client_id`, `sort_by`, `sort_order`

### Create / update body

Optional `client_id` links a case to a `clients` record in the same organization. When `client_id` is set, `client_name` and `client_email` default from the client unless explicitly provided.

`POST /cases/{case_id}/llm-summary` invokes the configured LLM provider when `ENABLE_LLM` and ADR-012 gates pass. Case context is PII-scrubbed before the provider call; a timeline audit event records model, provider, and prompt hash.

### Enums

- **status:** `open`, `active`, `on_hold`, `resolved`, `closed`
- **stage:** `intake`, `review`, `evidence_gathering`, `dispute_preparation`, `awaiting_response`, `monitoring`, `complete`
- **priority:** `low`, `medium`, `high`, `critical`

### Case accounts

| Method | Path                        | Min role  | Description              |
| ------ | --------------------------- | --------- | ------------------------ |
| GET    | `/cases/{case_id}/accounts` | read_only | List accounts for a case |

## Clients

Client records and nested contacts for credit repair consumers. Organization-scoped; distinct from credit tradeline **accounts**.

| Method | Path                                 | Min role     | Description              |
| ------ | ------------------------------------ | ------------ | ------------------------ |
| POST   | `/clients`                           | case_manager | Create a client          |
| GET    | `/clients`                           | read_only    | List clients             |
| GET    | `/clients/{client_id}`               | read_only    | Get client by ID         |
| PATCH  | `/clients/{client_id}`               | case_manager | Update a client          |
| DELETE | `/clients/{client_id}`               | admin        | Soft-delete a client     |
| POST   | `/clients/{client_id}/contacts`      | case_manager | Add a contact            |
| GET    | `/clients/{client_id}/contacts`      | read_only    | List contacts for client |
| GET    | `/clients/{client_id}/contacts/{id}` | read_only    | Get contact by ID        |
| PATCH  | `/clients/{client_id}/contacts/{id}` | case_manager | Update a contact         |
| DELETE | `/clients/{client_id}/contacts/{id}` | admin        | Soft-delete a contact    |
| POST   | `/clients/{client_id}/portal-user`   | case_manager | Provision portal login   |
| GET    | `/clients/{client_id}/portal-user`   | read_only    | Get portal user metadata |
| PATCH  | `/clients/{client_id}/portal-user`   | case_manager | Update portal access     |
| DELETE | `/clients/{client_id}/portal-user`   | case_manager | Revoke portal access     |

Portal provisioning requires `ENABLE_CLIENT_PORTAL=true`.

**List query parameters (clients):** `page`, `page_size`, `search`, `status`, `sort_by`, `sort_order`

**List query parameters (contacts):** `page`, `page_size`, `search`, `relationship_type`, `is_primary`, `sort_by`, `sort_order`

**Enums:**

- **client status:** `active`, `inactive`
- **contact relationship:** `primary`, `spouse`, `attorney`, `authorized`, `other`

Only one contact per client may have `is_primary=true` at a time.

## Client portal auth

Requires `ENABLE_CLIENT_PORTAL=true`. Portal JWTs use `realm=portal` and include `client_id`; staff tokens use `realm=staff`. Realms are not interchangeable.

| Method | Path                   | Auth       | Description              |
| ------ | ---------------------- | ---------- | ------------------------ |
| POST   | `/portal/auth/login`   | public     | Portal user login        |
| POST   | `/portal/auth/refresh` | public     | Refresh portal tokens    |
| GET    | `/portal/auth/me`      | portal JWT | Current portal user info |

Read-only case progress for portal users. Cases match when `client_id` is set to the portal client, with email/name heuristics as fallback for unlinked cases.

| Method | Path                           | Auth       | Description                                                                           |
| ------ | ------------------------------ | ---------- | ------------------------------------------------------------------------------------- |
| GET    | `/portal/cases`                | portal JWT | List cases linked to portal client                                                    |
| GET    | `/portal/cases/{id}`           | portal JWT | Read-only case progress and disputes                                                  |
| GET    | `/portal/cases/{id}/documents` | portal JWT | List documents on a linked case                                                       |
| POST   | `/portal/cases/{id}/documents` | portal JWT | Upload document to a linked case (multipart: `file`, `title`, optional `description`) |

Portal uploads use the same MIME and size limits as staff `POST /documents`. Documents appear in staff document views and emit `PORTAL_DOCUMENT_UPLOADED` timeline events. Account-scoped uploads and portal document download are not included in this slice.

Secure messaging uses one thread per case (`message_threads` + `thread_messages`). Portal users can read and post on linked cases; staff reply via the case message-thread endpoints.

| Method | Path                          | Auth       | Description                           |
| ------ | ----------------------------- | ---------- | ------------------------------------- |
| GET    | `/portal/cases/{id}/messages` | portal JWT | List messages on a linked case thread |
| POST   | `/portal/cases/{id}/messages` | portal JWT | Send a secure portal message          |

Portal push notifications require `ENABLE_PORTAL_PUSH=true` and `ENABLE_CLIENT_PORTAL=true`. Staff replies on linked cases enqueue Web Push HTTP delivery attempts for active portal subscriptions via `pywebpush` + VAPID keys; delivery is audited in `portal_push_delivery_logs`. Configure `PORTAL_PUSH_PROVIDER=web_push` with `PORTAL_PUSH_VAPID_PUBLIC_KEY`, `PORTAL_PUSH_VAPID_PRIVATE_KEY`, and `PORTAL_PUSH_VAPID_SUBJECT`.

| Method | Path                              | Auth       | Description                           |
| ------ | --------------------------------- | ---------- | ------------------------------------- |
| GET    | `/portal/push/status`             | portal JWT | Push readiness and subscription count |
| POST   | `/portal/push/subscribe`          | portal JWT | Register Web Push subscription keys   |
| DELETE | `/portal/push/subscriptions/{id}` | portal JWT | Deactivate a push subscription        |

## Secure messaging (staff)

| Method | Path                                       | Min role     | Description                              |
| ------ | ------------------------------------------ | ------------ | ---------------------------------------- |
| GET    | `/messaging/status`                        | read_only    | Secure messaging capabilities overview   |
| GET    | `/cases/{case_id}/message-thread`          | read_only    | List case message thread (empty if none) |
| POST   | `/cases/{case_id}/message-thread/messages` | case_manager | Post a staff reply (creates thread)      |

Staff replies require the case to be linked to a client (`client_id`). Real-time push, attachments, and email bridge are deferred to 5.0+.

## Accounts

Credit tradeline accounts with intelligence scoring. All endpoints require authentication and organization scoping.

| Method | Path                                                             | Min role     | Description                                           |
| ------ | ---------------------------------------------------------------- | ------------ | ----------------------------------------------------- |
| POST   | `/accounts`                                                      | case_manager | Create a credit account                               |
| GET    | `/accounts`                                                      | read_only    | List accounts                                         |
| GET    | `/accounts/intelligence/summary`                                 | read_only    | Organization intelligence                             |
| GET    | `/accounts/{account_id}`                                         | read_only    | Get account by ID                                     |
| GET    | `/accounts/{account_id}/dispute-draft`                           | read_only    | Preview rule-based dispute draft                      |
|        | Query: `recipient_type` (`credit_bureau`, `furnisher`)           |              |                                                       |
| GET    | `/accounts/{account_id}/dispute-letters`                         | read_only    | List saved dispute letter drafts                      |
| GET    | `/accounts/{account_id}/dispute-letters/{letter_id}`             | read_only    | Get saved dispute letter details                      |
| GET    | `/accounts/{account_id}/dispute-letters/{letter_id}/export`      | read_only    | Download letter artifact (`format=text` or `pdf`)     |
| POST   | `/accounts/{account_id}/dispute-draft/letters`                   | case_manager | Save generated dispute draft                          |
|        | Query: `recipient_type` (`credit_bureau`, `furnisher`)           |              |                                                       |
| POST   | `/accounts/{account_id}/dispute-draft/review-task`               | case_manager | Create or reuse dispute draft review task             |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/review-task` | case_manager | Create or reuse saved letter review task              |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/approve`     | case_manager | Approve a saved letter in review                      |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/send`        | case_manager | Mark an approved letter as sent                       |
| POST   | `/accounts/{account_id}/dispute-letters/{letter_id}/void`        | case_manager | Void an in-flight letter                              |
| POST   | `/accounts/{account_id}/dispute-awaiting-response`               | case_manager | Mark account awaiting CRA response                    |
| POST   | `/accounts/{account_id}/dispute-response-received`               | case_manager | Record CRA outcome (`verified`/`corrected`/`deleted`) |
| POST   | `/accounts/{account_id}/dispute-investigation-overdue`           | case_manager | Mark investigation overdue + escalation task          |
| PATCH  | `/accounts/{account_id}`                                         | case_manager | Update an account                                     |
| DELETE | `/accounts/{account_id}`                                         | admin        | Soft-delete an account                                |

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

`GET /accounts/{account_id}/dispute-letters/{letter_id}/export?format=text|pdf` downloads a plain-text or PDF artifact for manual mailing. Includes subject, body, disputed items, requested action, evidence checklist, and compliance notes. Returns `Content-Disposition: attachment` with a generated filename.

`POST /accounts/{account_id}/dispute-awaiting-response` transitions an account from `dispute_sent` to `awaiting_response`, sets `investigation_status` to `pending` when unset, and emits a timeline event. Already `awaiting_response` accounts are idempotent; other statuses return `422`.

`POST /accounts/{account_id}/dispute-response-received` records a CRA investigation outcome for accounts in `awaiting_response`. Body: `{ "outcome": "verified" | "corrected" | "deleted" }`. Sets `response_received=true`, updates `dispute_status`, marks `investigation_status` as `completed`, refreshes intelligence, and emits a timeline event. Idempotent when the same outcome is already recorded; other statuses return `422`.

`POST /accounts/{account_id}/dispute-investigation-overdue` marks a pending CRA investigation as `overdue` when the statutory response window (`last_dispute_date` + 30 days) has passed without a recorded outcome. Auto-creates a high-priority escalation task (`accounts.dispute_investigation_overdue`), refreshes intelligence, and emits a timeline event. Idempotent when already overdue (ensures the escalation task exists). The worker job `overdue_investigation_scan` performs the same scan across all organizations on a schedule; `GET /accounts/{account_id}` no longer auto-escalates. Accounts not in `awaiting_response`, investigations not `pending`, or deadlines not yet passed return `422`.

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
| POST   | `/documents/{document_id}/llm-summary`                             | case_manager | Generate scrubbed document summary              |

**List query parameters:** `metadata_status` (`pending`, `extracted`, `failed`), `resolution_status` (`matched`, `ambiguous`, `unmatched`, `confirmed`, `rejected`).

`POST /documents/{document_id}/llm-summary` invokes the configured LLM provider when `ENABLE_LLM` and ADR-012 gates pass. Document context (metadata + truncated OCR text) is PII-scrubbed before the provider call; timeline event `DOCUMENT_LLM_SUMMARY_GENERATED` records model, provider, and prompt hash.

When `ENABLE_BATCH_LLM_SUMMARIES=true` (and `ENABLE_LLM=true`), staff can enqueue org-scoped batch summarization runs processed by the `batch_document_llm_summary` worker job.

| Method | Path                                    | Min role     | Description                                |
| ------ | --------------------------------------- | ------------ | ------------------------------------------ |
| GET    | `/documents/batch-llm-summaries/status` | case_manager | Batch summarization readiness and blockers |
| GET    | `/documents/batch-llm-summaries/runs`   | case_manager | Paginated batch run audit log              |
| POST   | `/documents/batch-llm-summaries/run`    | case_manager | Enqueue batch summarization worker job     |

`POST /documents/batch-llm-summaries/run` accepts optional `document_ids`; when omitted, up to 25 documents with OCR text are selected. Returns `404` when batch summarization is disabled.

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

## Notifications

In-app notifications for staff users. Recipients only see their own notifications.

| Method | Path                              | Role      | Description                         |
| ------ | --------------------------------- | --------- | ----------------------------------- |
| POST   | `/notifications`                  | admin     | Create notification for org user    |
| GET    | `/notifications`                  | read_only | List current user's notifications   |
| GET    | `/notifications/unread-count`     | read_only | Unread count for current user       |
| POST   | `/notifications/mark-all-read`    | read_only | Mark all notifications read         |
| POST   | `/notifications/{id}/read`        | read_only | Mark one notification read          |
| GET    | `/notifications/email/status`     | read_only | Email delivery readiness            |
| POST   | `/notifications/email/send`       | admin     | Send email to org user via provider |
| GET    | `/notifications/email/deliveries` | admin     | List email delivery audit logs      |
| GET    | `/notifications/sms/status`       | read_only | SMS delivery readiness              |
| POST   | `/notifications/sms/send`         | admin     | Send SMS to org user via provider   |
| GET    | `/notifications/sms/deliveries`   | admin     | List SMS delivery audit logs        |

**List query parameters:** `unread_only`, `category`, `sort_by`, `sort_order`, `page`, `page_size`.

`/notifications/email/status` reports `enabled`, `ready`, configured provider metadata, and blockers based on `ENABLE_EMAIL_DELIVERY` plus email provider env vars.

`POST /notifications/email/send` delivers via the configured provider (`smtp` or `sendgrid`) when ready. Each attempt is persisted to `email_delivery_logs`. Set `deliver_email: true` on `POST /notifications` to send email alongside the in-app notification.

Provider env vars: `EMAIL_PROVIDER`, `EMAIL_FROM_ADDRESS`, `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_SMTP_USERNAME`, `EMAIL_SMTP_PASSWORD`, `EMAIL_SENDGRID_API_KEY`.

`/notifications/sms/status` reports `enabled`, `ready`, configured provider metadata, and blockers based on `ENABLE_SMS_DELIVERY` plus SMS provider env vars.

`POST /notifications/sms/send` delivers via the configured provider (`twilio`) when ready. Recipients must have `phone_number` set on their user record. Each attempt is persisted to `sms_delivery_logs`. Set `deliver_sms: true` on `POST /notifications` to send SMS alongside the in-app notification.

SMS provider env vars: `SMS_PROVIDER`, `SMS_FROM_NUMBER`, `SMS_TWILIO_ACCOUNT_SID`, `SMS_TWILIO_AUTH_TOKEN`.

### Marketing SMS campaigns

Marketing SMS campaign enqueue scaffold with org-scoped run audit log. Requires `ENABLE_SMS_DELIVERY=true` and `ENABLE_SMS_MARKETING_CAMPAIGNS=true`. When `ENABLE_SMS_MARKETING_DELIVERY=true`, `POST /notifications/sms-campaigns/run` creates a pending run and enqueues the `sms_marketing_campaign_delivery` worker job; delivery attempts are persisted to `sms_delivery_logs` with `campaign_run_id`. Without the delivery flag, enqueue remains audit-only (recipient counts, no Twilio calls).

| Method | Path                                  | Min role  | Description                               |
| ------ | ------------------------------------- | --------- | ----------------------------------------- |
| GET    | `/notifications/sms-campaigns/status` | read_only | Campaign readiness and blockers           |
| GET    | `/notifications/sms-campaigns/runs`   | admin     | Paginated marketing campaign run audit    |
| POST   | `/notifications/sms-campaigns/run`    | admin     | Enqueue a marketing SMS campaign scaffold |

SMS deliverability dashboard (`ENABLE_SMS_DELIVERABILITY_DASHBOARD=true`, requires marketing SMS delivery). Aggregates campaign run and delivery log metrics for the org.

| Method | Path                                                  | Min role  | Description                              |
| ------ | ----------------------------------------------------- | --------- | ---------------------------------------- |
| GET    | `/notifications/sms-campaigns/deliverability/status`  | read_only | Deliverability dashboard readiness       |
| GET    | `/notifications/sms-campaigns/deliverability/summary` | read_only | Org delivery metrics and recent outcomes |

Endpoints return `404` when the corresponding feature flag is false. Multi-provider failover and real-time alerting remain deferred.

Returns `404` when either `ENABLE_SMS_DELIVERY` or `ENABLE_SMS_MARKETING_CAMPAIGNS` is false.

## LLM gateway

LLM readiness and case summary generation behind ADR-012 gates.

| Method | Path                           | Min role     | Description                         |
| ------ | ------------------------------ | ------------ | ----------------------------------- |
| GET    | `/llm/status`                  | read_only    | LLM feature + provider readiness    |
| GET    | `/llm/dispute-draft/status`    | read_only    | LLM dispute draft augment readiness |
| POST   | `/cases/{case_id}/llm-summary` | case_manager | Generate scrubbed case summary      |

Requires `ENABLE_LLM=true` and `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` for provider calls. See [ADR-012](../adr/012-llm-provider-policy.md).

LLM dispute draft augment scaffold (`ENABLE_LLM_DISPUTE_DRAFT_AUGMENT=true`, requires `ENABLE_LLM`). Improves rule-based dispute letter drafts for staff review; does not auto-send letters.

| Method | Path                                                | Min role     | Description                             |
| ------ | --------------------------------------------------- | ------------ | --------------------------------------- |
| POST   | `/accounts/{account_id}/dispute-draft/llm-augment`  | case_manager | Generate LLM augment audit for draft    |
| GET    | `/accounts/{account_id}/dispute-draft/llm-augments` | read_only    | Paginated augment audit log for account |

Returns `404` when augment flag is false. Emits `DISPUTE_DRAFT_LLM_AUGMENT` timeline events on success.

### Agent observability

Agent run audit scaffold with optional case timeline correlation. Requires `ENABLE_AI=true` and `ENABLE_AGENT_OBSERVABILITY=true`. No external LLM calls or autonomous agent execution.

| Method | Path                 | Min role     | Description                                |
| ------ | -------------------- | ------------ | ------------------------------------------ |
| GET    | `/llm/agents/status` | read_only    | Agent observability readiness and blockers |
| GET    | `/llm/agents/runs`   | read_only    | Paginated agent run audit log              |
| POST   | `/llm/agents/run`    | case_manager | Record agent observability scaffold run    |

Returns `404` when either `ENABLE_AI` or `ENABLE_AGENT_OBSERVABILITY` is false.

### Agent execution (human-gated)

Human-gated agent step execution audit with admin approval and optional case timeline correlation. Requires `ENABLE_AI=true`, `ENABLE_AGENT_OBSERVABILITY=true`, and `ENABLE_AGENT_EXECUTION=true`. No external LLM calls or autonomous dispute filing.

| Method | Path                                | Min role     | Description                            |
| ------ | ----------------------------------- | ------------ | -------------------------------------- |
| GET    | `/llm/execution/status`             | read_only    | Agent execution readiness and blockers |
| GET    | `/llm/execution/steps`              | read_only    | Paginated execution step audit log     |
| POST   | `/llm/execution/steps`              | case_manager | Submit a step for human approval       |
| POST   | `/llm/execution/steps/{id}/approve` | admin        | Approve and record execution scaffold  |

Returns `404` when agent execution flags are false.

### Agent external tool-calling (human-gated)

Human-gated external tool invocation audit with admin approval and optional case timeline correlation. Requires `ENABLE_AI=true`, `ENABLE_AGENT_OBSERVABILITY=true`, `ENABLE_AGENT_EXECUTION=true`, and `ENABLE_AGENT_EXTERNAL_TOOL_CALLING=true`. No live external tool calls or unsupervised invocation loops.

| Method | Path                                      | Min role     | Description                            |
| ------ | ----------------------------------------- | ------------ | -------------------------------------- |
| GET    | `/llm/tool-calling/status`                | read_only    | Tool-calling readiness and blockers    |
| GET    | `/llm/tool-calling/requests`              | read_only    | Paginated tool invocation audit log    |
| POST   | `/llm/tool-calling/requests`              | case_manager | Submit a tool invocation for approval  |
| POST   | `/llm/tool-calling/requests/{id}/approve` | admin        | Approve and record invocation scaffold |

Returns `404` when agent external tool-calling flags are false.

### Agent supervised loops (human-gated)

Multi-step agent loop audit with human gates between steps. Requires `ENABLE_AI=true`, `ENABLE_AGENT_OBSERVABILITY=true`, `ENABLE_AGENT_EXECUTION=true`, `ENABLE_AGENT_EXTERNAL_TOOL_CALLING=true`, and `ENABLE_AGENT_SUPERVISED_LOOPS=true`. A supervised loop run can only start from an `invoked` tool invocation request. No fully unsupervised loops.

| Method | Path                                                          | Min role     | Description                                      |
| ------ | ------------------------------------------------------------- | ------------ | ------------------------------------------------ |
| GET    | `/llm/supervised-loops/status`                                | read_only    | Supervised loop readiness and blockers           |
| GET    | `/llm/supervised-loops/runs`                                  | read_only    | Paginated supervised loop audit log              |
| POST   | `/llm/supervised-loops/tool-requests/{tool_request_id}/start` | case_manager | Start a supervised loop from an invoked tool run |
| POST   | `/llm/supervised-loops/runs/{run_id}/approve`                 | admin        | Approve and complete a supervised loop step      |

Returns `404` when agent supervised loop flags are false.

### Agent unsupervised loops (v5.9)

| Method | Path                                                                | Role         | Description                                                |
| ------ | ------------------------------------------------------------------- | ------------ | ---------------------------------------------------------- |
| GET    | `/llm/unsupervised-loops/status`                                    | read_only    | Unsupervised loop readiness and blockers                   |
| GET    | `/llm/unsupervised-loops/runs`                                      | read_only    | Paginated unsupervised loop audit log                      |
| POST   | `/llm/unsupervised-loops/supervised-runs/{supervised_run_id}/start` | case_manager | Start an unsupervised loop from a completed supervised run |
| POST   | `/llm/unsupervised-loops/runs/{run_id}/approve`                     | admin        | Approve and complete an unsupervised multi-step loop       |

Returns `404` when agent unsupervised loop flags are false.

### Agent arbitrary execution (v5.10)

| Method | Path                                                                     | Role         | Description                                                 |
| ------ | ------------------------------------------------------------------------ | ------------ | ----------------------------------------------------------- |
| GET    | `/llm/arbitrary-execution/status`                                        | read_only    | Arbitrary execution readiness and blockers                  |
| GET    | `/llm/arbitrary-execution/runs`                                          | read_only    | Paginated arbitrary execution audit log                     |
| POST   | `/llm/arbitrary-execution/unsupervised-runs/{unsupervised_run_id}/start` | case_manager | Start arbitrary execution from a completed unsupervised run |
| POST   | `/llm/arbitrary-execution/runs/{run_id}/approve`                         | admin        | Approve and record arbitrary execution scaffold             |

Returns `404` when agent arbitrary execution flags are false.

## Enterprise identity

MFA and SSO readiness plus staff enrollment flows. Portal authentication (`/portal/auth/*`) remains a separate partition.

| Method | Path                                  | Min role  | Description                            |
| ------ | ------------------------------------- | --------- | -------------------------------------- |
| GET    | `/enterprise/status`                  | read_only | Enterprise MFA/SSO readiness           |
| POST   | `/enterprise/mfa/totp/enroll`         | read_only | Start TOTP enrollment (secret + URI)   |
| POST   | `/enterprise/mfa/totp/confirm`        | read_only | Confirm TOTP with verification code    |
| GET    | `/enterprise/mfa/totp`                | read_only | Current user TOTP enrollment status    |
| DELETE | `/enterprise/mfa/totp`                | read_only | Disable enrolled TOTP for current user |
| POST   | `/enterprise/sso/enrollment/start`    | read_only | Start OIDC account linking             |
| POST   | `/enterprise/sso/enrollment/complete` | read_only | Complete OIDC linking with auth code   |
| GET    | `/enterprise/sso/enrollment`          | read_only | Current user OIDC link status          |

Requires `ENABLE_ENTERPRISE=true`. TOTP enrollment requires `ENTERPRISE_MFA_MODE=totp` and `ENTERPRISE_MFA_ISSUER`. OIDC enrollment requires `ENTERPRISE_SSO_PROVIDER=oidc` with issuer, client credentials, and `ENTERPRISE_SSO_REDIRECT_URI`. SAML remains deferred. SCIM provisioning is documented below.

### SCIM provisioning

SCIM 2.0 user/group provision scaffold with org-scoped audit logs. Requires `ENABLE_ENTERPRISE=true`, `ENABLE_SCIM_PROVISIONING=true`, and configured OIDC SSO (`ENTERPRISE_SSO_PROVIDER=oidc` with issuer and client credentials). Optional `SCIM_PROVISIONING_BEARER_TOKEN` for future IdP bearer auth (staff JWT used in this scaffold). Admin role required for write; read-only and above for list/status.

| Method | Path                         | Min role  | Description                               |
| ------ | ---------------------------- | --------- | ----------------------------------------- |
| GET    | `/enterprise/scim/status`    | read_only | SCIM readiness and blockers               |
| POST   | `/enterprise/scim/v2/Users`  | admin     | Provision or update a SCIM user audit log |
| GET    | `/enterprise/scim/v2/Users`  | read_only | List provisioned SCIM users for the org   |
| POST   | `/enterprise/scim/v2/Groups` | admin     | Provision or update a SCIM group log      |
| GET    | `/enterprise/scim/v2/Groups` | read_only | List provisioned SCIM groups for the org  |

Multi-IdP federation scaffold (`ENABLE_IDP_FEDERATION=true`, requires `ENABLE_ENTERPRISE=true` and OIDC SSO config). SAML metadata upload scaffold requires `ENABLE_SAML_FEDERATION_METADATA=true` (and IdP federation). HRIS bidirectional sync requires `ENABLE_HRIS_BIDIRECTIONAL_SYNC=true` (and SAML metadata scaffold).

| Method | Path                                           | Min role  | Description                               |
| ------ | ---------------------------------------------- | --------- | ----------------------------------------- |
| GET    | `/enterprise/federation/status`                | read_only | Federation readiness and provider count   |
| GET    | `/enterprise/federation/providers`             | read_only | List registered IdP providers for the org |
| POST   | `/enterprise/federation/providers`             | admin     | Register an IdP provider in org registry  |
| GET    | `/enterprise/federation/saml-metadata/status`  | read_only | SAML metadata upload readiness            |
| GET    | `/enterprise/federation/saml-metadata/uploads` | read_only | List SAML metadata uploads for the org    |
| POST   | `/enterprise/federation/saml-metadata/upload`  | admin     | Upload and validate SAML metadata XML     |
| GET    | `/enterprise/federation/hris-sync/status`      | read_only | HRIS sync readiness and blockers          |
| GET    | `/enterprise/federation/hris-sync/runs`        | read_only | List HRIS sync runs for the org           |
| POST   | `/enterprise/federation/hris-sync/run`         | admin     | Enqueue HRIS sync run audit scaffold      |

HRIS lifecycle sync scaffold requires `ENABLE_HRIS_LIFECYCLE_SYNC=true` (and `ENABLE_HRIS_BIDIRECTIONAL_SYNC=true`). No passwordless enrollment UI or multi-IdP bulk provisioning.

| Method | Path                                                          | Min role  | Description                                           |
| ------ | ------------------------------------------------------------- | --------- | ----------------------------------------------------- |
| GET    | `/enterprise/federation/hris-lifecycle/status`                | read_only | HRIS lifecycle sync readiness and blockers            |
| GET    | `/enterprise/federation/hris-lifecycle/runs`                  | read_only | Paginated HRIS lifecycle sync audit log               |
| POST   | `/enterprise/federation/hris-lifecycle/sync-runs/{id}/start`  | admin     | Start lifecycle sync from completed bidirectional run |
| POST   | `/enterprise/federation/hris-lifecycle/runs/{run_id}/approve` | admin     | Approve lifecycle sync scaffold                       |

| GET | `/enterprise/federation/saml-cert-rotation/status` | read_only | SAML cert rotation readiness and blockers |
| GET | `/enterprise/federation/saml-cert-rotation/runs` | read_only | List SAML certificate rotation audit log |
| POST | `/enterprise/federation/saml-cert-rotation/metadata-uploads/{id}/rotate` | admin | Submit cert rotation run for admin review |
| POST | `/enterprise/federation/saml-cert-rotation/runs/{run_id}/approve` | admin | Approve rotation scaffold (no live IdP) |

SAML automated rotation scaffold requires `ENABLE_SAML_AUTOMATED_ROTATION=true` (and `ENABLE_SAML_CERTIFICATE_ROTATION=true`).

| GET | `/enterprise/federation/saml-automated-rotation/status` | read_only | SAML automated rotation readiness and blockers |
| GET | `/enterprise/federation/saml-automated-rotation/runs` | read_only | Paginated SAML automated rotation audit log |
| POST | `/enterprise/federation/saml-automated-rotation/rotation-runs/{id}/start` | admin | Start automated rotation from rotated cert run |
| POST | `/enterprise/federation/saml-automated-rotation/runs/{run_id}/approve` | admin | Approve automated rotation scaffold |

SAML passwordless enrollment scaffold requires `ENABLE_SAML_PASSWORDLESS_ENROLLMENT=true` (and `ENABLE_SAML_AUTOMATED_ROTATION=true`). No passwordless rollout without operator review.

| GET | `/enterprise/federation/saml-passwordless-enrollment/status` | read_only | SAML passwordless enrollment readiness and blockers |
| GET | `/enterprise/federation/saml-passwordless-enrollment/runs` | read_only | Paginated SAML passwordless enrollment audit log |
| POST | `/enterprise/federation/saml-passwordless-enrollment/automated-rotation-runs/{id}/enroll` | admin | Start passwordless enrollment from automated rotation run |
| POST | `/enterprise/federation/saml-passwordless-enrollment/runs/{run_id}/approve` | admin | Approve passwordless enrollment scaffold |

Endpoints return `404` when the corresponding feature flag is false.

## Organization admin

Enterprise org administration scaffold for API key lifecycle and organization summary metrics. All endpoints require `ENABLE_ENTERPRISE=true` and **admin** role.

| Method | Path                                    | Min role | Description                                     |
| ------ | --------------------------------------- | -------- | ----------------------------------------------- |
| GET    | `/org-admin/status`                     | admin    | Org admin capabilities overview                 |
| GET    | `/org-admin/organization`               | admin    | Organization summary (users, API keys, billing) |
| GET    | `/org-admin/api-keys`                   | admin    | List organization API keys (prefix only)        |
| POST   | `/org-admin/api-keys`                   | admin    | Create API key (full secret returned once)      |
| GET    | `/org-admin/api-keys/{id}`              | admin    | Get API key metadata                            |
| POST   | `/org-admin/api-keys/{id}/revoke`       | admin    | Revoke an active API key                        |
| GET    | `/org-admin/api-keys/rate-limit/status` | admin    | API key rate-limit configuration (5.2)          |

When `ENABLE_API_DEVELOPER_PORTAL=true`, admins can access the internal developer portal and rotate active keys.

| Method | Path                              | Min role | Description                                            |
| ------ | --------------------------------- | -------- | ------------------------------------------------------ |
| GET    | `/org-admin/developer-portal`     | admin    | Keys, scopes, rate-limit status, rotation readiness    |
| POST   | `/org-admin/api-keys/{id}/rotate` | admin    | Revoke key and issue replacement with same name/scopes |

Rotation writes an `api_key_rotation_logs` audit record. Returns `404` when `ENABLE_API_DEVELOPER_PORTAL` is false. Public external developer portal and OAuth client credentials remain deferred to 5.4+.

API keys use prefix `vrd_live_` with SHA-256 hashed storage. Scopes: `read`, `write`. SCIM provisioning is available when `ENABLE_SCIM_PROVISIONING=true` (see Enterprise identity). Cross-org roles and key usage analytics are deferred to 5.4+.

## Billing

Stripe customer and subscription scaffold for organization billing. Admin setup/subscribe endpoints require `ENABLE_BILLING=true` and `ENABLE_ENTERPRISE=true`. The Stripe webhook endpoint verifies `Stripe-Signature` and does not require staff JWT auth.

| Method | Path                                                 | Min role  | Description                                       |
| ------ | ---------------------------------------------------- | --------- | ------------------------------------------------- |
| GET    | `/billing/status`                                    | read_only | Stripe billing readiness and blockers             |
| POST   | `/billing/setup`                                     | admin     | Create Stripe customer for current organization   |
| POST   | `/billing/subscribe`                                 | admin     | Create subscription for org billing customer      |
| POST   | `/billing/webhooks/stripe`                           | public    | Stripe webhook handler (signature verified)       |
| GET    | `/billing/usage/summary`                             | read_only | Org usage metric totals (metering scaffold)       |
| POST   | `/billing/usage/events`                              | admin     | Record a billing usage event for the org          |
| GET    | `/billing/invoicing/status`                          | read_only | Invoicing/dunning readiness and blockers          |
| GET    | `/billing/invoicing/runs`                            | read_only | Paginated invoicing/dunning run audit log         |
| POST   | `/billing/invoicing/run`                             | admin     | Run invoice cycle or dunning reminder scaffold    |
| GET    | `/billing/collection/status`                         | read_only | Invoice collection readiness and blockers         |
| GET    | `/billing/collection/runs`                           | read_only | Paginated invoice collection run audit log        |
| POST   | `/billing/collection/run`                            | admin     | Run invoice PDF or payment reminder scaffold      |
| GET    | `/billing/invoice-pdf/status`                        | read_only | Stripe invoice PDF readiness and blockers         |
| GET    | `/billing/invoice-pdf/runs`                          | read_only | Paginated Stripe invoice PDF generation audit log |
| POST   | `/billing/invoice-pdf/collection-runs/{id}/generate` | admin     | Submit PDF generation run for admin review        |
| POST   | `/billing/invoice-pdf/runs/{run_id}/approve`         | admin     | Approve PDF generation scaffold (no live Stripe)  |

Stripe tax calculation scaffold requires `ENABLE_STRIPE_TAX_CALCULATION=true` (and `ENABLE_STRIPE_INVOICE_PDF=true`). No live Stripe Tax API calls without compliance deferral docs.

| Method | Path                                               | Min role  | Description                                    |
| ------ | -------------------------------------------------- | --------- | ---------------------------------------------- |
| GET    | `/billing/tax-calculation/status`                  | read_only | Stripe tax calculation readiness and blockers  |
| GET    | `/billing/tax-calculation/runs`                    | read_only | Paginated Stripe tax calculation audit log     |
| POST   | `/billing/tax-calculation/pdf-runs/{id}/calculate` | admin     | Submit tax calculation run from generated PDF  |
| POST   | `/billing/tax-calculation/runs/{run_id}/approve`   | admin     | Approve tax calculation scaffold (no live API) |

Stripe live Tax API scaffold requires `ENABLE_STRIPE_LIVE_TAX_API=true` (and `ENABLE_STRIPE_TAX_CALCULATION=true`). No live Stripe Tax API calls without compliance deferral docs.

| Method | Path                                                     | Min role  | Description                                        |
| ------ | -------------------------------------------------------- | --------- | -------------------------------------------------- |
| GET    | `/billing/live-tax-api/status`                           | read_only | Live Stripe Tax API readiness and blockers         |
| GET    | `/billing/live-tax-api/runs`                             | read_only | Paginated live Stripe Tax API invocation audit     |
| POST   | `/billing/live-tax-api/tax-calculation-runs/{id}/invoke` | admin     | Submit live Tax API invocation from calculated run |
| POST   | `/billing/live-tax-api/runs/{run_id}/approve`            | admin     | Approve live Tax API invocation scaffold           |

Stripe charge retry scaffold requires `ENABLE_STRIPE_CHARGE_RETRY=true` (and `ENABLE_STRIPE_LIVE_TAX_API=true`). No live charge retries without compliance deferral docs.

| Method | Path                                                 | Min role  | Description                                      |
| ------ | ---------------------------------------------------- | --------- | ------------------------------------------------ |
| GET    | `/billing/charge-retry/status`                       | read_only | Stripe charge retry readiness and blockers       |
| GET    | `/billing/charge-retry/runs`                         | read_only | Paginated Stripe charge retry audit log          |
| POST   | `/billing/charge-retry/live-tax-api-runs/{id}/retry` | admin     | Submit charge retry from invoked live Tax run    |
| POST   | `/billing/charge-retry/runs/{run_id}/approve`        | admin     | Approve charge retry scaffold (no live API call) |

`GET /org-admin/organization` embeds a `billing` section when billing is configured. Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_DEFAULT_PRICE_ID`. Usage metering requires `ENABLE_BILLING_USAGE_METERING=true` (and `ENABLE_BILLING=true`). Invoicing scaffold requires `ENABLE_BILLING_INVOICING=true`. Invoice collection scaffold requires `ENABLE_BILLING_INVOICE_COLLECTION=true` (and `ENABLE_BILLING_INVOICING=true`). Stripe invoice PDF generation scaffold requires `ENABLE_STRIPE_INVOICE_PDF=true` (and `ENABLE_BILLING_INVOICE_COLLECTION=true`). Actual Stripe invoice PDF API calls remain deferred.

## Compliance center

Consent history and retention policy placeholders for CROA/FCRA-oriented operations. Records are org-scoped and append-only (withdrawal updates status; records are not deleted).

| Method | Path                                         | Min role     | Description                             |
| ------ | -------------------------------------------- | ------------ | --------------------------------------- |
| GET    | `/compliance/status`                         | read_only    | Compliance center capabilities overview |
| GET    | `/compliance/consents`                       | read_only    | List consent records (filter by client) |
| POST   | `/compliance/consents`                       | case_manager | Record client consent                   |
| GET    | `/compliance/consents/{consent_id}`          | read_only    | Get consent record                      |
| POST   | `/compliance/consents/{consent_id}/withdraw` | case_manager | Withdraw previously granted consent     |
| GET    | `/compliance/retention-policies`             | read_only    | List retention policy placeholders      |
| POST   | `/compliance/retention-policies`             | admin        | Create retention policy placeholder     |
| GET    | `/compliance/retention-policies/{policy_id}` | read_only    | Get retention policy                    |
| PATCH  | `/compliance/retention-policies/{policy_id}` | admin        | Update retention policy placeholder     |

Retention enforcement endpoints require `ENABLE_COMPLIANCE_ENFORCEMENT=true`. Active retention policies soft-delete expired records in supported scopes (`documents`, `communications`, `client_profiles`); `audit_logs` scope runs are recorded as `skipped` until append-only purge is implemented. Manual runs are admin-only; scheduled runs use worker job `retention_enforcement_scan` (`0 3 * * *` UTC).

| Method | Path                             | Role      | Description                                      |
| ------ | -------------------------------- | --------- | ------------------------------------------------ |
| GET    | `/compliance/enforcement/status` | read_only | Enforcement feature status and last run metadata |
| GET    | `/compliance/enforcement/runs`   | read_only | Paginated retention enforcement audit log        |
| POST   | `/compliance/enforcement/run`    | admin     | Run retention enforcement for current org        |

Dispute filing prep endpoints require `ENABLE_DISPUTE_FILING_PREP=true` (and human-gated agent execution readiness). Admin approval marks a prep run as `prepared` without autonomous bureau submission.

| Method | Path                                                    | Role         | Description                             |
| ------ | ------------------------------------------------------- | ------------ | --------------------------------------- |
| GET    | `/compliance/dispute-filing/status`                     | read_only    | Filing prep readiness and blockers      |
| GET    | `/compliance/dispute-filing/runs`                       | read_only    | Paginated filing prep audit log         |
| POST   | `/compliance/dispute-filing/accounts/{account_id}/prep` | case_manager | Submit filing prep run for admin review |
| POST   | `/compliance/dispute-filing/runs/{run_id}/approve`      | admin        | Approve prep run (no bureau submission) |

Dispute bureau submission endpoints require `ENABLE_DISPUTE_BUREAU_SUBMISSION=true` (and a `prepared` filing prep run). Admin approval records a submission scaffold without live bureau API integration.

| Method | Path                                                          | Role         | Description                                   |
| ------ | ------------------------------------------------------------- | ------------ | --------------------------------------------- |
| GET    | `/compliance/dispute-bureau-submission/status`                | read_only    | Bureau submission readiness and blockers      |
| GET    | `/compliance/dispute-bureau-submission/runs`                  | read_only    | Paginated bureau submission audit log         |
| POST   | `/compliance/dispute-bureau-submission/prep-runs/{id}/submit` | case_manager | Submit bureau submission run for admin review |
| POST   | `/compliance/dispute-bureau-submission/runs/{run_id}/approve` | admin        | Approve submission scaffold (no live bureau)  |

Returns `404` when dispute bureau submission flags are false.

### Bureau live API integration (operator-gated)

Operator-gated external bureau API invocation audit. Requires `ENABLE_AI=true`, `ENABLE_AGENT_OBSERVABILITY=true`, `ENABLE_AGENT_EXECUTION=true`, `ENABLE_DISPUTE_FILING_PREP=true`, `ENABLE_DISPUTE_BUREAU_SUBMISSION=true`, and `ENABLE_BUREAU_LIVE_API=true`. A live API invocation run can only start from a `submitted` bureau submission run. No unsupervised filing loops or live bureau calls without operator review.

| Method | Path                                                                 | Min role     | Description                                         |
| ------ | -------------------------------------------------------------------- | ------------ | --------------------------------------------------- |
| GET    | `/compliance/bureau-live-api/status`                                 | read_only    | Bureau live API readiness and blockers              |
| GET    | `/compliance/bureau-live-api/runs`                                   | read_only    | Paginated bureau live API invocation audit log      |
| POST   | `/compliance/bureau-live-api/submission-runs/{submission_id}/invoke` | case_manager | Start live API invocation from submitted submission |
| POST   | `/compliance/bureau-live-api/runs/{run_id}/approve`                  | admin        | Approve and record invocation scaffold              |

Returns `404` when bureau live API flags are false.

### Autonomous bureau filing (v5.9)

| Method | Path                                                                    | Role         | Description                                      |
| ------ | ----------------------------------------------------------------------- | ------------ | ------------------------------------------------ |
| GET    | `/compliance/autonomous-bureau-filing/status`                           | read_only    | Autonomous filing readiness and blockers         |
| GET    | `/compliance/autonomous-bureau-filing/runs`                             | read_only    | Paginated autonomous bureau filing audit log     |
| POST   | `/compliance/autonomous-bureau-filing/live-api-runs/{live_api_id}/file` | case_manager | Start filing from an invoked bureau live API run |
| POST   | `/compliance/autonomous-bureau-filing/runs/{run_id}/approve`            | admin        | Approve and record autonomous filing scaffold    |

Returns `404` when autonomous bureau filing flags are false.

### Bureau re-filing audit (v5.10)

| Method | Path                                                             | Role         | Description                                               |
| ------ | ---------------------------------------------------------------- | ------------ | --------------------------------------------------------- |
| GET    | `/compliance/bureau-refiling/status`                             | read_only    | Bureau re-filing readiness and blockers                   |
| GET    | `/compliance/bureau-refiling/runs`                               | read_only    | Paginated bureau re-filing audit log                      |
| POST   | `/compliance/bureau-refiling/filing-runs/{filing_run_id}/refile` | case_manager | Start re-filing from a filed autonomous bureau filing run |
| POST   | `/compliance/bureau-refiling/runs/{run_id}/approve`              | admin        | Approve and record bureau re-filing scaffold              |

Returns `404` when bureau re-filing flags are false.

Consent types: `croa_services`, `fcra_dispute`, `fdcpa_contact`, `marketing`, `data_processing`. Retention scopes: `documents`, `communications`, `audit_logs`, `client_profiles`. Enforcement jobs and legal sign-off workflows are deferred to 5.0+.

## Reporting

Read-optimized operations reporting for 4.8 dashboard expansions.

| Method | Path                    | Min role  | Description                                      |
| ------ | ----------------------- | --------- | ------------------------------------------------ |
| GET    | `/reporting/operations` | read_only | Org-scoped clients, disputes, notifications KPIs |

`GET /reporting/operations` also accepts organization API keys when `ENABLE_ENTERPRISE=true`: pass `X-API-Key: vrd_live_…` or `Authorization: Bearer vrd_live_…` with a key that includes the `read` scope. Staff JWT auth with `read_only` role remains supported. Other reporting routes are JWT-only.

When `ENABLE_API_KEY_RATE_LIMIT=true`, API key requests to `GET /reporting/operations` are limited per organization and key (`API_KEY_RATE_LIMIT_PER_MINUTE`, default `60`) using a Redis fixed-window counter. Exceeded limits return `429 Too Many Requests` with a `Retry-After` header.

The Mission Control `GET /dashboard` response also embeds an `operations` section sourced from the same read model.

### Enterprise reporting (5.0)

Bureau performance and team productivity read models for enterprise dashboards. All endpoints are org-scoped aggregates — no cross-org queries.

| Method | Path                            | Min role  | Description                                             |
| ------ | ------------------------------- | --------- | ------------------------------------------------------- |
| GET    | `/reporting/status`             | read_only | Enterprise reporting capabilities overview              |
| GET    | `/reporting/bureau-performance` | read_only | Tradeline counts and dispute outcomes grouped by bureau |
| GET    | `/reporting/team-productivity`  | read_only | Per-staff task and case productivity (30-day window)    |
| GET    | `/reporting/revenue`            | read_only | Org revenue readiness from Stripe billing state         |

When `ENABLE_BILLING=true`, `GET /reporting/revenue` returns subscription status, client/portal counts, and a heuristic readiness score (0–100) derived from billing configuration and operations metrics. Returns `404` when billing is disabled.

When `ENABLE_MATERIALIZED_REPORTING=true`, bureau and team endpoints read from PostgreSQL materialized views refreshed by a scheduled worker job (`0 4 * * *` UTC) or manual admin refresh.

| Method | Path                                    | Min role  | Description                              |
| ------ | --------------------------------------- | --------- | ---------------------------------------- |
| GET    | `/reporting/materialized-views/status`  | read_only | Materialized view readiness and last run |
| GET    | `/reporting/materialized-views/runs`    | read_only | Paginated refresh audit log              |
| POST   | `/reporting/materialized-views/refresh` | admin     | Refresh all reporting materialized views |

When `ENABLE_PREDICTIVE_ANALYTICS=true`, staff can read org-scoped historical outcome aggregates and refresh cached snapshots.

| Method | Path                             | Min role  | Description                                 |
| ------ | -------------------------------- | --------- | ------------------------------------------- |
| GET    | `/reporting/predictive/status`   | read_only | Predictive analytics readiness and blockers |
| GET    | `/reporting/predictive/outcomes` | read_only | Historical case/dispute outcome aggregates  |
| POST   | `/reporting/predictive/refresh`  | admin     | Recompute and persist org outcome snapshot  |

Outcome metrics include case closure rates (90-day window), dispute resolution rates, letter send counts, and a heuristic `outcome_score` (0–100). Returns `404` when predictive analytics is disabled. Cross-org benchmarks and model serving remain deferred to 5.4+.

Score-improvement trends remain deferred to 5.4+.

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
