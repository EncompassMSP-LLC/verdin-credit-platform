# SMS Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field    | Value                                                 |
| -------- | ----------------------------------------------------- |
| Platform | `notifications` SMS campaign + deliverability modules |
| Gate     | Explicit TCPA / communication authorization           |

---

## 1. Allowed use cases

| Use                    | Example                                           |
| ---------------------- | ------------------------------------------------- |
| Appointment reminders  | T-24h, T-1h consultation reminder                 |
| Portal task nudge      | “You have a readiness task due tomorrow” (opt-in) |
| Referral ack (partner) | Short LO ack with referral number                 |

---

## 2. Forbidden

- Marketing blasts without consent
- Score promises (“you’ll hit 700”)
- Approval/funding claims
- Sharing credit report details over SMS

---

## 3. Template patterns (claim-safe)

**Appointment reminder**

> Lending Readiness Partners: Reminder — consultation [date/time]. Reply STOP to opt out. Not a loan approval.

**Task nudge**

> Reminder: you have a portal task waiting. Sign in: [link]. Reply STOP to opt out.

**LO referral ack**

> LRP: Referral [number] received. We’ll follow up per SLA. Reply STOP to opt out.

---

## 4. Suppression

| Event                        | Action                                        |
| ---------------------------- | --------------------------------------------- |
| STOP / opt-out               | Suppress SMS; keep email if allowed           |
| Carrier failure / spam block | Pause campaign; alert ops (deliverability)    |
| Quiet hours                  | Respect org timezone window (e.g. 9–20 local) |

---

## 5. Implementation map

- Campaign processor / delivery jobs already in `apps/worker` SMS marketing paths
- Prefer transactional SMS separate from marketing campaigns
- Log deliverability metrics for ops review
