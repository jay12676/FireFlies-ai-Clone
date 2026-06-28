"""Deterministic, rule-based generation of summary, action items, and topics.

No external LLM is used — everything is derived from the transcript text via
keyword-frequency ranking and cue-phrase matching, so output is reproducible and
works fully offline.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .parser import ParsedSegment

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "so", "to", "of", "in", "on",
    "at", "for", "with", "as", "by", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "i", "you", "we", "they", "he", "she",
    "me", "us", "them", "my", "our", "your", "their", "his", "her", "do", "does", "did",
    "have", "has", "had", "will", "would", "can", "could", "should", "shall", "may",
    "might", "must", "not", "no", "yes", "ok", "okay", "just", "really", "very", "about",
    "up", "out", "all", "some", "any", "what", "which", "who", "when", "where", "how",
    "there", "here", "now", "get", "got", "go", "going", "want", "like", "think", "know",
    "yeah", "um", "uh", "right", "well", "gonna", "let", "lets", "from", "into", "over",
}

_ACTION_CUES = [
    "will ", "i'll ", "we'll ", "need to", "needs to", "have to", "has to", "let's ",
    "lets ", "action item", "follow up", "follow-up", "to do", "todo", "make sure",
    "should ", "must ", "going to", "by tomorrow", "by friday", "by monday", "by end of",
    "send ", "schedule ", "set up", "set-up", "circle back", "take care of", "assign ",
]

_DATE_RE = re.compile(
    r"\b(by\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|"
    r"next week|end of (?:day|week|month|the week)|eod|eow|q[1-4]))\b",
    re.IGNORECASE,
)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class ActionItemDraft:
    text: str
    assignee: str = "Unassigned"
    due_date: str = ""


@dataclass
class TopicDraft:
    title: str
    start_ms: int


@dataclass
class GeneratedContent:
    overview: str
    action_items: list[ActionItemDraft] = field(default_factory=list)
    topics: list[TopicDraft] = field(default_factory=list)


def _keywords(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _STOPWORDS and len(w) > 2]


def _sentences(segments: list[ParsedSegment]) -> list[tuple[str, ParsedSegment]]:
    out: list[tuple[str, ParsedSegment]] = []
    for seg in segments:
        for sent in _SENT_SPLIT.split(seg.text.strip()):
            sent = sent.strip()
            if len(sent.split()) >= 4:
                out.append((sent, seg))
    return out


def generate_summary(segments: list[ParsedSegment], max_sentences: int = 5) -> str:
    """Rank sentences by keyword frequency and join the highest-scoring ones."""
    sentences = _sentences(segments)
    if not sentences:
        return ""
    freq = Counter(_keywords(" ".join(s.text for s in segments)))
    scored: list[tuple[float, int, str]] = []
    for idx, (sent, _seg) in enumerate(sentences):
        words = _keywords(sent)
        if not words:
            continue
        score = sum(freq[w] for w in words) / len(words)
        scored.append((score, idx, sent))
    scored.sort(key=lambda t: (-t[0], t[1]))
    chosen = sorted(scored[:max_sentences], key=lambda t: t[1])  # restore reading order
    return " ".join(sent for _s, _i, sent in chosen)


def extract_action_items(segments: list[ParsedSegment]) -> list[ActionItemDraft]:
    """Find sentences containing action cues; infer assignee + due date."""
    drafts: list[ActionItemDraft] = []
    seen: set[str] = set()
    for seg in segments:
        for sent in _SENT_SPLIT.split(seg.text.strip()):
            sent = sent.strip()
            low = sent.lower()
            if len(sent.split()) < 3:
                continue
            if not any(cue in low for cue in _ACTION_CUES):
                continue
            key = low[:60]
            if key in seen:
                continue
            seen.add(key)
            assignee = seg.speaker or "Unassigned"
            if low.startswith(("i'll", "i will", "let me")):
                assignee = seg.speaker
            date_match = _DATE_RE.search(sent)
            due = date_match.group(1) if date_match else ""
            drafts.append(ActionItemDraft(text=sent, assignee=assignee, due_date=due))
    return drafts[:12]


def extract_topics(segments: list[ParsedSegment], max_topics: int = 6) -> list[TopicDraft]:
    """Cluster the transcript by frequent keywords into ordered chapters."""
    if not segments:
        return []
    freq = Counter(_keywords(" ".join(s.text for s in segments)))
    # Candidate topics = most frequent meaningful keywords. Prefer repeated
    # keywords (freq >= 2); for short transcripts fall back to top singletons.
    candidates = [w for w, c in freq.most_common(40) if c >= 2]
    if len(candidates) < 3:
        candidates = [w for w, _c in freq.most_common(40)]
    topics: list[TopicDraft] = []
    used_ms: set[int] = set()
    for word in candidates:
        # First segment that mentions the keyword becomes the chapter anchor.
        for seg in segments:
            if word in seg.text.lower() and seg.start_ms not in used_ms:
                topics.append(TopicDraft(title=word.capitalize(), start_ms=seg.start_ms))
                used_ms.add(seg.start_ms)
                break
        if len(topics) >= max_topics:
            break
    topics.sort(key=lambda t: t.start_ms)
    return topics


def generate_all(segments: list[ParsedSegment]) -> GeneratedContent:
    return GeneratedContent(
        overview=generate_summary(segments),
        action_items=extract_action_items(segments),
        topics=extract_topics(segments),
    )
