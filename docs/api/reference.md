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

Portal push notifications require `ENABLE_PORTAL_PUSH=true` and `ENABLE_CLIENT_PORTAL=true`. Staff replies on linked cases enqueue push delivery attempts for active portal subscriptions; delivery is audited in `portal_push_delivery_logs`. Web Push provider configuration uses `PORTAL_PUSH_PROVIDER=web_push` with VAPID keys.

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

**List query parameters:** `unread_only`, `category`, `sort_by`, `sort_order`, `page`, `page_size`.

`/notifications/email/status` reports `enabled`, `ready`, configured provider metadata, and blockers based on `ENABLE_EMAIL_DELIVERY` plus email provider env vars.

`POST /notifications/email/send` delivers via the configured provider (`smtp` or `sendgrid`) when ready. Each attempt is persisted to `email_delivery_logs`. Set `deliver_email: true` on `POST /notifications` to send email alongside the in-app notification.

Provider env vars: `EMAIL_PROVIDER`, `EMAIL_FROM_ADDRESS`, `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_SMTP_USERNAME`, `EMAIL_SMTP_PASSWORD`, `EMAIL_SENDGRID_API_KEY`.

## LLM gateway

LLM readiness and case summary generation behind ADR-012 gates.

| Method | Path                           | Min role     | Description                      |
| ------ | ------------------------------ | ------------ | -------------------------------- |
| GET    | `/llm/status`                  | read_only    | LLM feature + provider readiness |
| POST   | `/cases/{case_id}/llm-summary` | case_manager | Generate scrubbed case summary   |

Requires `ENABLE_LLM=true` and `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` for provider calls. See [ADR-012](../adr/012-llm-provider-policy.md).

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

Requires `ENABLE_ENTERPRISE=true`. TOTP enrollment requires `ENTERPRISE_MFA_MODE=totp` and `ENTERPRISE_MFA_ISSUER`. OIDC enrollment requires `ENTERPRISE_SSO_PROVIDER=oidc` with issuer, client credentials, and `ENTERPRISE_SSO_REDIRECT_URI`. SAML and SCIM remain deferred.

## Organization admin

Enterprise org administration scaffold for API key lifecycle and organization summary metrics. All endpoints require `ENABLE_ENTERPRISE=true` and **admin** role.

| Method | Path                              | Min role | Description                                     |
| ------ | --------------------------------- | -------- | ----------------------------------------------- |
| GET    | `/org-admin/status`               | admin    | Org admin capabilities overview                 |
| GET    | `/org-admin/organization`         | admin    | Organization summary (users, API keys, billing) |
| GET    | `/org-admin/api-keys`             | admin    | List organization API keys (prefix only)        |
| POST   | `/org-admin/api-keys`             | admin    | Create API key (full secret returned once)      |
| GET    | `/org-admin/api-keys/{id}`        | admin    | Get API key metadata                            |
| POST   | `/org-admin/api-keys/{id}/revoke` | admin    | Revoke an active API key                        |

API keys use prefix `vrd_live_` with SHA-256 hashed storage. Scopes: `read`, `write`. SCIM, cross-org roles, and usage analytics are deferred to 5.2+.

## Billing

Stripe customer and subscription scaffold for organization billing. Admin setup/subscribe endpoints require `ENABLE_BILLING=true` and `ENABLE_ENTERPRISE=true`. The Stripe webhook endpoint verifies `Stripe-Signature` and does not require staff JWT auth.

| Method | Path                       | Min role  | Description                                     |
| ------ | -------------------------- | --------- | ----------------------------------------------- |
| GET    | `/billing/status`          | read_only | Stripe billing readiness and blockers           |
| POST   | `/billing/setup`           | admin     | Create Stripe customer for current organization |
| POST   | `/billing/subscribe`       | admin     | Create subscription for org billing customer    |
| POST   | `/billing/webhooks/stripe` | public    | Stripe webhook handler (signature verified)     |

`GET /org-admin/organization` embeds a `billing` section when billing is configured. Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_DEFAULT_PRICE_ID`. Usage metering and invoicing PDFs are deferred.

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

Consent types: `croa_services`, `fcra_dispute`, `fdcpa_contact`, `marketing`, `data_processing`. Retention scopes: `documents`, `communications`, `audit_logs`, `client_profiles`. Enforcement jobs and legal sign-off workflows are deferred to 5.0+.

## Reporting

Read-optimized operations reporting for 4.8 dashboard expansions.

| Method | Path                    | Min role  | Description                                      |
| ------ | ----------------------- | --------- | ------------------------------------------------ |
| GET    | `/reporting/operations` | read_only | Org-scoped clients, disputes, notifications KPIs |

`GET /reporting/operations` also accepts organization API keys when `ENABLE_ENTERPRISE=true`: pass `X-API-Key: vrd_live_…` or `Authorization: Bearer vrd_live_…` with a key that includes the `read` scope. Staff JWT auth with `read_only` role remains supported. Other reporting routes are JWT-only.

The Mission Control `GET /dashboard` response also embeds an `operations` section sourced from the same read model.

### Enterprise reporting (5.0)

Bureau performance and team productivity read models for enterprise dashboards. All endpoints are org-scoped aggregates — no cross-org queries.

| Method | Path                            | Min role  | Description                                             |
| ------ | ------------------------------- | --------- | ------------------------------------------------------- |
| GET    | `/reporting/status`             | read_only | Enterprise reporting capabilities overview              |
| GET    | `/reporting/bureau-performance` | read_only | Tradeline counts and dispute outcomes grouped by bureau |
| GET    | `/reporting/team-productivity`  | read_only | Per-staff task and case productivity (30-day window)    |

When `ENABLE_MATERIALIZED_REPORTING=true`, bureau and team endpoints read from PostgreSQL materialized views refreshed by a scheduled worker job (`0 4 * * *` UTC) or manual admin refresh.

| Method | Path                                    | Min role  | Description                              |
| ------ | --------------------------------------- | --------- | ---------------------------------------- |
| GET    | `/reporting/materialized-views/status`  | read_only | Materialized view readiness and last run |
| GET    | `/reporting/materialized-views/runs`    | read_only | Paginated refresh audit log              |
| POST   | `/reporting/materialized-views/refresh` | admin     | Refresh all reporting materialized views |

Revenue metrics and score-improvement trends remain deferred to 5.2+.

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
