# FAQ Catalog

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field | Value                                                                       |
| ----- | --------------------------------------------------------------------------- |
| Hub   | `/faqs` (`apps/lrp-web` + `src/content/faqs`)                               |
| Rule  | Answers must stay claim-library locked; expand landings with `#faq` anchors |

---

## Global FAQ themes (required)

### About LRP

**Q: What does Lending Readiness Partners do?**  
A: We help borrowers prepare for a financing conversation through education, structured tasks, and advisory progress tracking—while keeping referring partners informed. We are not a lender and do not approve loans.

**Q: Are you a credit repair company that guarantees score increases?**  
A: No. We do not guarantee score outcomes, approvals, or funding. Where dispute work is appropriate, it is staff-mediated.

**Q: What is the Lending Readiness Score™?**  
A: An advisory tool for organizing credit and documentation work. It is not a bureau credit score and not an underwriting decision.

### For lenders / LOs

**Q: Will you underwrite or pre-approve my borrowers?**  
A: No. Your team underwrites. We support readiness and partner visibility.

**Q: How do referrals work?**  
A: Refer → Plan → Update → Return. See the partner kit and Section 4 referral tracker.

**Q: What marketing language can my branch use?**  
A: Claim-safe materials from the partner kit only—never guaranteed approval or fabricated FICO.

### For realtors

**Q: What can I tell a buyer who didn’t qualify yet?**  
A: That “not yet” can still have a clear plan, and their loan officer can involve Lending Readiness Partners. Do not promise approval timelines.

**Q: Do I need to stop working with my preferred lender?**  
A: No. We coordinate with the borrower’s lender relationship.

### For borrowers

**Q: Will you get me a mortgage?**  
A: No. We help you prepare for the next financing conversation with your loan officer.

**Q: How do I get started?**  
A: Ask your loan officer or realtor about Lending Readiness Partners, or contact us and we will route you appropriately.

### Compliance / privacy

**Q: How is my information handled?**  
A: See our privacy policy and electronic consent (Section 3). Client credit detail stays in secured case systems—not in public marketing forms.

---

## Landing `#faq` subsets

| Path                         | Include                                              |
| ---------------------------- | ---------------------------------------------------- |
| `/lenders#faq`               | Timing, guarantees, underwriting boundary, reports   |
| `/realtors#faq`              | What agents can say, preferred lender, buyer dignity |
| `/borrowers#faq`             | What to expect, portal, no approval promises         |
| `/resources/partner-kit/faq` | Kit contents, training, referral form                |

---

## Editorial process

1. Draft in this catalog or `apps/lrp-web` content module.
2. Claim-library check.
3. Compliance review for dispute / privacy answers.
4. Publish; keep JSON-LD FAQPage schema on `/faqs`.
