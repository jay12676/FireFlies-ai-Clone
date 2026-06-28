"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { api, formatTimestamp } from "@/lib/api";
import type { SearchHit } from "@/lib/types";
import Highlight from "@/components/Highlight";

function SearchInner() {
  const params = useSearchParams();
  const router = useRouter();
  const initial = params.get("q") || "";
  const [q, setQ] = useState(initial);
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    const term = q.trim();
    if (!term) {
      setHits([]);
      setSearched(false);
      return;
    }
    setLoading(true);
    const t = setTimeout(() => {
      api
        .search(term)
        .then((r) => setHits(r.hits))
        .finally(() => {
          setLoading(false);
          setSearched(true);
        });
    }, 300);
    return () => clearTimeout(t);
  }, [q]);

  // Group hits by meeting.
  const grouped = useMemo(() => {
    const map = new Map<number, { title: string; hits: SearchHit[] }>();
    hits.forEach((h) => {
      if (!map.has(h.meeting_id)) map.set(h.meeting_id, { title: h.meeting_title, hits: [] });
      map.get(h.meeting_id)!.hits.push(h);
    });
    return Array.from(map.entries());
  }, [hits]);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.replace(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 md:px-8">
      <h1 className="mb-4 text-2xl font-bold">Search transcripts</h1>
      <form onSubmit={onSubmit} className="relative mb-6">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          🔍
        </span>
        <input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search across all meeting transcripts…"
          className="w-full rounded-lg border border-gray-200 bg-white py-3 pl-10 pr-3 outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-brand-900/40"
        />
      </form>

      {loading && <p className="text-sm text-gray-500">Searching…</p>}

      {!loading && searched && hits.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center text-gray-500 dark:border-gray-700">
          No matches for “{q}”.
        </div>
      )}

      {!loading && hits.length > 0 && (
        <>
          <p className="mb-3 text-sm text-gray-500">
            {hits.length} match{hits.length === 1 ? "" : "es"} in {grouped.length} meeting
            {grouped.length === 1 ? "" : "s"}
          </p>
          <div className="flex flex-col gap-5">
            {grouped.map(([mid, group]) => (
              <div
                key={mid}
                className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
              >
                <Link
                  href={`/meetings/${mid}`}
                  className="font-semibold hover:text-brand-600 dark:hover:text-brand-400"
                >
                  {group.title}
                </Link>
                <ul className="mt-2 flex flex-col gap-1.5">
                  {group.hits.slice(0, 5).map((h) => (
                    <li key={h.segment_id}>
                      <Link
                        href={`/meetings/${mid}`}
                        className="flex gap-2 rounded-lg p-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        <span className="shrink-0 font-medium text-brand-500">{h.speaker}</span>
                        <span className="shrink-0 tabular-nums text-xs text-gray-400">
                          {formatTimestamp(h.start_ms)}
                        </span>
                        <span className="text-gray-700 dark:text-gray-300">
                          <Highlight text={h.text} query={q} />
                        </span>
                      </Link>
                    </li>
                  ))}
                  {group.hits.length > 5 && (
                    <li className="px-2 text-xs text-gray-400">
                      +{group.hits.length - 5} more in this meeting
                    </li>
                  )}
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="p-8 text-sm text-gray-500">Loading…</div>}>
      <SearchInner />
    </Suspense>
  );
}
