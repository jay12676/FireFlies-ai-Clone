"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { ActionItem, MeetingDetail } from "@/lib/types";
import { api, formatDate, formatDuration } from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import MediaPlayer from "@/components/MediaPlayer";
import TranscriptPanel from "@/components/TranscriptPanel";
import MeetingTabs from "@/components/MeetingTabs";
import ExportMenu from "@/components/ExportMenu";
import EditMeetingModal from "@/components/EditMeetingModal";
import Avatars from "@/components/Avatars";

export default function MeetingDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const router = useRouter();
  const { notify } = useToast();

  const [meeting, setMeeting] = useState<MeetingDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const audioRef = useRef<HTMLAudioElement>(null);
  const [currentMs, setCurrentMs] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .getMeeting(id)
      .then((m) => {
        setMeeting(m);
        setDurationMs(m.duration_seconds * 1000);
      })
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, [id]);

  const seekTo = useCallback((ms: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = ms / 1000;
    setCurrentMs(ms);
    audio.play().then(() => setPlaying(true)).catch(() => {});
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play().then(() => setPlaying(true)).catch(() => {});
    }
  };

  const onDelete = async () => {
    if (!confirm("Delete this meeting? This cannot be undone.")) return;
    await api.deleteMeeting(id);
    notify("Meeting deleted");
    router.push("/");
    router.refresh();
  };

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const content = await file.text();
      const updated = await api.uploadTranscript(id, content, file.name);
      setMeeting(updated);
      setDurationMs(updated.duration_seconds * 1000);
      notify("Transcript uploaded & summary generated");
    } catch {
      notify("Upload failed", "error");
    }
  };

  const setActionItems = (items: ActionItem[]) =>
    setMeeting((m) => (m ? { ...m, action_items: items } : m));

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 md:px-8">
        <div className="h-24 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-900" />
      </div>
    );
  }
  if (error || !meeting) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="text-lg font-medium">Meeting not found</p>
        <Link href="/" className="mt-3 inline-block text-brand-600 hover:underline">
          ← Back to meetings
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-full max-w-7xl flex-col px-4 py-5 md:px-8">
      {/* Header */}
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <Link href="/" className="text-sm text-gray-500 hover:text-brand-600">
            ← All meetings
          </Link>
          <h1 className="mt-1 text-xl font-bold md:text-2xl">{meeting.title}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-500">
            <span>{formatDate(meeting.date)}</span>
            <span>· {formatDuration(meeting.duration_seconds)}</span>
            <Avatars participants={meeting.participants} />
            {meeting.tags.map((t) => (
              <span key={t.id} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">
                #{t.name}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input ref={fileRef} type="file" accept=".txt,.vtt,.json" className="hidden" onChange={onUpload} />
          <button
            onClick={() => fileRef.current?.click()}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800"
          >
            ⬆ Transcript
          </button>
          <ExportMenu meeting={meeting} />
          <button
            onClick={() => setEditOpen(true)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-800"
          >
            ✏️ Edit
          </button>
          <button
            onClick={onDelete}
            className="rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 dark:border-red-900/50 dark:hover:bg-red-900/20"
          >
            🗑 Delete
          </button>
        </div>
      </div>

      {/* Player */}
      <div className="mb-4">
        <audio
          ref={audioRef}
          src={meeting.audio_url}
          onTimeUpdate={(e) => setCurrentMs(e.currentTarget.currentTime * 1000)}
          onLoadedMetadata={(e) => {
            const d = e.currentTarget.duration;
            if (isFinite(d) && d > 0) setDurationMs(d * 1000);
          }}
          onEnded={() => setPlaying(false)}
          preload="metadata"
        />
        <MediaPlayer
          title={meeting.title}
          currentMs={currentMs}
          durationMs={durationMs}
          playing={playing}
          onTogglePlay={togglePlay}
          onScrub={seekTo}
        />
      </div>

      {/* Two-panel body */}
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="min-h-[400px] lg:h-[calc(100vh-330px)]">
          <TranscriptPanel segments={meeting.segments} currentMs={currentMs} onSeek={seekTo} />
        </div>
        <div className="min-h-[400px] lg:h-[calc(100vh-330px)]">
          <MeetingTabs meeting={meeting} onSeek={seekTo} onActionItemsChange={setActionItems} />
        </div>
      </div>

      <EditMeetingModal
        meeting={meeting}
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSaved={setMeeting}
      />
    </div>
  );
}
