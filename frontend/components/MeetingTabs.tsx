"use client";

import { useState } from "react";
import type { ActionItem, MeetingDetail } from "@/lib/types";
import { formatTimestamp } from "@/lib/api";
import ActionItems from "./ActionItems";

type Tab = "summary" | "topics" | "actions";

export default function MeetingTabs({
  meeting,
  onSeek,
  onActionItemsChange,
}: {
  meeting: MeetingDetail;
  onSeek: (ms: number) => void;
  onActionItemsChange: (items: ActionItem[]) => void;
}) {
  const [tab, setTab] = useState<Tab>("summary");

  const tabs: { key: Tab; label: string; badge?: number }[] = [
    { key: "summary", label: "Summary" },
    { key: "topics", label: "Topics", badge: meeting.topics.length },
    { key: "actions", label: "Action Items", badge: meeting.action_items.length },
  ];

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div className="flex border-b border-gray-200 dark:border-gray-800">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium transition ${
              tab === t.key
                ? "border-b-2 border-brand-500 text-brand-600 dark:text-brand-400"
                : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
            }`}
          >
            {t.label}
            {t.badge != null && t.badge > 0 && (
              <span className="rounded-full bg-gray-100 px-1.5 text-xs dark:bg-gray-800">
                {t.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="scrollbar-thin flex-1 overflow-y-auto p-4">
        {tab === "summary" && (
          <div>
            {meeting.summary?.overview ? (
              <>
                <div className="mb-3 flex items-center gap-2">
                  <span className="rounded-md bg-brand-50 px-2 py-1 text-xs font-medium text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
                    ✨ AI Summary
                  </span>
                  <span className="text-xs text-gray-400">
                    {meeting.summary.generated_by === "seed" ? "Curated" : "Auto-generated"}
                  </span>
                </div>
                <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                  {meeting.summary.overview}
                </p>
              </>
            ) : (
              <p className="text-sm text-gray-500">No summary available yet.</p>
            )}
          </div>
        )}

        {tab === "topics" && (
          <ul className="flex flex-col gap-1">
            {meeting.topics.length === 0 && (
              <li className="text-sm text-gray-500">No topics extracted.</li>
            )}
            {meeting.topics.map((t, i) => (
              <li key={t.id}>
                <button
                  onClick={() => onSeek(t.start_ms)}
                  className="flex w-full items-center gap-3 rounded-lg p-2 text-left transition hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
                    {i + 1}
                  </span>
                  <span className="flex-1 text-sm font-medium">{t.title}</span>
                  <span className="text-xs tabular-nums text-brand-500">
                    {formatTimestamp(t.start_ms)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {tab === "actions" && (
          <ActionItems
            meetingId={meeting.id}
            items={meeting.action_items}
            onChange={onActionItemsChange}
          />
        )}
      </div>
    </div>
  );
}
