"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Modal from "./Modal";
import { api } from "@/lib/api";
import { useToast } from "@/context/ToastContext";

const SAMPLE = `[00:00] Alex: Welcome to the kickoff meeting for the mobile app project.
[00:06] Jamie: Thanks. I will prepare the wireframes by Friday.
[00:12] Alex: Great. We need to finalize the tech stack this week.
[00:18] Jamie: Let's schedule a follow up to review the API design.`;

export default function NewMeetingModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const { notify } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);

  const [title, setTitle] = useState("");
  const [participants, setParticipants] = useState("");
  const [tags, setTags] = useState("");
  const [transcript, setTranscript] = useState("");
  const [filename, setFilename] = useState("transcript.txt");
  const [submitting, setSubmitting] = useState(false);

  const reset = () => {
    setTitle("");
    setParticipants("");
    setTags("");
    setTranscript("");
    setFilename("transcript.txt");
  };

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFilename(file.name);
    setTranscript(await file.text());
  };

  const submit = async () => {
    if (!title.trim()) {
      notify("Please enter a title", "error");
      return;
    }
    setSubmitting(true);
    try {
      const meeting = await api.createMeeting({
        title: title.trim(),
        participants: participants
          .split(",")
          .map((p) => p.trim())
          .filter(Boolean)
          .map((name) => ({ name })),
        tags: tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        transcript_text: transcript.trim() || null,
        transcript_filename: filename,
      });
      notify("Meeting created");
      reset();
      onClose();
      router.push(`/meetings/${meeting.id}`);
      router.refresh();
    } catch (err) {
      notify((err as Error).message || "Failed to create meeting", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const field =
    "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-brand-900/40";
  const label = "mb-1 block text-sm font-medium";

  return (
    <Modal open={open} onClose={onClose} title="New meeting" maxWidth="max-w-xl">
      <div className="flex flex-col gap-4">
        <div>
          <label className={label}>Title *</label>
          <input
            className={field}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Q3 Roadmap Planning"
          />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={label}>Participants (comma-separated)</label>
            <input
              className={field}
              value={participants}
              onChange={(e) => setParticipants(e.target.value)}
              placeholder="Alex, Jamie"
            />
          </div>
          <div>
            <label className={label}>Tags (comma-separated)</label>
            <input
              className={field}
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="planning, product"
            />
          </div>
        </div>

        <div>
          <div className="mb-1 flex items-center justify-between">
            <label className={label + " mb-0"}>Transcript (paste or upload)</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setTranscript(SAMPLE)}
                className="text-xs font-medium text-brand-600 hover:underline"
              >
                Insert sample
              </button>
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="text-xs font-medium text-brand-600 hover:underline"
              >
                Upload .txt/.vtt/.json
              </button>
            </div>
          </div>
          <input
            ref={fileRef}
            type="file"
            accept=".txt,.vtt,.json"
            className="hidden"
            onChange={onFile}
          />
          <textarea
            className={field + " h-40 resize-y font-mono text-xs"}
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder={"[00:00] Speaker: Hello everyone…\nOr leave empty to add a transcript later."}
          />
          <p className="mt-1 text-xs text-gray-400">
            Summary, topics, and action items are generated automatically from the transcript.
          </p>
        </div>

        <div className="flex justify-end gap-2 pt-1">
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={submitting}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
          >
            {submitting ? "Creating…" : "Create meeting"}
          </button>
        </div>
      </div>
    </Modal>
  );
}
