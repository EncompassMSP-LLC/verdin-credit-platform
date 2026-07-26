# Document Pipeline Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Hooks into existing document worker jobs — classify, OCR, parse, entity resolve — without unsupervised filing.

---

## 1. Event → automation

| Event                           | Automation                                             |
| ------------------------------- | ------------------------------------------------------ |
| Document uploaded               | Enqueue classify / OCR per existing pipeline           |
| Classification complete         | Notify case owner if needs review                      |
| OCR / parse failed              | Retry policy; then operator task                       |
| Credit report parsed            | Notify specialist; optional AI summary if LLM-ready    |
| Client completes checklist item | Update readiness tasks; optional partner progress ping |

---

## 2. Existing worker jobs (reuse)

| Job                   | Path / module                     |
| --------------------- | --------------------------------- |
| OCR                   | `apps/worker` `jobs/ocr`          |
| Classify              | `jobs/classify`                   |
| Credit report parse   | `jobs/credit_report_parse`        |
| Entity resolve        | `jobs/entity_resolve`             |
| AI summary            | `jobs/ai_summary` (ADR-012 gated) |
| Batch LLM summary     | `jobs/batch_document_llm_summary` |
| Retention enforcement | `jobs/retention_enforcement_scan` |

Ops automation **configures triggers and notifications**; it does not fork a parallel pipeline.

---

## 3. Staff gates

| Action                     | Gate                               |
| -------------------------- | ---------------------------------- |
| Dispute letter send        | Approved status only               |
| Bureau submission          | Explicitly deferred — never auto   |
| External LLM with PII      | Org config + `require_llm_ready()` |
| Partner share of documents | Authorization + least privilege    |

---

## 4. Operator recovery

Align with Version 23–26 document recovery surfaces:

- Re-parse / re-classify / OCR retry enqueue from case UI
- Bulk enqueue remains staff-initiated
- Automations may **suggest** retries; humans confirm bulk actions

---

## 5. Notifications

See [`notification-matrix.md`](notification-matrix.md) borrower/case rows for upload and needs-attention events.
