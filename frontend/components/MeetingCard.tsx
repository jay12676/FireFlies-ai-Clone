import Link from "next/link";
import type { MeetingRow } from "@/lib/types";
import { formatDate, formatDuration } from "@/lib/api";
import Avatars from "./Avatars";

export default function MeetingCard({ meeting }: { meeting: MeetingRow }) {
  return (
    <Link
      href={`/meetings/${meeting.id}`}
      className="group flex flex-col gap-3 rounded-xl border border-gray-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:hover:border-brand-700"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="line-clamp-2 font-semibold leading-snug group-hover:text-brand-600 dark:group-hover:text-brand-400">
          {meeting.title}
        </h3>
        <span className="shrink-0 rounded-md bg-brand-50 px-2 py-1 text-xs font-medium text-brand-600 dark:bg-brand-500/15 dark:text-brand-300">
          {formatDuration(meeting.duration_seconds)}
        </span>
      </div>

      <p className="text-sm text-gray-500">{formatDate(meeting.date)}</p>

      {meeting.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {meeting.tags.map((t) => (
            <span
              key={t.id}
              className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-300"
            >
              #{t.name}
            </span>
          ))}
        </div>
      )}

      <div className="mt-auto flex items-center justify-between pt-2">
        <Avatars participants={meeting.participants} />
        <span className="flex items-center gap-1 text-xs text-gray-500">
          ✅ {meeting.action_item_count} action{meeting.action_item_count === 1 ? "" : "s"}
        </span>
      </div>
    </Link>
  );
}
