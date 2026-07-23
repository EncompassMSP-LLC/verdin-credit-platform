# Volume 14 — SOP manual

| Field        | Value                             |
| ------------ | --------------------------------- |
| Status       | `review`                          |
| Stage        | 1                                 |
| Owner        | Ops lead                          |
| Last updated | 2026-07-22                        |
| Depends on   | Vol 09 · Vol 11 · Vol 18 · Vol 22 |

---

## 1. Scope

Standard operating procedures for **day-to-day readiness operations**. Product UX details live in Stage 2 volumes; this volume is how humans run the business.

**Stage keys:** [STAGE-MODEL.md](../../STAGE-MODEL.md)  
**Claims:** [CLAIM-LIBRARY.md](../../CLAIM-LIBRARY.md)

**Non-goals:** Legal advice; live unsupervised bureau filing; LOS underwriting.

## 2. SOP index

| ID     | Procedure                                  | Owner                   |
| ------ | ------------------------------------------ | ----------------------- |
| SOP-01 | New borrower intake                        | Case manager            |
| SOP-02 | Credit report intake & analysis queue      | Ops                     |
| SOP-03 | Findings review (Metro2 / FCRA / ID theft) | Reviewer                |
| SOP-04 | Lending Readiness Score publish / revise   | Ops lead                |
| SOP-05 | Action-plan task management                | Case manager            |
| SOP-06 | Dispute letter draft → review → send       | Case manager + reviewer |
| SOP-07 | Partner referral accept / decline          | Partner success         |
| SOP-08 | Weekly partner digest                      | Partner success         |
| SOP-09 | Readiness package export for lender        | Ops                     |
| SOP-10 | Escalation & incident                      | Ops lead / founder      |
| SOP-11 | Monthly borrower progress review           | Case manager            |

---

## 3. Core procedures (summaries)

### SOP-01 — New borrower intake

1. Confirm consent / disclosures.
2. Create/link case + portal invite (Vol 11).
3. Capture mortgage intent + partner referral IDs if any.
4. Set next check-in date.
5. Log welcome note (no guarantee language).

### SOP-02 — Credit report intake

1. Receive tri-bureau (or available) reports via approved channel.
2. Attach to case; verify identity match.
3. Enqueue analysis (engine + human review gate).
4. If incomplete bureau set → note limitation on score.

### SOP-03 — Findings review

1. Review automated findings; mark accept / override with reason.
2. Flag identity-theft indicators for compliance path.
3. Never auto-label fraud without staff confirmation.
4. Publish findings summary suitable for borrower-safe language.

### SOP-04 — Score publish / revise

1. Confirm inputs complete enough for advisory score.
2. Publish band + drivers (Vol 22 when detailed).
3. On material report change → re-run and version score.
4. Notify borrower + partner per SLA.

### SOP-05 — Action plan

1. Map findings → prioritized tasks.
2. Assign owner (borrower vs staff).
3. Track completion; unblock stuck tasks within 2 business days of ping.

### SOP-06 — Dispute workflow (staff-mediated)

1. Eligibility check (not unsupervised filing).
2. Draft letter / portal package.
3. Reviewer approve.
4. Operator send / file via approved channel.
5. Record send date; start reinvestigation tracking if applicable.
6. **Never** auto-file without human approve.

### SOP-07 — Referral accept / decline

1. Validate partner membership.
2. Accept → link borrower + ack within SLA.
3. Decline → reason code + notify partner (no PII dump).

### SOP-08 — Weekly digest

1. Pull open referrals by partner.
2. Stage + blocker + next date only.
3. Send; archive copy in CRM.

### SOP-09 — Readiness package export

1. Confirm package eligibility checklist.
2. Generate operator-gated export (advisory disclaimer).
3. Deliver to authorized LO only.
4. Audit log access.

### SOP-10 — Escalation & incident

Follow Vol 09 severity table. Security / PII → founder + counsel immediately.

### SOP-11 — Monthly progress

1. Score / task / education deltas.
2. Borrower-facing summary.
3. Partner note if referred.

---

## 4. Record-keeping

| Record          | Retention (draft — counsel)   |
| --------------- | ----------------------------- |
| Case notes      | Per platform policy           |
| Dispute sends   | Per FCRA ops policy           |
| Partner digests | 24 months minimum recommended |
| Access audits   | Per enterprise policy         |

## 5. Open decisions

- [ ] Exact retention periods with counsel
- [ ] Which steps are product-enforced vs checklist-only

## Approval

| Role       | Name | Date | Sign-off |
| ---------- | ---- | ---- | -------- |
| Ops lead   |      |      | ☐        |
| Compliance |      |      | ☐        |
