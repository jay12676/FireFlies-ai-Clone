"use client";

import { useState } from "react";
import Modal from "./Modal";
import type { MeetingDetail } from "@/lib/types";
import { api } from "@/lib/api";
import { useToast } from "@/context/ToastContext";

export default function EditMeetingModal({
  meeting,
  open,
  onClose,
  onSaved,
}: {
  meeting: MeetingDetail;
  open: boolean;
  onClose: () => void;
  onSaved: (m: MeetingDetail) => void;
}) {
  const { notify } = useToast();
  const [title, setTitle] = useState(meeting.title);
  const [description, setDescription] = useState(meeting.description);
  const [participants, setParticipants] = useState(
    meeting.participants.map((p) => p.name).join(", ")
  );
  const [tags, setTags] = useState(meeting.tags.map((t) => t.name).join(", "));
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await api.updateMeeting(meeting.id, {
        title: title.trim(),
        description,
        participants: participants
          .split(",")
          .map((p) => p.trim())
          .filter(Boolean)
          .map((name) => ({ name })),
        tags: tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      });
      onSaved(updated);
      notify("Meeting updated");
      onClose();
    } catch (err) {
      notify((err as Error).message || "Update failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const field =
    "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800";
  const label = "mb-1 block text-sm font-medium";

  return (
    <Modal open={open} onClose={onClose} title="Edit meeting">
      <div className="flex flex-col gap-4">
        <div>
          <label className={label}>Title</label>
          <input className={field} value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div>
          <label className={label}>Description</label>
          <textarea
            className={field + " h-20 resize-y"}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <label className={label}>Participants (comma-separated)</label>
          <input
            className={field}
            value={participants}
            onChange={(e) => setParticipants(e.target.value)}
          />
        </div>
        <div>
          <label className={label}>Tags (comma-separated)</label>
          <input className={field} value={tags} onChange={(e) => setTags(e.target.value)} />
        </div>
        <div className="flex justify-end gap-2 pt-1">
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
          >
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>
    </Modal>
  );
}
