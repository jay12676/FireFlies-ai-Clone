"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { MeetingRow } from "@/lib/types";
import MeetingCard from "@/components/MeetingCard";
import NewMeetingModal from "@/components/NewMeetingModal";

export default function DashboardPage() {
  const [meetings, setMeetings] = useState<MeetingRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [participant, setParticipant] = useState("");
  const [tag, setTag] = useState("");
  const [sort, setSort] = useState("recent");
  const [modalOpen, setModalOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await api.listMeetings({ search, participant, tag, sort });
      setMeetings(rows);
    } finally {
      setLoading(false);
    }
  }, [search, participant, tag, sort]);

  useEffect(() => {
    const t = setTimeout(load, 250); // debounce filter changes
    return () => clearTimeout(t);
  }, [load]);

  // Unique participants & tags for filter dropdowns (derived from all rows once loaded).
  const [allRows, setAllRows] = useState<MeetingRow[]>([]);
  useEffect(() => {
    api.listMeetings().then(setAllRows);
  }, [modalOpen]);

  const participantOptions = useMemo(() => {
    const set = new Set<string>();
    allRows.forEach((m) => m.participants.forEach((p) => set.add(p.name)));
    return Array.from(set).sort();
  }, [allRows]);

  const tagOptions = useMemo(() => {
    const set = new Set<string>();
    allRows.forEach((m) => m.tags.forEach((t) => set.add(t.name)));
    return Array.from(set).sort();
  }, [allRows]);

  const select =
    "rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800";

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 md:px-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">My Meetings</h1>
          <p className="text-sm text-gray-500">
            {loading ? "Loading…" : `${meetings.length} meeting${meetings.length === 1 ? "" : "s"}`}
          </p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        >
          + New meeting
        </button>
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="relative min-w-[200px] flex-1">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            🔍
          </span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search meetings by title…"
            className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800"
          />
        </div>
        <select className={select} value={participant} onChange={(e) => setParticipant(e.target.value)}>
          <option value="">All participants</option>
          {participantOptions.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select className={select} value={tag} onChange={(e) => setTag(e.target.value)}>
          <option value="">All tags</option>
          {tagOptions.map((t) => (
            <option key={t} value={t}>
              #{t}
            </option>
          ))}
        </select>
        <select className={select} value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="recent">Most recent</option>
          <option value="oldest">Oldest first</option>
          <option value="title">Title A–Z</option>
        </select>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-44 animate-pulse rounded-xl border border-gray-200 bg-gray-100 dark:border-gray-800 dark:bg-gray-900"
            />
          ))}
        </div>
      ) : meetings.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 py-20 text-center dark:border-gray-700">
          <span className="text-4xl">📭</span>
          <p className="mt-3 font-medium">No meetings found</p>
          <p className="text-sm text-gray-500">Try adjusting filters or create a new meeting.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {meetings.map((m) => (
            <MeetingCard key={m.id} meeting={m} />
          ))}
        </div>
      )}

      <NewMeetingModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
