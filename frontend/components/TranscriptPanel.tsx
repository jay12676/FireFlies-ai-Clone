"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Highlight, Segment } from "@/lib/types";
import { formatTimestamp } from "@/lib/api";
import { colorFor, initials } from "./Avatars";
import HighlightText from "./Highlight";

export default function TranscriptPanel({
  segments,
  currentMs,
  onSeek,
  highlights,
  onAddHighlight,
}: {
  segments: Segment[];
  currentMs: number;
  onSeek: (ms: number) => void;
  highlights: Highlight[];
  onAddHighlight: (seg: Segment, note: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [matchIdx, setMatchIdx] = useState(0);
  const [noteFor, setNoteFor] = useState<number | null>(null);
  const [noteText, setNoteText] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLDivElement>(null);

  const activeId = useMemo(() => {
    let id: number | null = null;
    for (const s of segments) {
      if (currentMs >= s.start_ms) id = s.id;
      else break;
    }
    return id;
  }, [segments, currentMs]);

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return segments.filter((s) => s.text.toLowerCase().includes(q)).map((s) => s.id);
  }, [segments, query]);

  // Map of segment_id -> notes (a segment can have multiple highlights/comments).
  const notesBySegment = useMemo(() => {
    const map = new Map<number, Highlight[]>();
    highlights.forEach((h) => {
      if (h.segment_id == null) return;
      if (!map.has(h.segment_id)) map.set(h.segment_id, []);
      map.get(h.segment_id)!.push(h);
    });
    return map;
  }, [highlights]);

  useEffect(() => setMatchIdx(0), [query]);

  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }, [activeId]);

  const gotoMatch = (dir: 1 | -1) => {
    if (matches.length === 0) return;
    const next = (matchIdx + dir + matches.length) % matches.length;
    setMatchIdx(next);
    document.getElementById(`seg-${matches[next]}`)?.scrollIntoView({ block: "center", behavior: "smooth" });
  };

  const openNote = (segId: number) => {
    setNoteFor(segId);
    setNoteText("");
  };

  const saveNote = (seg: Segment) => {
    onAddHighlight(seg, noteText.trim());
    setNoteFor(null);
    setNoteText("");
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center gap-2 border-b border-gray-200 p-3 dark:border-gray-800">
        <h2 className="mr-auto text-sm font-semibold">Transcript</h2>
        <div className="relative">
          <span className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-gray-400">
            🔍
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Find in transcript…"
            className="w-44 rounded-lg border border-gray-200 bg-gray-50 py-1.5 pl-7 pr-2 text-xs outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800"
          />
        </div>
        {query && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <span>{matches.length ? `${matchIdx + 1}/${matches.length}` : "0"}</span>
            <button onClick={() => gotoMatch(-1)} className="rounded px-1 hover:bg-gray-100 dark:hover:bg-gray-800">
              ↑
            </button>
            <button onClick={() => gotoMatch(1)} className="rounded px-1 hover:bg-gray-100 dark:hover:bg-gray-800">
              ↓
            </button>
          </div>
        )}
      </div>

      <div ref={containerRef} className="scrollbar-thin flex-1 overflow-y-auto p-2">
        {segments.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center py-16 text-center text-sm text-gray-500">
            <span className="text-3xl">📝</span>
            <p className="mt-2">No transcript yet.</p>
            <p>Upload one from the meeting menu to generate a summary.</p>
          </div>
        ) : (
          segments.map((s) => {
            const active = s.id === activeId;
            const isMatch = matches.includes(s.id);
            const segNotes = notesBySegment.get(s.id) || [];
            const highlighted = segNotes.length > 0;
            return (
              <div
                id={`seg-${s.id}`}
                key={s.id}
                ref={active ? activeRef : undefined}
                className={`group mb-1 rounded-lg p-2.5 transition ${
                  active
                    ? "bg-brand-50 ring-1 ring-brand-200 dark:bg-brand-500/15 dark:ring-brand-700"
                    : isMatch
                    ? "bg-yellow-50 dark:bg-yellow-500/10"
                    : "hover:bg-gray-50 dark:hover:bg-gray-800/60"
                } ${highlighted ? "border-l-2 border-yellow-400" : ""}`}
              >
                <div className="flex gap-3">
                  <div
                    className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold text-white ${colorFor(
                      s.speaker
                    )}`}
                  >
                    {initials(s.speaker)}
                  </div>
                  <div className="min-w-0 flex-1 cursor-pointer" onClick={() => onSeek(s.start_ms)}>
                    <div className="flex items-baseline gap-2">
                      <span className="text-sm font-semibold">{s.speaker}</span>
                      <span className="text-xs tabular-nums text-brand-500 group-hover:underline">
                        {formatTimestamp(s.start_ms)}
                      </span>
                    </div>
                    <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                      <HighlightText text={s.text} query={query} />
                    </p>
                  </div>
                  <button
                    onClick={() => openNote(s.id)}
                    title="Highlight & comment"
                    className="h-6 shrink-0 self-start rounded px-1 text-xs opacity-0 transition group-hover:opacity-100 hover:bg-gray-200 dark:hover:bg-gray-700"
                  >
                    💬
                  </button>
                </div>

                {/* Existing comments on this line */}
                {segNotes.map((h) => (
                  <div
                    key={h.id}
                    className="ml-10 mt-1.5 flex items-start gap-2 rounded-md bg-yellow-50 px-2 py-1 text-xs text-gray-600 dark:bg-yellow-500/10 dark:text-gray-300"
                  >
                    <span>💬</span>
                    <span>{h.note || "Highlighted"}</span>
                  </div>
                ))}

                {/* Inline note editor */}
                {noteFor === s.id && (
                  <div className="ml-10 mt-2 flex gap-2">
                    <input
                      autoFocus
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && saveNote(s)}
                      placeholder="Add a comment (optional) and save…"
                      className="flex-1 rounded border border-gray-200 px-2 py-1 text-xs dark:border-gray-700 dark:bg-gray-800"
                    />
                    <button onClick={() => saveNote(s)} className="rounded bg-brand-500 px-2 py-1 text-xs font-medium text-white">
                      Save
                    </button>
                    <button onClick={() => setNoteFor(null)} className="rounded px-2 py-1 text-xs text-gray-500">
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
