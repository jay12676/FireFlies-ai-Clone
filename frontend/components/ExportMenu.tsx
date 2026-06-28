"use client";

import { useEffect, useRef, useState } from "react";
import type { MeetingDetail } from "@/lib/types";
import { buildMarkdown, buildText, download, slugify } from "@/lib/export";
import { useToast } from "@/context/ToastContext";

export default function ExportMenu({ meeting }: { meeting: MeetingDetail }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const { notify } = useToast();

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const slug = slugify(meeting.title);
  const doExport = (kind: "md" | "txt") => {
    if (kind === "md") {
      download(`${slug}.md`, buildMarkdown(meeting), "text/markdown");
    } else {
      download(`${slug}.txt`, buildText(meeting), "text/plain");
    }
    notify(`Exported ${kind.toUpperCase()}`);
    setOpen(false);
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800"
      >
        ⬇ Export
      </button>
      {open && (
        <div className="absolute right-0 z-20 mt-1 w-44 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          <button
            onClick={() => doExport("md")}
            className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Markdown (.md)
          </button>
          <button
            onClick={() => doExport("txt")}
            className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Plain text (.txt)
          </button>
        </div>
      )}
    </div>
  );
}
