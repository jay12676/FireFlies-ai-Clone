"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Segment } from "@/lib/types";
import { formatTimestamp } from "@/lib/api";
import { colorFor, initials } from "./Avatars";
import Highlight from "./Highlight";

export default function TranscriptPanel({
  segments,
  currentMs,
  onSeek,
}: {
  segments: Segment[];
  currentMs: number;
  onSeek: (ms: number) => void;
}) {
  const [query, setQuery] = useState("");
  const [matchIdx, setMatchIdx] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLDivElement>(null);

  // The currently-playing segment (last one whose start <= currentMs).
  const activeId = useMemo(() => {
    let id: number | null = null;
    for (const s of segments) {
      if (currentMs >= s.start_ms) id = s.id;
      else break;
    }
    return id;
  }, [segments, currentMs]);

  // Segment ids that match the in-transcript search.
  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return segments.filter((s) => s.text.toLowerCase().includes(q)).map((s) => s.id);
  }, [segments, query]);

  useEffect(() => setMatchIdx(0), [query]);

  // Auto-scroll the active (playing) line into view.
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }, [activeId]);

  const gotoMatch = (dir: 1 | -1) => {
    if (matches.length === 0) return;
    const next = (matchIdx + dir + matches.length) % matches.length;
    setMatchIdx(next);
    const el = document.getElementById(`seg-${matches[next]}`);
    el?.scrollIntoView({ block: "center", behavior: "smooth" });
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
            return (
              <div
                id={`seg-${s.id}`}
                key={s.id}
                ref={active ? activeRef : undefined}
                onClick={() => onSeek(s.start_ms)}
                className={`group mb-1 flex cursor-pointer gap-3 rounded-lg p-2.5 transition ${
                  active
                    ? "bg-brand-50 ring-1 ring-brand-200 dark:bg-brand-500/15 dark:ring-brand-700"
                    : isMatch
                    ? "bg-yellow-50 dark:bg-yellow-500/10"
                    : "hover:bg-gray-50 dark:hover:bg-gray-800/60"
                }`}
              >
                <div
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold text-white ${colorFor(
                    s.speaker
                  )}`}
                >
                  {initials(s.speaker)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-semibold">{s.speaker}</span>
                    <span className="text-xs tabular-nums text-brand-500 group-hover:underline">
                      {formatTimestamp(s.start_ms)}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                    <Highlight text={s.text} query={query} />
                  </p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
