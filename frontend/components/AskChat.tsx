"use client";

import { useRef, useState } from "react";
import { api, formatTimestamp } from "@/lib/api";
import type { AskCitation } from "@/lib/types";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  citations?: AskCitation[];
}

const SUGGESTIONS = ["What were the action items?", "What was decided?", "Who is responsible for what?"];

export default function AskChat({
  meetingId,
  onSeek,
}: {
  meetingId: number;
  onSeek: (ms: number) => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "Ask me anything about this meeting — I'll answer from the transcript and cite the moments.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const send = async (question: string) => {
    const q = question.trim();
    if (!q || loading) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.ask(meetingId, q);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, citations: res.citations }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Something went wrong answering that." }]);
    } finally {
      setLoading(false);
      setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="scrollbar-thin flex-1 space-y-3 overflow-y-auto pb-2">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                m.role === "user"
                  ? "bg-brand-500 text-white"
                  : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
              }`}
            >
              <p className="leading-relaxed">{m.text}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {m.citations.map((c) => (
                    <button
                      key={c.segment_id}
                      onClick={() => onSeek(c.start_ms)}
                      className="rounded-full bg-white/70 px-2 py-0.5 text-xs font-medium text-brand-700 hover:bg-white dark:bg-gray-700 dark:text-brand-300"
                      title={c.text}
                    >
                      {c.speaker} · {formatTimestamp(c.start_ms)}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-xs text-gray-400">Thinking…</p>}
        <div ref={endRef} />
      </div>

      {messages.length <= 1 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-gray-200 px-2.5 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
          placeholder="Ask about this meeting…"
          className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800"
        />
        <button
          onClick={() => send(input)}
          disabled={loading}
          className="rounded-lg bg-brand-500 px-3 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-60"
        >
          Ask
        </button>
      </div>
    </div>
  );
}
