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

export async function downloadPdf(m: MeetingDetail) {
  // jsPDF is loaded lazily so it never bloats the initial bundle.
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const margin = 48;
  const width = doc.internal.pageSize.getWidth() - margin * 2;
  const bottom = doc.internal.pageSize.getHeight() - margin;
  let y = margin;

  const writeLine = (text: string, size: number, bold = false, gap = 6) => {
    doc.setFont("helvetica", bold ? "bold" : "normal");
    doc.setFontSize(size);
    const lines = doc.splitTextToSize(text, width) as string[];
    for (const line of lines) {
      if (y > bottom) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += size + gap;
    }
  };

  writeLine(m.title, 18, true, 10);
  writeLine(`${formatDate(m.date)}  ·  ${m.participants.map((p) => p.name).join(", ") || "—"}`, 10, false, 14);

  if (m.summary?.overview) {
    writeLine("Summary", 13, true);
    writeLine(m.summary.overview, 11, false, 12);
  }
  if (m.action_items.length) {
    writeLine("Action Items", 13, true);
    m.action_items.forEach((a) =>
      writeLine(`${a.completed ? "[x]" : "[ ]"} ${a.text} (${a.assignee}${a.due_date ? ", " + a.due_date : ""})`, 11)
    );
    y += 6;
  }
  if (m.segments.length) {
    writeLine("Transcript", 13, true);
    m.segments.forEach((s) => writeLine(`[${formatTimestamp(s.start_ms)}] ${s.speaker}: ${s.text}`, 10, false, 5));
  }

  doc.save(`${slugify(m.title)}.pdf`);
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
