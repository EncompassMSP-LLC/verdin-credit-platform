# Canonical readiness stage model

| Field        | Value                                     |
| ------------ | ----------------------------------------- |
| Status       | `ready-for-build` (accepted 2026-07-22)   |
| Last updated | 2026-07-22                                |
| Used by      | Vol 14 · Vol 19–22 · CRM/lender pipelines |

---

## Stages (ordered)

| Key             | Label         | Meaning                               | Typical exit                     |
| --------------- | ------------- | ------------------------------------- | -------------------------------- |
| `intake`        | Intake        | Invited / profile / consents          | Docs requested                   |
| `documenting`   | Documenting   | Collecting ID/reports/checklist       | Reports ready to analyze         |
| `analyzing`     | Analyzing     | Parse + findings in progress          | Findings ready for review        |
| `planning`      | Planning      | Score published; action plan active   | Material tasks underway          |
| `remediating`   | Remediating   | Disputes/education/tasks in flight    | Blockers cleared or stable       |
| `near_ready`    | Near ready    | Minor gaps; partner can plan timeline | Package checklist green          |
| `lending_ready` | Lending Ready | Ops marks package-eligible            | Export authorized (not approval) |
| `paused`        | Paused        | Borrower/partner hold                 | Resume → prior stage             |
| `closed`        | Closed        | Completed / withdrawn / disqualified  | —                                |

**Forbidden labels:** Approved, Pre-approved, Funded, Guaranteed.

## Score bands vs stages

Bands (Vol 22) are **advisory quality signals**. Stages are **ops workflow**.  
A borrower can be `remediating` with band `Progressing`, etc. Do not auto-set `lending_ready` from score alone — **staff action** required.

## Allowed transitions (draft)

```text
intake → documenting → analyzing → planning → remediating ⇄ near_ready → lending_ready
any active → paused → (resume prior)
any → closed
```

Skip-forward allowed with reason (audit). Skip to `lending_ready` requires ops lead (or dual control later).

## Partner-visible mapping (coarse)

| Internal stage       | LO sees                  | Realtor sees             |
| -------------------- | ------------------------ | ------------------------ |
| intake / documenting | Getting started          | Getting started          |
| analyzing / planning | In review                | In review                |
| remediating          | Working plan             | Working plan             |
| near_ready           | Near ready               | Near ready               |
| lending_ready        | Lending Ready (advisory) | Lending Ready (advisory) |
| paused / closed      | Paused / Closed          | Paused / Closed          |
