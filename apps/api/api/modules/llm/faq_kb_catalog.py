"""Approved LRP knowledge-base catalog for FAQ retrieval (LRP-405).

Answers are composed only from these articles. No generative external model
is required for the retrieval path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FaqAudience = Literal["borrower", "lender", "realtor", "staff"]


@dataclass(frozen=True, slots=True)
class KbArticle:
    id: str
    title: str
    body: str
    audiences: tuple[FaqAudience, ...]
    tags: tuple[str, ...]
    source_path: str


APPROVED_KB_ARTICLES: tuple[KbArticle, ...] = (
    KbArticle(
        id="kb.lending-readiness-definition",
        title="What is lending readiness?",
        body=(
            "Lending readiness is the operational state in which a borrower's credit posture, "
            "documentation quality, and partner workflows are clear enough for a lender to "
            "evaluate funding eligibility with confidence. It is a system outcome—not a single "
            "bureau score or a guarantee of approval."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("readiness", "definition", "score", "approval"),
        source_path="apps/lrp-web/src/content/faqs.ts#lending-readiness",
    ),
    KbArticle(
        id="kb.no-approval-guarantee",
        title="Does Lending Readiness Partners guarantee loan approval?",
        body=(
            "No. We never guarantee approval or funding. Lender underwriting, overlays, and "
            "applicable guidelines always govern. Our role is to make readiness visible, "
            "auditable, and actionable so qualified borrowers can move forward with fewer surprises."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("approval", "guarantee", "funding", "underwriting", "claim-library"),
        source_path="apps/lrp-web/src/content/faqs.ts#no-approval-guarantee",
    ),
    KbArticle(
        id="kb.audience-fit",
        title="Who is the platform built for?",
        body=(
            "Primary buyers are mid-market mortgage lenders and credit services operators. "
            "Realtors participate through preferred-partner programs. Borrowers are supported "
            "through advisors—not through aggressive direct-to-consumer credit hype."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("audience", "lender", "realtor", "borrower"),
        source_path="apps/lrp-web/src/content/faqs.ts#audience",
    ),
    KbArticle(
        id="kb.staff-mediated-actions",
        title="How do you handle compliance-sensitive credit actions?",
        body=(
            "High-risk actions are designed to be staff-mediated with audit trails and "
            "role-based controls. We do not market unsupervised dispute filing or black-box "
            "automation that bypasses professional judgment."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("compliance", "dispute", "filing", "staff", "automation"),
        source_path="apps/lrp-web/src/content/faqs.ts#compliance-actions",
    ),
    KbArticle(
        id="kb.not-a-los-replacement",
        title="Can LRP replace our LOS or underwriting stack?",
        body=(
            "No. Lending Readiness Partners complements your loan origination and credit "
            "decisioning stack by coordinating readiness workflows and partner signals. "
            "Underwriting judgment remains with the lender."
        ),
        audiences=("lender", "staff"),
        tags=("los", "underwriting", "lender", "stack"),
        source_path="apps/lrp-web/src/content/faqs.ts#los",
    ),
    KbArticle(
        id="kb.pricing",
        title="How does pricing work?",
        body=(
            "We offer Operator, Lender, and Network packages with annual platform fees and "
            "implementation support. Enterprise and multi-region deployments are scoped through "
            "a readiness briefing. See the Pricing page for package details."
        ),
        audiences=("lender", "staff"),
        tags=("pricing", "packages", "fees"),
        source_path="apps/lrp-web/src/content/faqs.ts#pricing",
    ),
    KbArticle(
        id="kb.implementation",
        title="What does an implementation typically include?",
        body=(
            "A typical pilot defines near-miss segments, readiness stages, partner handoffs, "
            "success metrics, and training for production, operations, and compliance "
            "stakeholders. Most design partners run a 60-day controlled pilot before broader rollout."
        ),
        audiences=("lender", "staff"),
        tags=("implementation", "pilot", "onboarding"),
        source_path="apps/lrp-web/src/content/faqs.ts#implementation",
    ),
    KbArticle(
        id="kb.data-isolation",
        title="Is borrower data shared across tenants or sold?",
        body=(
            "No. We do not sell borrower data and we do not expose unrestricted cross-tenant PII. "
            "Any aggregate insight programs require explicit governance and consent boundaries."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("privacy", "tenant", "pii", "data"),
        source_path="apps/lrp-web/src/content/faqs.ts#data-isolation",
    ),
    KbArticle(
        id="kb.realtor-usage",
        title="How do realtors use Lending Readiness Partners?",
        body=(
            "Realtors typically adopt LRP through preferred lender and operator partnerships. "
            "They receive plain-language readiness stages and expectation-setting guidance—"
            "without being asked to sell credit-repair claims."
        ),
        audiences=("realtor", "lender", "staff"),
        tags=("realtor", "partner", "readiness", "claims"),
        source_path="apps/lrp-web/src/content/faqs.ts#realtor",
    ),
    KbArticle(
        id="kb.getting-started",
        title="Where do I start?",
        body=(
            "Book a readiness briefing from the Contact page. Bring production, operations, and "
            "compliance stakeholders so we can scope a pilot against your fallout and cycle-time "
            "realities."
        ),
        audiences=("lender", "realtor", "staff"),
        tags=("start", "contact", "briefing"),
        source_path="apps/lrp-web/src/content/faqs.ts#start",
    ),
    KbArticle(
        id="kb.no-score-point-promises",
        title="Can you tell me how many credit-score points I will gain?",
        body=(
            "No. The platform does not estimate item-by-item point increases. Correcting "
            "inaccurate information may improve, leave unchanged, or temporarily change a "
            "consumer's credit profile; outcomes depend on the full file and lender models. "
            "Ask your advisor for case-specific, staff-reviewed guidance."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("score", "points", "fico", "guarantee", "claim-library"),
        source_path="docs/lrp-enterprise/claim-library#no-score-promises",
    ),
    KbArticle(
        id="kb.no-auto-dispute-filing",
        title="Will the platform automatically file my credit disputes?",
        body=(
            "No. Dispute letters and bureau submissions remain staff-mediated. The platform may "
            "help prepare drafts and track evidence, but it does not auto-send or unsupervised-file "
            "disputes."
        ),
        audiences=("borrower", "lender", "realtor", "staff"),
        tags=("dispute", "filing", "auto-send", "bureau"),
        source_path="docs/lrp-enterprise/claim-library#no-auto-filing",
    ),
    KbArticle(
        id="kb.borrower-portal-basics",
        title="What can borrowers see in the portal?",
        body=(
            "Borrowers can review readiness status, assigned tasks, documents, and advisory "
            "dispute suggestions prepared by staff. Personalized legal advice and underwriting "
            "predictions are out of scope for the FAQ assistant."
        ),
        audiences=("borrower", "staff"),
        tags=("portal", "borrower", "tasks", "documents"),
        source_path="docs/lrp-enterprise/borrower-portal#basics",
    ),
    KbArticle(
        id="kb.staff-faq-assistant-limits",
        title="What are the FAQ assistant limits for staff?",
        body=(
            "The FAQ assistant retrieves only approved knowledge-base articles, shows citations, "
            "and records an audit turn. It does not give personalized legal advice, invent case "
            "facts, or execute disputes. Staff can mark answers inaccurate for follow-up."
        ),
        audiences=("staff",),
        tags=("assistant", "limits", "staff", "audit"),
        source_path="docs/development/lrp-platform-v1.0-completion-checklist.md#lrp-405",
    ),
)


FALLBACK_ANSWER = (
    "I can only answer from the approved Lending Readiness Partners knowledge base. "
    "I do not have an approved article that answers that question. Please ask a staff advisor, "
    "or rephrase using platform topics such as readiness, disputes, partner roles, privacy, or pricing."
)

DISCLAIMER = (
    "Educational retrieval only. Not legal advice. Not a credit-score prediction. "
    "Not an underwriting or approval decision. Not an automatic dispute filing tool."
)
