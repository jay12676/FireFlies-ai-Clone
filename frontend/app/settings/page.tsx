"use client";

import { useTheme } from "@/context/ThemeContext";

function ComingSoon({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center gap-4">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-xl dark:bg-gray-800">
          {icon}
        </span>
        <div>
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-500">{desc}</p>
        </div>
      </div>
      <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 dark:bg-amber-500/10 dark:text-amber-300">
        Coming soon
      </span>
    </div>
  );
}

export default function SettingsPage() {
  const { theme, toggle } = useTheme();

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 md:px-8">
      <h1 className="mb-1 text-2xl font-bold">Settings</h1>
      <p className="mb-6 text-sm text-gray-500">Manage your workspace preferences.</p>

      {/* Profile */}
      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">Profile</h2>
        <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-500 text-lg font-semibold text-white">
              J
            </div>
            <div>
              <p className="font-medium">Jayant</p>
              <p className="text-sm text-gray-500">kotharijayant73@gmail.com</p>
              <span className="mt-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">
                Free plan · default user
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Appearance */}
      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          Appearance
        </h2>
        <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <div>
            <p className="font-medium">Dark mode</p>
            <p className="text-sm text-gray-500">Toggle between light and dark themes.</p>
          </div>
          <button
            onClick={toggle}
            className={`relative h-6 w-11 rounded-full transition ${
              theme === "dark" ? "bg-brand-500" : "bg-gray-300"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${
                theme === "dark" ? "left-[22px]" : "left-0.5"
              }`}
            />
          </button>
        </div>
      </section>

      {/* Integrations / placeholders */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
          Integrations &amp; more
        </h2>
        <div className="flex flex-col gap-3">
          <ComingSoon icon="🤖" title="Meeting Bot" desc="Auto-join Zoom, Meet & Teams calls." />
          <ComingSoon icon="📅" title="Calendar Sync" desc="Connect Google or Outlook calendar." />
          <ComingSoon icon="🔌" title="CRM Integrations" desc="Push notes to Salesforce & HubSpot." />
          <ComingSoon icon="👥" title="Team & Sharing" desc="Invite teammates and share meetings." />
          <ComingSoon icon="🎙️" title="Live Transcription" desc="Real-time speech-to-text." />
        </div>
      </section>
    </div>
  );
}
