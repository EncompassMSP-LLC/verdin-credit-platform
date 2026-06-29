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

| Method | Path                             | Min role     | Description               |
| ------ | -------------------------------- | ------------ | ------------------------- |
| POST   | `/accounts`                      | case_manager | Create a credit account   |
| GET    | `/accounts`                      | read_only    | List accounts             |
| GET    | `/accounts/intelligence/summary` | read_only    | Organization intelligence |
| GET    | `/accounts/{account_id}`         | read_only    | Get account by ID         |
| PATCH  | `/accounts/{account_id}`         | case_manager | Update an account         |
| DELETE | `/accounts/{account_id}`         | admin        | Soft-delete an account    |

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

## Documents

Secure document storage with MinIO, SHA-256 hashing, versioning, and duplicate detection. See [`docs/epics/document-intelligence-platform.md`](../epics/document-intelligence-platform.md).

| Method | Path                                                 | Min role     | Description                        |
| ------ | ---------------------------------------------------- | ------------ | ---------------------------------- |
| POST   | `/documents`                                         | case_manager | Upload document (multipart)        |
| GET    | `/documents`                                         | read_only    | List documents                     |
| GET    | `/documents/{document_id}`                           | read_only    | Get document with versions         |
| PATCH  | `/documents/{document_id}`                           | case_manager | Update metadata                    |
| DELETE | `/documents/{document_id}`                           | admin        | Soft-delete document               |
| GET    | `/documents/{document_id}/classification`            | read_only    | Classification result              |
| POST   | `/documents/{document_id}/classification`            | case_manager | Run rule-based classification      |
| POST   | `/documents/{document_id}/classification/reclassify` | case_manager | Re-run classification              |
| GET    | `/documents/{document_id}/ocr`                       | read_only    | OCR status and extracted text      |
| POST   | `/documents/{document_id}/ocr/retry`                 | case_manager | Re-queue OCR for failed document   |
| GET    | `/documents/{document_id}/download`                  | read_only    | Download file (optional `version`) |
| POST   | `/documents/{document_id}/versions`                  | case_manager | Upload new version                 |
| GET    | `/documents/{document_id}/versions`                  | read_only    | List version history               |

### Upload (multipart form)

Fields: `file` (required), `title` (required), `case_id` (required), `description`, `account_id`

### List query parameters

`page`, `page_size`, `search`, `case_id`, `account_id`, `is_duplicate`, `processing_status`, `document_type`, `classification_status`, `sort_by`, `sort_order`

`classification_status` values: `classified`, `unclassified`, `unknown`

### Classification

`POST /documents/{document_id}/classification` runs the rule-based classifier registry against OCR text, file name, and title. Results persist `document_type`, `confidence_score`, `classification_method`, `classified_at`, and `classified_by_id`.

**Response (200):**

```json
{
  "document_id": "uuid",
  "document_type": "credit_report",
  "confidence_score": 0.85,
  "classification_method": "rules",
  "classified_at": "2026-06-29T12:00:00Z",
  "classified_by_id": "uuid"
}
```

**Errors:** `401` unauthenticated, `403` insufficient role, `404` document not found.

Duplicate detection: uploading a file with the same SHA-256 hash as an existing org document sets `is_duplicate: true` and `duplicate_of_id`.

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
