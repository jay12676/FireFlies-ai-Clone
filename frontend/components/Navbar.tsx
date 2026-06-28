"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTheme } from "@/context/ThemeContext";

export default function Navbar() {
  const { theme, toggle } = useTheme();
  const router = useRouter();
  const [q, setQ] = useState("");

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) router.push(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-200 bg-white/80 px-4 backdrop-blur dark:border-gray-800 dark:bg-gray-900/80 md:px-6">
      <Link href="/" className="flex items-center gap-2 md:hidden">
        <span className="text-xl">🔥</span>
        <span className="font-bold">Fireflies</span>
      </Link>

      <form onSubmit={onSearch} className="relative ml-auto hidden w-full max-w-md sm:block">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          🔍
        </span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search all transcripts…"
          className="w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pl-9 pr-3 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-brand-900/40"
        />
      </form>

      <div className="ml-auto flex items-center gap-3 sm:ml-0">
        <button
          onClick={toggle}
          aria-label="Toggle dark mode"
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200 text-gray-600 transition hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>
        <button className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800">
          🔔
        </button>
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-500 text-sm font-semibold text-white">
            J
          </div>
          <div className="hidden text-sm leading-tight lg:block">
            <p className="font-medium">Jayant</p>
            <p className="text-xs text-gray-500">Free plan</p>
          </div>
        </div>
      </div>
    </header>
  );
}
