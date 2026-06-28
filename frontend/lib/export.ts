import type { MeetingDetail } from "./types";
import { formatTimestamp, formatDate } from "./api";

export function buildMarkdown(m: MeetingDetail): string {
  const lines: string[] = [];
  lines.push(`# ${m.title}`, "");
  lines.push(`**Date:** ${formatDate(m.date)}  `);
  lines.push(`**Participants:** ${m.participants.map((p) => p.name).join(", ") || "—"}`, "");

  if (m.summary?.overview) {
    lines.push("## Summary", "", m.summary.overview, "");
  }
  if (m.topics.length) {
    lines.push("## Key Topics", "");
    m.topics.forEach((t) => lines.push(`- [${formatTimestamp(t.start_ms)}] ${t.title}`));
    lines.push("");
  }
  if (m.action_items.length) {
    lines.push("## Action Items", "");
    m.action_items.forEach((a) =>
      lines.push(
        `- [${a.completed ? "x" : " "}] ${a.text} _(‎${a.assignee}${a.due_date ? ", " + a.due_date : ""})_`
      )
    );
    lines.push("");
  }
  if (m.segments.length) {
    lines.push("## Transcript", "");
    m.segments.forEach((s) =>
      lines.push(`**${s.speaker}** [${formatTimestamp(s.start_ms)}]: ${s.text}`, "")
    );
  }
  return lines.join("\n");
}

export function buildText(m: MeetingDetail): string {
  const lines: string[] = [];
  lines.push(m.title.toUpperCase());
  lines.push(formatDate(m.date));
  lines.push(`Participants: ${m.participants.map((p) => p.name).join(", ") || "-"}`);
  lines.push("");
  if (m.summary?.overview) lines.push("SUMMARY", m.summary.overview, "");
  if (m.action_items.length) {
    lines.push("ACTION ITEMS");
    m.action_items.forEach((a) =>
      lines.push(`  [${a.completed ? "x" : " "}] ${a.text} (${a.assignee}${a.due_date ? ", " + a.due_date : ""})`)
    );
    lines.push("");
  }
  if (m.segments.length) {
    lines.push("TRANSCRIPT");
    m.segments.forEach((s) => lines.push(`[${formatTimestamp(s.start_ms)}] ${s.speaker}: ${s.text}`));
  }
  return lines.join("\n");
}

export function download(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "meeting";
}
