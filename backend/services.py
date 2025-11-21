from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ParaBucket


@dataclass
class ClassificationResult:
    bucket: ParaBucket
    area_name: str | None
    project_outcome: str | None
    confidence: float
    method: str
    reason: str


AREA_MAP: dict[str, set[str]] = {
    "Cooking": {"recipe", "cook", "kitchen", "bake", "pancake", "dinner", "meal"},
    "Health": {"run", "workout", "gym", "sleep", "diet", "nutrition", "wellness"},
    "Finance": {"budget", "invest", "salary", "raise", "401k", "tax", "invoice", "expense"},
    "Gaming": {"game", "games", "gaming", "tarkov", "elden ring", "mapgenie", "steam"},
    "Learning": {"course", "learn", "tutorial", "lesson", "study", "class", "lecture"},
    "Travel": {"flight", "hotel", "trip", "airbnb", "itinerary", "booking"},
    "Work": {"meeting", "deck", "report", "okrs", "sprint", "roadmap", "requirements"},
}

ACTION_VERBS = {
    "make",
    "cook",
    "write",
    "publish",
    "send",
    "plan",
    "fix",
    "schedule",
    "set up",
    "create",
    "draft",
    "prepare",
    "build",
    "organize",
}

TIME_SIGNALS = {"today", "tomorrow", "this weekend", "by ", "due ", "next ", "asap", "tonight"}

TASK_MARKERS = {"todo", "to-do", "task", "deadline", "due", "finish", "complete"}


def _detect_area(text_blob: str) -> str | None:
    for area, keywords in AREA_MAP.items():
        if any(keyword in text_blob for keyword in keywords):
            return area
    return None


def classify(content: str, title: str | None = None, tags: Iterable[str] | None = None) -> ClassificationResult:
    text = f"{title or ''}\n{content}".lower()
    tag_text = " ".join(tags or []).lower()
    text_blob = f"{text} {tag_text}"

    has_time_signal = any(signal in text_blob for signal in TIME_SIGNALS)
    has_action_verb = any(verb in text_blob for verb in ACTION_VERBS)
    has_task_marker = any(marker in text_blob for marker in TASK_MARKERS)
    has_url = "http://" in text_blob or "https://" in text_blob or "www." in text_blob

    area_name = _detect_area(text_blob)

    is_project_like = has_action_verb and (has_time_signal or has_task_marker)

    if is_project_like:
        project_outcome = title or "Untitled project"
        reason = "Detected action and task cues indicative of a project."
        confidence = 0.72 if has_time_signal else 0.64
        return ClassificationResult(
            bucket=ParaBucket.PROJECT,
            area_name=area_name,
            project_outcome=project_outcome,
            confidence=confidence,
            method="heuristic",
            reason=reason,
        )

    if area_name:
        reason = f"Matched area keywords for {area_name}; treating as a resource within that area."
        return ClassificationResult(
            bucket=ParaBucket.RESOURCE,
            area_name=area_name,
            project_outcome=None,
            confidence=0.65,
            method="heuristic",
            reason=reason,
        )

    if has_url:
        reason = "Detected a link; defaulting to resource for reference material."
        return ClassificationResult(
            bucket=ParaBucket.RESOURCE,
            area_name=None,
            project_outcome=None,
            confidence=0.55,
            method="heuristic",
            reason=reason,
        )

    reason = "Defaulted to resource based on heuristic rules."
    return ClassificationResult(
        bucket=ParaBucket.RESOURCE,
        area_name=None,
        project_outcome=None,
        confidence=0.45,
        method="heuristic",
        reason=reason,
    )
