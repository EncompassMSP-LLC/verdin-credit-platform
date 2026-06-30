# Epic: Document Intelligence Platform

**Target version:** 4.3 (Operational Core)  
**Branch strategy:** One feature branch per milestone  
**Status:** Milestone 4 complete — Metadata & Entity Resolution on `feature/document-entity-resolution`

## Epic goal

Create an enterprise document platform that:

- Securely stores documents
- Extracts text (M2+)
- Understands document content (M3–M4)
- Links documents to Cases and Accounts
- Creates Timeline events (M5)
- Powers future AI features (M2–M5)

This epic is the foundation for OCR, AI, Timeline, Import Wizard, and Dispute Generation.

## Milestones

| #   | Milestone                       | Branch                            | Capability matrix row |
| --- | ------------------------------- | --------------------------------- | --------------------- |
| 1   | Document Foundation             | `feature/document-foundation`     | Document Foundation   |
| 2   | OCR Pipeline                    | `feature/document-ocr`            | OCR Pipeline          |
| 3   | AI Classification               | `feature/document-classification` | AI Classification     |
| 4   | Metadata & Entity Extraction    | `feature/document-metadata`       | Metadata Extraction   |
| 5   | Timeline Integration            | `feature/document-timeline`       | Timeline Integration  |
| 6   | Document Intelligence Dashboard | `feature/document-dashboard`      | Document Dashboard    |

Update [`capability-matrix.md`](../governance/capability-matrix.md) as each milestone merges.

---

## Milestone 1 — Document Foundation

**Goal:** Core document infrastructure with secure storage, versioning, and duplicate detection.

### Backend

- Document model + DocumentVersion model
- Organization scoping, optional account link
- SHA-256 file hashing + duplicate detection
- MinIO object storage (`DocumentStorage` abstraction)
- CRUD API + upload/download + version upload
- Repository, service, permissions, tests

### Frontend

- Document library (list, search, filters)
- Upload page
- Detail page with version history
- Preview placeholder

### Definition of done

- [x] Documents upload successfully
- [x] Metadata persists in PostgreSQL
- [x] Files stored in MinIO (or test storage adapter)
- [x] Duplicate detection works (same SHA-256 in org)
- [x] Integration tests pass
- [x] API client + UI integrated
- [x] Capability matrix row updated

---

## Milestone 2 — OCR Pipeline

**Goal:** Async text extraction for PDF and image documents without blocking upload requests.

**Pipeline:**

```
Upload → (Virus scan, future) → OCR Queue → Worker → Extract Text → Store OCR Result
```

**Formats:** PDF, JPG, PNG, TIFF (DOCX/TXT marked `skipped`)

Workers update `processing_status` asynchronously — never block upload requests.

### Backend

- `processing_status`, `ocr_text`, `ocr_error`, `ocr_processed_at` on `documents`
- API enqueues `ocr` job to Redis after upload / version upload
- Worker `OcrJob` reads MinIO, extracts text (pypdf / pytesseract), persists result
- `GET /documents/{id}/ocr`, `POST /documents/{id}/ocr/retry`
- List filter by `processing_status`

### Frontend

- Processing status badges on list and detail
- Extracted text panel with auto-refresh while queued/processing
- Retry OCR action on failure

### Definition of done

- [x] Eligible uploads enqueue OCR without blocking HTTP response
- [x] Worker extracts PDF text and persists to PostgreSQL
- [x] Processing status visible in API and UI
- [x] Retry OCR endpoint works
- [x] Integration + worker unit tests pass
- [x] Capability matrix row updated

---

## Milestone 3 — AI Classification

**Goal:** Rule-based document type classification with confidence scoring. Designed as an extensible classifier framework so AI-based classifiers can plug in alongside deterministic rules in 4.5+.

**Branch:** `feature/document-classification`

### Architecture

```
apps/api/api/modules/documents/classification/
    base.py          # DocumentClassifier protocol, ClassificationResult
    registry.py      # Evaluates all classifiers; selects highest confidence
    classifiers/
        credit_report.py
        bureau_response.py
        collection_letter.py
        identity_document.py
        proof_of_address.py
        bankruptcy.py
        court_record.py
        medical_collection.py
        utility_bill.py
        unknown.py
```

Each classifier implements:

```python
class DocumentClassifier(Protocol):
    def classify(self, context: ClassificationContext) -> ClassificationResult | None: ...
```

### Document types

