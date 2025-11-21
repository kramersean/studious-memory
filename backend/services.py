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
    "Cooking": {"recipe", "cook", "kitchen", "bake", "pancake", "dinner"},
    "Health": {"run", "workout", "gym", "sleep", "diet", "nutrition"},
    "Finance": {"budget", "invest", "salary", "raise", "401k", "tax"},
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
}

TIME_SIGNALS = {"today", "tomorrow", "this weekend", "by ", "due ", "next "}


def classify(content: str, title: str | None = None, tags: Iterable[str] | None = None) -> ClassificationResult:
    text = f"{title or ''}\n{content}".lower()
    tag_text = " ".join(tags or []).lower()
    text_blob = f"{text} {tag_text}"

    has_time_signal = any(signal in text_blob for signal in TIME_SIGNALS)
    has_action_verb = any(verb in text_blob for verb in ACTION_VERBS)

    if has_time_signal and has_action_verb:
        project_outcome = title or "Untitled project"
        reason = "Detected time and action cues indicative of a project."
        return ClassificationResult(
            bucket=ParaBucket.PROJECT,
            area_name=None,
            project_outcome=project_outcome,
            confidence=0.7,
            method="heuristic",
            reason=reason,
        )

    for area, keywords in AREA_MAP.items():
        if any(keyword in text_blob for keyword in keywords):
            reason = f"Matched area keywords for {area}."
            return ClassificationResult(
                bucket=ParaBucket.RESOURCE,
                area_name=area,
                project_outcome=None,
                confidence=0.6,
                method="heuristic",
                reason=reason,
            )

    reason = "Defaulted to resource based on heuristic rules."
    return ClassificationResult(
        bucket=ParaBucket.RESOURCE,
        area_name=None,
        project_outcome=None,
        confidence=0.4,
        method="heuristic",
        reason=reason,
    )
