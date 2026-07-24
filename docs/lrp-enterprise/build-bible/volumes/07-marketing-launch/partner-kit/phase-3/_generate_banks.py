"""Generate Phase 3 social + email content banks (claim-safe templates)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOCIAL = ROOT / "10-social-media"
EMAIL = ROOT / "11-email-campaigns"
SOCIAL.mkdir(parents=True, exist_ok=True)
EMAIL.mkdir(parents=True, exist_ok=True)

PILLARS = [
    "Readiness is more than a single number—it is habits, documents, and time.",
    'When the answer is "not yet," your borrower still deserves a clear plan.',
    "Loan officers underwrite. We help borrowers prepare for the next conversation.",
    "Partner visibility without underwriting confusion.",
    "Staff-mediated process. Claim-safe communication. Dignity-first coaching.",
    "Utilization, collections, inquiries, and documentation—each needs a plan.",
    "Helping More Borrowers Become Lending Ready.",
    "Advisory progress beats radio silence.",
    "Ask before applying for new credit while you prepare.",
    "Education first. Hype never.",
]
CTAS = [
    "Learn more with your loan officer.",
    "Lenders: book a briefing.",
    "Realtors: ask about our co-channel kit.",
    "Scan the partner kit for resources.",
    "Start with one conversation this week.",
]
DISCLAIMER = (
    "Lending Readiness Score™ is advisory and not a loan approval or underwriting decision."
)


def write_posts(path: Path, n: int, audience: str, opener: str) -> None:
    lines = [
        f"# {audience} posts ({n})",
        "",
        f"> All posts include claim-safe framing. {DISCLAIMER}",
        "",
    ]
    for i in range(1, n + 1):
        p = PILLARS[(i - 1) % len(PILLARS)]
        c = CTAS[(i - 1) % len(CTAS)]
        lines += [
            f"## {i}. {opener} ({i})",
            "",
            p,
            "",
            c,
            "",
            f"_{DISCLAIMER}_",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_success_stories() -> None:
    lines = [
        "# Borrower success stories (fictional composites)",
        "",
        "> Fictional. Not real testimonials. No fabricated FICO before/after.",
        "",
        DISCLAIMER,
        "",
    ]
    archetypes = [
        ("Maya", "high utilization", "built a payment priority list and stayed in touch with her LO"),
        ("Jordan", "a collection and missing docs", "organized letters and completed a document checklist"),
        ("Sam", "inquiry timing concerns", "paused new applications and coordinated shopping with the LO"),
        ("Alex", "thin credit file", "focused on on-time habits and documentation readiness"),
        ("Riley", "charge-off questions", "gathered records and followed a staff-guided plan"),
    ]
    for i in range(1, 51):
        name, issue, action = archetypes[(i - 1) % len(archetypes)]
        lines += [
            f"## Story {i} — {name} (composite)",
            "",
            f"**Situation:** Motivated borrower facing {issue}.",
            "",
            f"**Work:** With Lending Readiness Partners, they {action}.",
            "",
            "**Framing:** Progress toward a financing conversation—not a promised approval.",
            "",
            f"_{DISCLAIMER}_",
            "",
            "---",
            "",
        ]
    (SOCIAL / "success-stories.md").write_text("\n".join(lines), encoding="utf-8")


def write_story_graphics() -> None:
    lines = [
        "# Story graphics copy (100)",
        "",
        "Format: 1080×1920. One line + tagline + disclaimer footer.",
        "",
    ]
    story_lines = [
        "Not yet can still have a plan.",
        "Ask your LO about readiness support.",
        "Visibility for partners. Clarity for borrowers.",
        "Education over hype.",
        "Prepare. Then talk financing.",
        "Staff-mediated. Claim-safe.",
        "Your next step beats waiting in silence.",
        "Documents matter as much as habits.",
        "Readiness is a process.",
        "Helping More Borrowers Become Lending Ready.",
    ]
    for i in range(1, 101):
        lines += [
            f"## Story {i}",
            "",
            f"Text: {story_lines[(i - 1) % len(story_lines)]}",
            "",
            "Footer: Lending Readiness Partners",
            "",
            f"Disclaimer: {DISCLAIMER}",
            "",
            "---",
            "",
        ]
    (SOCIAL / "story-graphics.md").write_text("\n".join(lines), encoding="utf-8")


def write_reels() -> None:
    lines = [
        "# Reels scripts (30)",
        "",
        "15–45 seconds. On-screen text + VO. No guarantee claims.",
        "",
    ]
    for i in range(1, 31):
        lines += [
            f"## Reel {i}",
            "",
            f"HOOK: {PILLARS[(i - 1) % len(PILLARS)][:70]}",
            "",
            "VO: Lending Readiness Partners helps borrowers organize education and next "
            "steps while keeping loan officers informed.",
            "",
            "VO: We do not guarantee approvals. We help prepare for the next financing "
            "conversation.",
            "",
            "END CARD: Tagline + QR to /lenders or kit",
            "",
            f"Disclaimer on-screen: {DISCLAIMER}",
            "",
            "---",
            "",
        ]
    (SOCIAL / "reels-scripts.md").write_text("\n".join(lines), encoding="utf-8")


SUBJECTS = {
    "lenders": [
        "Help more borrowers become lending ready",
        "When a file is not ready yet",
        "Introducing our Mortgage Readiness Partnership",
        "Keep more clients from walking away",
        "What partners see (and do not decide)",
        "Claim-safe co-marketing for your brand",
        "A 15-minute briefing for your LO team",
        "Referral loop in four steps",
        "Advisory readiness vs underwriting",
        "Pilot a 90-day design partnership",
        "Weekly digests without PII overload",
        "Why guarantee culture hurts lenders",
        "Rescore prep support—without promises",
        "Security and tenant isolation at a glance",
        "Next step: digital partner kit",
    ],
    "realtors": [
        "Keep buyers engaged when financing needs time",
        "Scripts your agents can defend",
        "Preferred lender + readiness path",
        'Dignity-first conversations for "not yet"',
        "What you can say (and should not)",
        "Shared stages without shame",
        "Co-channel kit for your office",
        "How updates work with LOs",
        "Open house leave-behind ideas",
        "Partner with readiness—not hype",
        "Buyer education nights (framework)",
        "Rack cards for your lobby",
        "When to refer vs when to wait",
        "FAQ for buyer agents",
        "Book a realtor briefing",
    ],
    "borrowers": [
        "Welcome—here is how readiness works",
        "Your next three actions",
        "Why documentation matters",
        "How we keep your loan officer informed",
        "Utilization in plain language",
        "Collections: organize before you panic",
        "Inquiries: ask before you apply",
        "Budget basics for home goals",
        "You are building toward lending ready",
        "Portal tip: check tasks weekly",
        "Questions to bring to your LO",
        "Identity concerns—what to do first",
        "Celebrating progress without score myths",
        "Preparing for your next conversation",
        "We are here—still no guarantees, just a plan",
    ],
    "past-clients": [
        "Checking in on your home goals",
        "Habits that protect hard-won progress",
        "Thinking about a future refinance conversation?",
        "Share us with someone who needs a plan",
        "New education resources from LRP",
        "How to talk to an LO after a pause",
        "Document folder refresher",
        "Avoid new credit surprises",
        "We still do not guarantee approvals—and that is the point",
        "Partner kit for your LO or realtor",
        "Community workshop invite (optional)",
        "Update your contact preferences",
        "When life changes, update your plan",
        "Thank you for trusting a claim-safe process",
        "Stay connected with Lending Readiness Partners",
    ],
    "referral-partners": [
        "Thank you for partnering with LRP",
        "Referral form refresher",
        "SLA and update cadence",
        "Co-branded marketing review reminder",
        "New leave-behind folder available",
        "Quick reference for your front desk",
        "How to escalate a stuck file",
        "QBR agenda preview",
        "Digital kit download links",
        "What good looks like in week one",
        "Compliance posture one-pager",
        "Realtor vs LO referral tips",
        "Portal seats and access hygiene",
        "Share wins as process stories—not FICO claims",
        "Book your next partnership review",
    ],
}

AUDIENCES = {
    "lenders": "Mortgage lenders",
    "realtors": "Realtors",
    "borrowers": "Borrowers",
    "past-clients": "Past clients",
    "referral-partners": "Referral partners",
}


def write_emails() -> None:
    for key, title in AUDIENCES.items():
        subs = SUBJECTS[key]
        lines = [
            f"# Email campaign — {title} ({len(subs)} emails)",
            "",
            f"Footer every email: tagline + {DISCLAIMER}",
            "",
        ]
        for i, sub in enumerate(subs, 1):
            lines += [
                f"## Email {i}",
                "",
                f"**Subject:** {sub}",
                "",
                "**Preview:** Lending Readiness Partners — claim-safe mortgage readiness support.",
                "",
                "**Body:**",
                "",
                "Hello,",
                "",
                PILLARS[(i - 1) % len(PILLARS)],
                "",
                "Lending Readiness Partners partners with lenders, realtors, and borrowers "
                "to organize education, tasks, and progress updates. We do not guarantee "
                "loan approval, terms, or funding.",
                "",
                f"**CTA:** {CTAS[(i - 1) % len(CTAS)]}",
                "",
                "Helping More Borrowers Become Lending Ready.",
                "",
                f"_{DISCLAIMER}_",
                "",
                "---",
                "",
            ]
        (EMAIL / f"{key}.md").write_text("\n".join(lines), encoding="utf-8")

    (EMAIL / "README.md").write_text(
        "\n".join(
            [
                "# 11 — Email Campaigns",
                "",
                "| Audience | File | Count |",
                "| -------- | ---- | ----- |",
                "| Mortgage lenders | [lenders.md](lenders.md) | 15 |",
                "| Realtors | [realtors.md](realtors.md) | 15 |",
                "| Borrowers | [borrowers.md](borrowers.md) | 15 |",
                "| Past clients | [past-clients.md](past-clients.md) | 15 |",
                "| Referral partners | [referral-partners.md](referral-partners.md) | 15 |",
                "",
                "Expand Phase 2 drip outlines into full send-ready copy. "
                "All footers claim-library locked.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    write_posts(SOCIAL / "facebook-posts.md", 100, "Facebook", "FB")
    write_posts(SOCIAL / "instagram-posts.md", 100, "Instagram", "IG")
    write_posts(SOCIAL / "linkedin-posts.md", 100, "LinkedIn", "LI")
    write_posts(SOCIAL / "realtor-posts.md", 50, "Realtor-focused", "Realtor")
    write_posts(SOCIAL / "loan-officer-posts.md", 50, "Loan Officer-focused", "LO")
    write_success_stories()
    write_story_graphics()
    write_reels()
    write_emails()
    print("ok", len(list(SOCIAL.glob("*.md"))), "social,", len(list(EMAIL.glob("*.md"))), "email")


if __name__ == "__main__":
    main()