Credit Report, Collection Letter, Bureau Response, Identity Document, Proof of Address, Bankruptcy Filing, Court Record, Medical Collection, Utility Bill, Unknown

### Backend

- `document_type`, `confidence_score`, `classification_method`, `classified_at`, `classified_by_id` on `documents`
- `GET /documents/{id}/classification`, `POST /documents/{id}/classify`
- Worker `DocumentClassifyJob` runs after OCR completes
- Deterministic keyword/heuristic rules only (no LLM in M3)

### Definition of done

- [ ] Classifier framework with registry and per-type classifiers
- [ ] Classification persists to PostgreSQL after OCR or manual classify
- [ ] API endpoints with integration tests
- [ ] Worker auto-classifies after OCR success
- [ ] Capability matrix row updated (🚧 → ✅ when complete)

---

## Milestone 4 — Metadata & Entity Resolution Engine

**Goal:** Extract structured metadata from OCR text and classification results, then resolve/link entities to existing Cases and Credit Accounts using deterministic rules. Flag ambiguous matches for manual review.

**Branch:** `feature/document-entity-resolution`

### Shared packages

```
packages/document-metadata/verdin_document_metadata/
    extractor.py     # Rule-based field extraction (no LLM)
packages/entity-resolution/verdin_entity_resolution/
    registry.py      # Resolver pipeline
    resolvers/       # case, account, person, organization
```

### Extracted fields

Consumer name, bureau, creditor, collection agency, masked account number, report date, balance, payment status, addresses, phone numbers, SSN (masked).

### Resolution fields

`confidence_score`, `resolution_status`, `resolution_method`, `matched_entity_id`, `matched_entity_type`, `candidate_entity_ids`, `reasoning`.

### Backend

- Tables: `document_metadata`, `document_entity_resolutions`
- Migration: `007_document_metadata_resolution.py`
- Worker jobs: `DocumentMetadataExtractJob` (after classification), `DocumentEntityResolveJob` (after extraction)
- API: metadata CRUD + resolution confirm/reject
- On matched account resolution, `documents.account_id` is set automatically

### Definition of done

- [x] `packages/entity-resolution` reusable shared package
- [x] `packages/document-metadata` rule-based extraction service
- [x] Deterministic resolution with ambiguous/unmatched handling
- [x] API endpoints with integration tests
- [x] Document Detail UI metadata + entity match panels
- [x] Document Library metadata/resolution filters
- [x] Capability matrix and API docs updated

---

## Milestone 5 — Timeline & Audit Engine

**Goal:** Single immutable event stream for compliance, debugging, and operational visibility. Domain services publish typed events through a shared event bus; the Timeline module subscribes and persists append-only records.

**Branch:** `feature/document-timeline`

### Shared packages

- `packages/event-bus` — in-process publish/subscribe (`PlatformEvent`, `EventBus`)
- `packages/event-types` — typed constants for case, account, document, auth, and task events

### Backend

- Extended `timeline_events` schema (organization, entity links, JSON metadata, performer, source module)
- `GET /timeline` with filters; events are append-only (no edit/delete)
- Publishers wired in case, account, document, and auth services
- Worker emits OCR, classification, metadata, and entity resolution events

### Definition of done

- [x] Event bus + event-types packages
- [x] Timeline API with filters
- [x] Automatic publishing from core domain services
- [x] Worker pipeline timeline events
- [x] Timeline UI page
- [ ] Task module publishers (when task CRUD ships)

---

## Milestone 6 — Document Intelligence Dashboard

Operational views:

- OCR queue, processing failures, duplicates
- Missing metadata, AI confidence
- Recent uploads, documents awaiting review

---

## Dependencies

```
M1 Document Foundation
    ├── M2 OCR Pipeline
    │       ├── M3 AI Classification
    │       └── M4 Metadata Extraction
    ├── M5 Timeline Integration (can start after M1; full value after M2–M4)
    └── M6 Dashboard (after M2+ for meaningful metrics)
```

## Governance

Follow the [feature lifecycle](../governance/README.md#feature-lifecycle):

Roadmap → Architecture review → ADR (if needed) → Branch → Implement → Tests → Docs → PR → CI → Release notes → Capability matrix

Architecture references:

- [Domain Model — Document Intelligence](../architecture/domain-model.md#document-intelligence-planned-43)
- [AI Architecture — Phase 1](../architecture/ai-architecture.md#phase-1--document-intelligence-target-45)
- [Security Architecture — file uploads](../architecture/security-architecture.md#input-validation)
