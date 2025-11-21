from __future__ import annotations

from dataclasses import dataclass
import re
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
    "ship",
    "launch",
}

TIME_SIGNALS = {
    "today",
    "tomorrow",
    "this weekend",
    "this week",
    "this month",
    "tonight",
    "by ",
    "due ",
    "next week",
    "next month",
    "next quarter",
    "next monday",
    "next tuesday",
    "next wednesday",
    "next thursday",
    "next friday",
    "next saturday",
    "next sunday",
}

TASK_MARKERS = {"todo", "to-do", "task", "deadline", "due", "finish", "complete", "deliver", "submit"}


def _detect_area(text_blob: str) -> str | None:
    for area, keywords in AREA_MAP.items():
        if any(keyword in text_blob for keyword in keywords):
            return area
    return None


DATE_PATTERN = re.compile(r"\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b")
TIME_PATTERN = re.compile(r"\b(\d{1,2}:\d{2}\s?(?:am|pm)?)\b")


def classify(content: str, title: str | None = None, tags: Iterable[str] | None = None) -> ClassificationResult:
    text = f"{title or ''}\n{content}".lower()
    tag_text = " ".join(tags or []).lower()
    text_blob = f"{text} {tag_text}"

    has_time_signal = any(signal in text_blob for signal in TIME_SIGNALS) or bool(DATE_PATTERN.search(text_blob))
    has_time_detail = has_time_signal or bool(TIME_PATTERN.search(text_blob))
    has_action_verb = any(verb in text_blob for verb in ACTION_VERBS)
    has_task_marker = any(marker in text_blob for marker in TASK_MARKERS)
    has_url = "http://" in text_blob or "https://" in text_blob or "www." in text_blob

    area_name = _detect_area(text_blob)

    is_project_like = has_action_verb and (has_time_detail or has_task_marker)

    if is_project_like:
        project_outcome = title or "Untitled project"
        reason = "Detected an actionable item with a finish line (time or task cues)."
        confidence = 0.7 if has_time_detail else 0.62
        return ClassificationResult(
            bucket=ParaBucket.PROJECT,
            area_name=area_name,
            project_outcome=project_outcome,
            confidence=confidence,
            method="heuristic",
            reason=reason,
        )

    if area_name:
        reason = (
            f"Matched area keywords for {area_name}; treating as a resource anchored to that area."
        )
        return ClassificationResult(
            bucket=ParaBucket.RESOURCE,
            area_name=area_name,
            project_outcome=None,
            confidence=0.64,
            method="heuristic",
            reason=reason,
        )

    if has_url:
        reason = "Detected a link; defaulting to a resource for reference material."
        return ClassificationResult(
            bucket=ParaBucket.RESOURCE,
            area_name=None,
            project_outcome=None,
            confidence=0.56,
            method="heuristic",
            reason=reason,
        )

    reason = "Defaulted to resource to keep captures non-urgent unless clear project cues exist."
    return ClassificationResult(
        bucket=ParaBucket.RESOURCE,
        area_name=None,
        project_outcome=None,
        confidence=0.5,
        method="heuristic",
        reason=reason,
    )
