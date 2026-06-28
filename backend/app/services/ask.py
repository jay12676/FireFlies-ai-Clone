"""Rule-based "ask a question about this meeting" retrieval.

No LLM is used. The question is classified into a coarse intent (action items,
decisions, who-did-what, or general) and answered from the most relevant data:

* **action-item** questions → the meeting's extracted action items.
* **general** questions → transcript segments scored by keyword overlap (with
  light stemming so "payments" matches "payment"), composed into a short answer
  with citations back to each segment's timestamp.

To upgrade to a real LLM later, send the retrieved segments + action items as
context to a model in ``answer_question``; the retrieval step stays identical.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .generator import _keywords


@dataclass
class Citation:
    segment_id: int
    speaker: str
    start_ms: int
    text: str


@dataclass
class Answer:
    answer: str
    citations: list[Citation] = field(default_factory=list)


_ACTION_INTENT = {"action", "actions", "todo", "todos", "task", "tasks", "next", "step",
                  "steps", "assign", "assigned", "responsible", "owner", "deadline", "due"}
_DECISION_INTENT = {"decide", "decided", "decision", "agree", "agreed", "conclusion", "outcome"}
_SUMMARY_INTENT = {"summary", "summarize", "overall", "recap", "gist", "tldr", "happened"}
_WHO_INTENT = {"who"}


def _stem(word: str) -> str:
    """Very light stemmer: drop a trailing plural 's' for better recall."""
    return word[:-1] if len(word) > 4 and word.endswith("s") else word


def _stems(text: str) -> set[str]:
    return {_stem(w) for w in _keywords(text)}


def _segment_id(seg) -> int:
    return getattr(seg, "id", 0) or 0


def answer_question(
    segments: list,
    question: str,
    summary: str = "",
    action_items: list | None = None,
) -> Answer:
    q_words = _stems(question)
    if not q_words:
        return Answer("Please ask a more specific question about this meeting.")

    action_items = action_items or []

    # --- Intent: action items / next steps ---
    if q_words & _ACTION_INTENT and action_items:
        lines = []
        for a in action_items:
            who = getattr(a, "assignee", "") or "Unassigned"
            due = getattr(a, "due_date", "") or ""
            lines.append(f"• {a.text} ({who}{', ' + due if due else ''})")
        return Answer("Here are the action items from this meeting:\n" + "\n".join(lines))

    # --- Intent: decisions / outcomes (no literal match needed) ---
    if q_words & _DECISION_INTENT and summary:
        return Answer(f"Here's what came out of the meeting: {summary}")

    # --- Intent: overall summary / recap ---
    if q_words & _SUMMARY_INTENT and summary:
        return Answer(summary)

    # --- General: keyword retrieval over transcript segments ---
    scored: list[tuple[float, object]] = []
    for seg in segments:
        words = _stems(seg.text)
        if not words:
            continue
        overlap = len(words & q_words)
        if overlap == 0:
            continue
        score = overlap + overlap / len(words)
        scored.append((score, seg))

    scored.sort(key=lambda t: -t[0])
    top = [seg for _s, seg in scored[:3]]

    if not top:
        if summary:
            return Answer(
                "I couldn't find a direct mention of that, but here's the overall "
                f"summary: {summary}"
            )
        return Answer("I couldn't find anything about that in the transcript.")

    citations = [
        Citation(_segment_id(s), s.speaker, s.start_ms, s.text) for s in top
    ]

    lead = "Based on the transcript:"
    if q_words & _WHO_INTENT:
        speakers = ", ".join(dict.fromkeys(c.speaker for c in citations))
        lead = f"This involved {speakers}. Relevant moments:"

    body = " ".join(f"“{c.text}” — {c.speaker}." for c in citations)
    return Answer(f"{lead} {body}", citations)
