"""Transcript parsing service.

Supports three input formats, dispatched by file extension (falling back to
content sniffing):

* ``.txt``  — ``Speaker: text`` lines, optionally prefixed with ``[mm:ss]`` or
  ``[hh:mm:ss]``. Missing timestamps are synthesized sequentially.
* ``.vtt``  — WebVTT cues (``HH:MM:SS.mmm --> HH:MM:SS.mmm``); speaker taken from
  ``<v Name>`` tags or a ``Name:`` prefix on the cue text.
* ``.json`` — an array of objects with ``speaker`` and either ``start_ms``/``end_ms``
  or ``start``/``end`` (seconds).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

# Average spoken segment length used when timestamps are absent.
_SYNTH_SEGMENT_MS = 4000


@dataclass
class ParsedSegment:
    speaker: str
    start_ms: int
    end_ms: int
    text: str


_TS_BRACKET = re.compile(r"^\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]\s*")
_SPEAKER_LINE = re.compile(r"^([A-Za-z0-9 ._'-]{1,40}?):\s+(.*)$")
_VTT_TIME = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[.,](\d{3})"
)
_VTT_VOICE = re.compile(r"<v\s+([^>]+)>(.*?)(?:</v>)?$", re.IGNORECASE)


def _to_ms(h: str, m: str, s: str, ms: str) -> int:
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def parse_transcript(content: str, filename: str = "transcript.txt") -> list[ParsedSegment]:
    """Parse raw transcript ``content`` into ordered segments."""
    name = (filename or "").lower()
    stripped = content.strip()
    if name.endswith(".json") or stripped.startswith("[") or stripped.startswith("{"):
        try:
            return _parse_json(stripped)
        except (ValueError, json.JSONDecodeError):
            pass  # fall through to text parsing
    if name.endswith(".vtt") or "-->" in content:
        return _parse_vtt(content)
    return _parse_txt(content)


def _parse_json(content: str) -> list[ParsedSegment]:
    data = json.loads(content)
    if isinstance(data, dict):
        data = data.get("segments", data.get("transcript", []))
    segments: list[ParsedSegment] = []
    for i, item in enumerate(data):
        if "start_ms" in item:
            start = int(item["start_ms"])
            end = int(item.get("end_ms", start + _SYNTH_SEGMENT_MS))
        else:
            start = int(float(item.get("start", i * _SYNTH_SEGMENT_MS / 1000)) * 1000)
            end = int(float(item.get("end", start / 1000 + 4)) * 1000)
        segments.append(
            ParsedSegment(
                speaker=str(item.get("speaker", "Speaker")).strip() or "Speaker",
                start_ms=start,
                end_ms=end,
                text=str(item.get("text", "")).strip(),
            )
        )
    return [s for s in segments if s.text]


def _parse_vtt(content: str) -> list[ParsedSegment]:
    segments: list[ParsedSegment] = []
    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines or lines[0].strip().upper() == "WEBVTT":
            lines = [ln for ln in lines if ln.strip().upper() != "WEBVTT"]
        time_idx = next((i for i, ln in enumerate(lines) if _VTT_TIME.search(ln)), None)
        if time_idx is None:
            continue
        m = _VTT_TIME.search(lines[time_idx])
        start = _to_ms(m.group(1), m.group(2), m.group(3), m.group(4))
        end = _to_ms(m.group(5), m.group(6), m.group(7), m.group(8))
        text_lines = lines[time_idx + 1 :]
        speaker = "Speaker"
        cleaned: list[str] = []
        for tl in text_lines:
            voice = _VTT_VOICE.search(tl.strip())
            if voice:
                speaker = voice.group(1).strip()
                cleaned.append(voice.group(2).strip())
            else:
                sp = _SPEAKER_LINE.match(tl.strip())
                if sp and len(cleaned) == 0:
                    speaker = sp.group(1).strip()
                    cleaned.append(sp.group(2).strip())
                else:
                    cleaned.append(re.sub(r"<[^>]+>", "", tl).strip())
        text = " ".join(c for c in cleaned if c)
        if text:
            segments.append(ParsedSegment(speaker=speaker, start_ms=start, end_ms=end, text=text))
    return segments


def _parse_txt(content: str) -> list[ParsedSegment]:
    segments: list[ParsedSegment] = []
    cursor = 0
    last_speaker = "Speaker"
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        explicit_start: int | None = None
        ts = _TS_BRACKET.match(line)
        if ts:
            h = ts.group(3)
            if h is not None:  # [h:mm:ss]
                explicit_start = _to_ms(ts.group(1), ts.group(2), ts.group(3), "0")
            else:  # [mm:ss]
                explicit_start = _to_ms("0", ts.group(1), ts.group(2), "0")
            line = line[ts.end():]
        sp = _SPEAKER_LINE.match(line)
        if sp:
            last_speaker = sp.group(1).strip()
            text = sp.group(2).strip()
        else:
            text = line
        if not text:
            continue
        start = explicit_start if explicit_start is not None else cursor
        end = start + _SYNTH_SEGMENT_MS
        segments.append(
            ParsedSegment(speaker=last_speaker, start_ms=start, end_ms=end, text=text)
        )
        cursor = end
    return segments
