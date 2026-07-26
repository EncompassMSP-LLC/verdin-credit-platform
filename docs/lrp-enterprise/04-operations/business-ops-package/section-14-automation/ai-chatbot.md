# AI Chatbot (Gated)

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field    | Value                                                                    |
| -------- | ------------------------------------------------------------------------ |
| Surfaces | Marketing site FAQ helper · optional portal helper                       |
| Gate     | ADR-012 / `require_llm_ready()` · claim library · no unsupervised filing |

---

## 1. Allowed scopes

| Bot                     | Audience               | May do                                                                 |
| ----------------------- | ---------------------- | ---------------------------------------------------------------------- |
| Public FAQ bot          | Anonymous web          | Answer from FAQ/KB; route to contact                                   |
| Portal helper           | Authenticated borrower | Explain tasks, point to docs, summarize next steps **already on file** |
| Partner helper (future) | LO / realtor login     | Explain referral status fields; link to kit                            |

---

## 2. Must refuse / escalate

- Guaranteed approval, funding, or score outcomes
- Legal conclusions / “FCRA violation proven”
- Filing disputes or contacting bureaus
- Inventing account-level facts not in the case
- Cross-tenant data
- Medical / unrelated advice

Escalation path: “Connect me with a specialist” → CRM task + human reply SLA.

---

## 3. System prompt constraints (ops spec)

1. Full brand name before LRP
2. State advisory nature of Lending Readiness Score™ when discussed
3. Cite only approved KB/FAQ snippets
4. If unsure → escalate; never guess credit data
5. Log prompt/response IDs for audit (no unnecessary PII in logs)

---

## 4. Implementation notes

- Prefer retrieval over free-form generation (FAQ + KB from Section 12)
- Disable public bot until counsel/marketing sign-off on responses corpus
- Portal bot behind feature flag + org LLM policy
- No tool-calling that mutates dispute letters without staff

---

## 5. Success metrics

| Metric                            | Target                         |
| --------------------------------- | ------------------------------ |
| Deflection to FAQ                 | Track only — not vanity        |
| Escalation rate                   | Monitor quality                |
| Claim violations caught in review | Zero tolerance in prod samples |
