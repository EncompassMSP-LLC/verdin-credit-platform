"""Generate Business Ops Package Section 10 social content banks (claim-safe)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

DISCLAIMER = (
    "Lending Readiness Score™ is advisory and not a loan approval or underwriting decision."
)
TAGLINE = "Helping More Borrowers Become Lending Ready."
BRAND = "Lending Readiness Partners"

PILLARS = [
    "Readiness is more than a single number—it is habits, documents, and time.",
    'When the answer is "not yet," your borrower still deserves a clear plan.',
    "Loan officers underwrite. We help borrowers prepare for the next conversation.",
    "Partner visibility without underwriting confusion.",
    "Staff-mediated process. Claim-safe communication. Dignity-first coaching.",
    "Utilization, collections, inquiries, and documentation—each needs a plan.",
    TAGLINE,
    "Advisory progress beats radio silence.",
    "Ask before applying for new credit while you prepare.",
    "Education first. Hype never.",
    "A clear roadmap beats a vague promise.",
    "Mortgage conversations go better with organized docs.",
    "We are not a lender—and we never guarantee approval.",
    "Realtors: keep buyers moving with a readiness plan, not radio silence.",
    "Credit unions and community banks: claim-safe partnership language matters.",
]

CTAS = [
    "Learn more with your loan officer.",
    "Lenders: book a briefing.",
    "Realtors: ask about our partner kit.",
    "Start with one conversation this week.",
    "Ask your LO about Lending Readiness Partners.",
    "Scan the partner kit for resources.",
    "Borrowers: start with the document checklist.",
    "Partners: send a referral in a few minutes.",
]


def write_posts(path: Path, n: int, title: str, opener: str) -> None:
    lines = [
        f"# {title} ({n})",
        "",
        f"> {BRAND} · {TAGLINE}",
        f"> All posts are claim-safe. {DISCLAIMER}",
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


def write_story_graphics(path: Path, n: int) -> None:
    lines = [
        f"# Story graphics briefs ({n})",
        "",
        f"> Vertical 9:16. Brand + short line + optional CTA. {DISCLAIMER}",
        "",
    ]
    frames = [
        ("Brand lockup", TAGLINE),
        ("Myth vs fact", "No guaranteed approval—ever."),
        ("Checklist tease", "Docs ready before the lender conversation."),
        ("LO tip", "Refer in minutes. Stay in the loop."),
        ("Borrower tip", "One habit this week beats a vague goal."),
        ("Score note", "Advisory readiness ≠ FICO."),
        ("Partner CTA", "Book a briefing."),
        ("Seminar invite", "Homebuyer education night."),
    ]
    for i in range(1, n + 1):
        title, line = frames[(i - 1) % len(frames)]
        lines += [
            f"## {i}. {title}",
            "",
            f"**On-frame copy:** {line}",
            "",
            f"**Footer:** {BRAND}",
            "",
            f"_{DISCLAIMER}_",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_reel_scripts(path: Path, n: int) -> None:
    lines = [
        f"# Reel scripts ({n})",
        "",
        f"> 15–30 sec. Talk-to-camera or simple B-roll. {DISCLAIMER}",
        "",
    ]
    hooks = [
        "Not ready for a mortgage conversation yet?",
        "Your LO is not a credit coach—and that’s okay.",
        "Stop promising score miracles.",
        "Here’s what “lending ready” actually means.",
        "Three docs to gather this week.",
        "Partners: here’s our referral loop in 20 seconds.",
    ]
    for i in range(1, n + 1):
        h = hooks[(i - 1) % len(hooks)]
        p = PILLARS[(i - 1) % len(PILLARS)]
        lines += [
            f"## {i}. Reel",
            "",
            f"**Hook:** {h}",
            "",
            f"**Body:** {p}",
            "",
            f"**Close:** {TAGLINE} — {BRAND}",
            "",
            f"**On-screen disclaimer:** {DISCLAIMER}",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_carousels(path: Path, n: int) -> None:
    lines = [
        f"# Canva carousel templates ({n})",
        "",
        f"> 5–7 slides each. Spec for Canva; no fabricated FICO charts. {DISCLAIMER}",
        "",
    ]
    themes = [
        ("What lending ready means", ["Definition", "Docs", "Habits", "Partner role", "CTA"]),
        ("LO referral loop", ["Refer", "Plan", "Update", "Hand-back", "CTA"]),
        ("Myths", ["Wipe credit?", "Guaranteed approval?", "AI auto-file?", "Truth", "CTA"]),
        ("Borrower week-one", ["Checklist", "Goals", "Consult", "Next step", "CTA"]),
        ("Realtor handoff", ["When to refer", "What to say", "What not to say", "Seminar", "CTA"]),
    ]
    for i in range(1, n + 1):
        title, slides = themes[(i - 1) % len(themes)]
        lines += [f"## {i}. {title}", ""]
        for si, s in enumerate(slides, 1):
            lines.append(f"{si}. {s}")
        lines += ["", f"_{DISCLAIMER}_", "", "---", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_posts(ROOT / "facebook-posts.md", 250, "Facebook posts", "FB")
    write_posts(ROOT / "linkedin-posts.md", 250, "LinkedIn posts", "LI")
    write_posts(ROOT / "instagram-posts.md", 250, "Instagram posts", "IG")
    write_posts(ROOT / "threads-posts.md", 250, "Threads posts", "TH")
    write_posts(ROOT / "x-posts.md", 100, "X (Twitter) posts", "X")
    write_story_graphics(ROOT / "story-graphics.md", 150)
    write_reel_scripts(ROOT / "reel-scripts.md", 100)
    write_carousels(ROOT / "canva-carousels.md", 100)
    readme = ROOT / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Section 10 — Marketing Expansion",
                "",
                f"**{BRAND}** · {TAGLINE}",
                "",
                "Generated claim-safe content banks. Regenerate with:",
                "",
                "```bash",
                "python docs/lrp-enterprise/04-operations/business-ops-package/section-10-marketing-expansion/_generate_banks.py",
                "```",
                "",
                "| Asset | Count | File |",
                "| ----- | ----- | ---- |",
                "| Facebook posts | 250 | [`facebook-posts.md`](facebook-posts.md) |",
                "| LinkedIn posts | 250 | [`linkedin-posts.md`](linkedin-posts.md) |",
                "| Instagram posts | 250 | [`instagram-posts.md`](instagram-posts.md) |",
                "| Threads posts | 250 | [`threads-posts.md`](threads-posts.md) |",
                "| X (Twitter) posts | 100 | [`x-posts.md`](x-posts.md) |",
                "| Story graphics | 150 | [`story-graphics.md`](story-graphics.md) |",
                "| Reel scripts | 100 | [`reel-scripts.md`](reel-scripts.md) |",
                "| Canva carousels | 100 | [`canva-carousels.md`](canva-carousels.md) |",
                "",
                f"_{DISCLAIMER}_",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("Section 10 banks written to", ROOT)


if __name__ == "__main__":
    main()
