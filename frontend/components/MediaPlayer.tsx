"use client";

import { formatTimestamp } from "@/lib/api";

export default function MediaPlayer({
  title,
  currentMs,
  durationMs,
  playing,
  onTogglePlay,
  onScrub,
}: {
  title: string;
  currentMs: number;
  durationMs: number;
  playing: boolean;
  onTogglePlay: () => void;
  onScrub: (ms: number) => void;
}) {
  const pct = durationMs > 0 ? Math.min(100, (currentMs / durationMs) * 100) : 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center gap-4">
        <button
          onClick={onTogglePlay}
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-500 text-xl text-white transition hover:bg-brand-600"
          aria-label={playing ? "Pause" : "Play"}
        >
          {playing ? "⏸" : "▶"}
        </button>

        <div className="min-w-0 flex-1">
          <p className="mb-2 truncate text-sm font-medium">{title}</p>
          <div className="flex items-center gap-3">
            <span className="w-12 text-right text-xs tabular-nums text-gray-500">
              {formatTimestamp(currentMs)}
            </span>
            <input
              type="range"
              min={0}
              max={durationMs || 0}
              value={currentMs}
              onChange={(e) => onScrub(Number(e.target.value))}
              className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-gray-200 accent-brand-500 dark:bg-gray-700"
              style={{
                background: `linear-gradient(to right, #6c5ce7 ${pct}%, transparent ${pct}%)`,
              }}
            />
            <span className="w-12 text-xs tabular-nums text-gray-500">
              {formatTimestamp(durationMs)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
