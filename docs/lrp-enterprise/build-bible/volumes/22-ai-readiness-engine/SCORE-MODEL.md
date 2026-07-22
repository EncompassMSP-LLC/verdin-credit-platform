# Lending Readiness Score™ — model worksheet

| Field        | Value      |
| ------------ | ---------- |
| Status       | `draft`    |
| Parent       | Vol 22     |
| Last updated | 2026-07-22 |

## Formula (conceptual)

```text
score = clamp(0..100,
  Σ (dimension_score_i * weight_i)
  - penalties(partial_bureau, unresolved_id_mismatch)
)
```

Dimension scores are 0–100 from rule tables (to be filled with ops calibration).

## Example driver → task map

| Driver                        | Severity | Example task                       |
| ----------------------------- | -------- | ---------------------------------- |
| High revolving utilization    | High     | Pay down plan module + checklist   |
| Open collection               | High     | Docs gather + staff dispute review |
| Recent inquiry spike          | Med      | Education: inquiry timing          |
| Cross-bureau balance mismatch | Med      | Staff verify / re-pull guidance    |
| Missing ID doc                | High     | Upload task                        |
| ID-theft signal               | Critical | Staff compliance path (not auto)   |

## Calibration log

| Date | Change                | Approver |
| ---- | --------------------- | -------- |
|      | Initial draft weights |          |
