# Portal Automation (Borrower & Partner)

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Surface      | App routes                 |
| ------------ | -------------------------- |
| Borrower     | `apps/lrp-web` `/portal/*` |
| Lender / LO  | `/lender/*`                |
| Internal CRM | `/crm/*`                   |

---

## 1. Borrower portal events

| Event                    | Automation                                        |
| ------------------------ | ------------------------------------------------- |
| Signup / invite accepted | Welcome email; create onboarding tasks            |
| First login              | Tour / checklist spotlight                        |
| Task completed           | Progress update; optional LO notify if authorized |
| All phase tasks done     | Specialist review task                            |
| Inactivity 7 / 14 days   | Nudge email; CS task at 14                        |
| Message from staff       | In-app + email                                    |

---

## 2. Lender workspace events

| Event                      | Automation                     |
| -------------------------- | ------------------------------ |
| New referral on LO book    | In-app badge + email per prefs |
| Status change (authorized) | In-app + optional email        |
| Report shared              | Notify LO                      |
| Export ready               | Notify requester               |

---

## 3. Preference defaults

| Audience | Default email                   | Default SMS       |
| -------- | ------------------------------- | ----------------- |
| Borrower | Transactional on; marketing off | Off until consent |
| LO       | Referral + weekly digest opt-in | Off               |
| Realtor  | Referral ack on                 | Off               |

User can change in portal/lender settings; automations honor preferences.

---

## 4. Security

- Magic links expire
- No full credit file in email deep links
- Partner sees progress only per authorization
- CRM staff actions audited

---

## 5. Tie-ins

- Section 12 thank-you + contact forms enqueue CRM + portal invites
- Section 5 health scores influence nurture intensity (not borrower-facing grades)
- Section 7 reports appear in portal when published
