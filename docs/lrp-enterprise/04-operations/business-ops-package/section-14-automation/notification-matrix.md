# Notification Matrix

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Maps who gets notified, on which channel, for each event. Implement via `apps/api` notifications module + worker delivery jobs.

---

## Legend

| Code | Channel                               |
| ---- | ------------------------------------- |
| E    | Email                                 |
| S    | SMS (TCPA consent required)           |
| I    | In-app (`/portal`, `/lender`, `/crm`) |
| T    | CRM task / activity                   |
| —    | None                                  |

---

## Partner / referral events

| Event                     | Partner Success | Credit Specialist | Referring LO | Realtor          | Borrower      |
| ------------------------- | --------------- | ----------------- | ------------ | ---------------- | ------------- |
| Website contact (B2B)     | E+I+T           | —                 | —            | —                | —             |
| Referral submitted        | E+I+T           | E+I+T             | E+I          | E+I (if realtor) | E (thank-you) |
| Referral assigned         | I+T             | E+I               | I            | —                | —             |
| Consultation scheduled    | E+I             | E+I               | I            | I (opt)          | E+S+I         |
| Consultation completed    | E+I+T           | E+I               | E+I          | E (opt)          | E+I           |
| Status report published   | I               | —                 | E+I          | E (opt)          | E+I           |
| Mortgage Ready (advisory) | E+I             | I                 | E+I          | E (opt)          | E+I           |
| Partner inactive 30d      | E+T             | —                 | —            | —                | —             |

---

## Borrower / case events

| Event                                | Borrower   | Case owner | Partner (authorized) |
| ------------------------------------ | ---------- | ---------- | -------------------- |
| Portal invite                        | E+I        | I          | —                    |
| Task due soon                        | E+I+S(opt) | I          | —                    |
| Task overdue                         | E+I        | E+I+T      | —                    |
| Document uploaded                    | I          | I+T        | —                    |
| Document needs attention             | E+I        | E+I+T      | —                    |
| Dispute letter ready for review      | —          | E+I+T      | —                    |
| Dispute letter sent (staff-approved) | E+I        | I          | I (if authorized)    |
| Readiness report available           | E+I        | I          | E+I (if authorized)  |

---

## System / ops events

| Event                                 | Recipients           | Channel |
| ------------------------------------- | -------------------- | ------- |
| Worker job failed (retries exhausted) | Eng on-call + ops    | E+I     |
| SMS/email deliverability alert        | Ops                  | E+I     |
| SLA breach (referral ack)             | Partner Success lead | E+I+T   |

---

## Template rules

1. Every external message: brand + short disclaimer when readiness/score mentioned.
2. No approval/funding language.
3. Preference center / unsubscribe honored for marketing; transactional ops may continue per counsel policy.
4. Log `notification_id`, `template_key`, `org_id`, `case_id`/`partner_id` in audit.
