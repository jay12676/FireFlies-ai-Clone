"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  soon?: boolean;
}

const MAIN: NavItem[] = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/search", label: "Search", icon: "🔍" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

const SOON: NavItem[] = [
  { href: "#", label: "Live Bot", icon: "🤖", soon: true },
  { href: "#", label: "Integrations", icon: "🔌", soon: true },
  { href: "#", label: "Team", icon: "👥", soon: true },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-gray-200 bg-white px-3 py-5 dark:border-gray-800 dark:bg-gray-900 md:flex">
      <Link href="/" className="mb-6 flex items-center gap-2 px-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500 text-lg">
          🔥
        </span>
        <span className="text-lg font-bold tracking-tight">Fireflies</span>
      </Link>

      <nav className="flex flex-col gap-1">
        {MAIN.map((item) => {
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                active
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300"
                  : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-8 px-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
        Coming soon
      </div>
      <nav className="mt-2 flex flex-col gap-1">
        {SOON.map((item) => (
          <div
            key={item.label}
            className="flex cursor-not-allowed items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-gray-400 dark:text-gray-600"
            title="Coming soon"
          >
            <span className="flex items-center gap-3">
              <span>{item.icon}</span>
              {item.label}
            </span>
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] dark:bg-gray-800">
              Soon
            </span>
          </div>
        ))}
      </nav>

      <div className="mt-auto rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 p-4 text-white">
        <p className="text-sm font-semibold">Free Workspace</p>
        <p className="mt-1 text-xs text-white/80">Unlimited meetings &amp; transcripts.</p>
      </div>
    </aside>
  );
}
