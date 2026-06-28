import type { Participant } from "@/lib/types";

const COLORS = [
  "bg-rose-500",
  "bg-amber-500",
  "bg-emerald-500",
  "bg-sky-500",
  "bg-violet-500",
  "bg-pink-500",
];

export function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function colorFor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return COLORS[Math.abs(hash) % COLORS.length];
}

export default function Avatars({
  participants,
  max = 4,
}: {
  participants: Participant[];
  max?: number;
}) {
  const shown = participants.slice(0, max);
  const extra = participants.length - shown.length;
  return (
    <div className="flex -space-x-2">
      {shown.map((p, i) => (
        <div
          key={i}
          title={p.name}
          className={`flex h-7 w-7 items-center justify-center rounded-full border-2 border-white text-[10px] font-semibold text-white dark:border-gray-900 ${colorFor(
            p.name
          )}`}
        >
          {initials(p.name)}
        </div>
      ))}
      {extra > 0 && (
        <div className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-gray-300 text-[10px] font-semibold text-gray-700 dark:border-gray-900 dark:bg-gray-700 dark:text-gray-200">
          +{extra}
        </div>
      )}
    </div>
  );
}
