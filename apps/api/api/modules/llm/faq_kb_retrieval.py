"""Deterministic FAQ/KB retrieval engine (LRP-405).

Grounded extractive answers only — no external generative calls, no case PII.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from api.modules.llm.faq_kb_catalog import (
    APPROVED_KB_ARTICLES,
    DISCLAIMER,
    FALLBACK_ANSWER,
    FaqAudience,
    KbArticle,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "are",
        "you",
        "can",
        "see",
        "how",
        "does",
        "what",
        "with",
        "from",
        "that",
        "this",
        "will",
        "into",
        "your",
        "our",
        "not",
    }
)

_INJECTION_PATTERNS = (
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts)",
    r"disregard (the )?(system|developer) (prompt|message)",
    r"you are now",
    r"act as (if|a|an|the)",
    r"jailbreak",
    r"system prompt",
    r"reveal (your|the) (system|hidden) (prompt|instructions)",
    r"do anything now",
)

_UNSUPPORTED_CLAIM_PATTERNS = (
    (
        r"\b(how many|what(?:'s| is)|will (my|the))?\s*(score|fico).{0,40}\b(point|points|increase|go up)\b",
        "kb.no-score-point-promises",
    ),
    (r"\bguarantee(d)? (approval|funding|loan)\b", "kb.no-approval-guarantee"),
    (
        r"\b(auto(matic(ally)?)?|unsupervised)\s+(file|filing|send|submit).{0,30}\bdispute",
        "kb.no-auto-dispute-filing",
    ),
    (r"\bwill (you|the platform) (file|submit|send) (my )?dispute", "kb.no-auto-dispute-filing"),
)


@dataclass(frozen=True, slots=True)
class Citation:
    article_id: str
    title: str
    source_path: str
    excerpt: str
    score: float


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    answer: str
    grounded: bool
    refused: bool
    refusal_reason: str | None
    citations: tuple[Citation, ...]
    matched_article_ids: tuple[str, ...]
    disclaimer: str


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in _STOPWORDS}


def _score_article(question_tokens: set[str], article: KbArticle) -> float:
    haystack = _tokens(f"{article.title} {article.body} {' '.join(article.tags)}")
    if not question_tokens or not haystack:
        return 0.0
    overlap = question_tokens & haystack
    if len(overlap) < 2:
        return 0.0
    return len(overlap) / len(question_tokens) + 0.15 * len(overlap) / max(len(haystack), 1)


def _detect_injection(question: str) -> bool:
    lowered = question.lower()
    return any(re.search(pattern, lowered) for pattern in _INJECTION_PATTERNS)


def _unsupported_article_id(question: str) -> str | None:
    lowered = question.lower()
    for pattern, article_id in _UNSUPPORTED_CLAIM_PATTERNS:
        if re.search(pattern, lowered):
            return article_id
    return None


def _article_by_id(article_id: str) -> KbArticle | None:
    for article in APPROVED_KB_ARTICLES:
        if article.id == article_id:
            return article
    return None


def _citation_from(article: KbArticle, score: float) -> Citation:
    excerpt = article.body if len(article.body) <= 240 else f"{article.body[:237]}..."
    return Citation(
        article_id=article.id,
        title=article.title,
        source_path=article.source_path,
        excerpt=excerpt,
        score=round(score, 4),
    )


def retrieve_faq_answer(*, question: str, audience: FaqAudience) -> RetrievalResult:
    cleaned = " ".join(question.strip().split())
    if not cleaned:
        return RetrievalResult(
            answer=FALLBACK_ANSWER,
            grounded=False,
            refused=True,
            refusal_reason="empty_question",
            citations=(),
            matched_article_ids=(),
            disclaimer=DISCLAIMER,
        )

    if _detect_injection(cleaned):
        return RetrievalResult(
            answer=(
                "I can only retrieve approved Lending Readiness Partners knowledge-base content. "
                "I will not follow instructions that attempt to override that policy."
            ),
            grounded=False,
            refused=True,
            refusal_reason="prompt_injection",
            citations=(),
            matched_article_ids=(),
            disclaimer=DISCLAIMER,
        )

    forced_id = _unsupported_article_id(cleaned)
    if forced_id:
        article = _article_by_id(forced_id)
        if article is not None and audience in article.audiences:
            citation = _citation_from(article, 1.0)
            return RetrievalResult(
                answer=article.body,
                grounded=True,
                refused=False,
                refusal_reason=None,
                citations=(citation,),
                matched_article_ids=(article.id,),
                disclaimer=DISCLAIMER,
            )

    q_tokens = _tokens(cleaned)
    scored: list[tuple[float, KbArticle]] = []
    for article in APPROVED_KB_ARTICLES:
        if audience not in article.audiences:
            continue
        score = _score_article(q_tokens, article)
        if score >= 0.28:
            scored.append((score, article))
    scored.sort(key=lambda item: (-item[0], item[1].id))

    if not scored:
        return RetrievalResult(
            answer=FALLBACK_ANSWER,
            grounded=False,
            refused=True,
            refusal_reason="no_approved_match",
            citations=(),
            matched_article_ids=(),
            disclaimer=DISCLAIMER,
        )

    top = scored[:3]
    primary = top[0][1]
    citations = tuple(_citation_from(article, score) for score, article in top)
    if len(top) == 1:
        answer = primary.body
    else:
        extra = " ".join(article.body for _, article in top[1:])
        answer = f"{primary.body}\n\nRelated approved guidance: {extra}"
    return RetrievalResult(
        answer=answer,
        grounded=True,
        refused=False,
        refusal_reason=None,
        citations=citations,
        matched_article_ids=tuple(article.id for _, article in top),
        disclaimer=DISCLAIMER,
    )
