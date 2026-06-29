# Epic: Document Intelligence Platform

**Target version:** 4.3 (Operational Core)  
**Branch strategy:** One feature branch per milestone  
**Status:** Milestone 3 in progress — Document Classification on `feature/document-classification`

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

## Milestone 4 — Metadata & Entity Extraction

Extract: consumer name, bureau, creditor, masked account number, report date, collection agency, balance, addresses, phone numbers.

Link to Cases and Accounts when confidence is high; flag uncertain matches for review.

---

## Milestone 5 — Timeline Integration

Auto-create timeline events:

- Uploaded
- OCR complete
- Classified
- Metadata extracted
- Linked to case / account
- Deleted (soft delete)

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
