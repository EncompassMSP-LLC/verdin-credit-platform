# Volume 09 — Customer service playbook

| Field        | Value                 |
| ------------ | --------------------- |
| Status       | `draft`               |
| Stage        | 1                     |
| Owner        | Partner success / Ops |
| Last updated | 2026-07-22            |

---

## 1. Service mission

Respond with clarity and compliance. Borrowers feel guided; partners feel informed; no one is promised a loan.

## 2. Channels

| Channel                | Use for              | SLA (draft)                          |
| ---------------------- | -------------------- | ------------------------------------ |
| In-app messages        | Borrower ↔ staff     | First response 1 business day        |
| Partner email / digest | LO / realtor updates | Digest weekly; ad-hoc 1 business day |
| Phone                  | Escalations          | Same-day callback for P1             |
| Portal notifications   | System events        | Near real-time                       |

## 3. Personas & tone

| Audience       | Tone                                      |
| -------------- | ----------------------------------------- |
| Borrower       | Calm, plain language, educational         |
| LO             | Concise, stage + blockers + next date     |
| Realtor        | Expectation-setting; no underwriting talk |
| Operator admin | Precise; link to case IDs                 |

## 4. Ticket taxonomy

| Type                    | Example              | Owner                            |
| ----------------------- | -------------------- | -------------------------------- |
| Portal access           | Can’t log in         | Support / eng                    |
| Document                | Upload failed        | Ops                              |
| Score / report question | “Why is my band X?”  | Ops (+ compliance if claim risk) |
| Partner status          | “Where is referral?” | Partner success                  |
| Billing                 | Invoice              | Founder / finance                |
| Compliance concern      | Marketing language   | Compliance                       |

## 5. Macros (approved themes)

- Welcome / how readiness works (advisory)
- Document checklist reminder
- Stage change explanation
- Partner weekly digest template
- “We cannot guarantee approval” redirect

Full macro text library: add `macros.md` in this folder as Stage 1 deepens.

## 6. Escalation

| Severity | Definition                      | Action                           |
| -------- | ------------------------------- | -------------------------------- |
| P1       | Data leak, security, harassment | Founder + compliance immediately |
| P2       | Partner SLA breach; portal down | Ops lead + eng                   |
| P3       | Single-borrower friction        | Queue                            |

## 7. Partner SLA (draft)

| Commitment                | Target                                |
| ------------------------- | ------------------------------------- |
| Referral acknowledged     | 1 business day                        |
| First status after accept | 3 business days                       |
| Weekly digest             | If opted in                           |
| Readiness export request  | 2 business days when package eligible |

## 8. Quality checks

- [ ] No guarantee language in replies
- [ ] PII minimized in email
- [ ] Case/referral IDs cited
- [ ] Angry partner → manager within 4 business hours

## Approval

| Role       | Name | Date | Sign-off |
| ---------- | ---- | ---- | -------- |
| Founder    |      |      | ☐        |
| Compliance |      |      | ☐        |
