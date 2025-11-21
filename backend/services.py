from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Category


@dataclass
class ClassificationResult:
    category: Category
    reason: str


KEYWORD_MAP: dict[Category, set[str]] = {
    Category.PROJECTS: {"deliverable", "deadline", "milestone", "launch", "proposal"},
    Category.AREAS: {"process", "habit", "maintenance", "operations", "health"},
    Category.RESOURCES: {"reference", "ideas", "research", "learning", "snippet", "template"},
    Category.ARCHIVES: {"archive", "completed", "done", "past"},
}


def classify(content: str, title: str | None = None, tags: Iterable[str] | None = None) -> ClassificationResult:
    text = f"{title or ''} {content}".lower()
    tag_text = " ".join(tags or []).lower()
    text_blob = f"{text} {tag_text}"

    scores: dict[Category, int] = {category: 0 for category in Category}
    for category, keywords in KEYWORD_MAP.items():
        scores[category] = sum(1 for word in keywords if word in text_blob)

    # Prioritize explicit mentions of PARA buckets when present
    for category in Category:
        if category.value in text_blob:
            scores[category] += 2

    best_category = max(scores, key=scores.get)
    reason = "Heuristic classification based on keywords: " + ", ".join(
        f"{cat.value}={score}" for cat, score in scores.items()
    )
    return ClassificationResult(category=best_category, reason=reason)
