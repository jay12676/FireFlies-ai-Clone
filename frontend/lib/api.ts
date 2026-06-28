import type {
  ActionItem,
  AskResponse,
  Highlight,
  MeetingCreatePayload,
  MeetingDetail,
  MeetingRow,
  MeetingUpdatePayload,
  SearchResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export interface MeetingFilters {
  search?: string;
  participant?: string;
  tag?: string;
  sort?: string;
}

export const api = {
  listMeetings(filters: MeetingFilters = {}): Promise<MeetingRow[]> {
    const params = new URLSearchParams();
    if (filters.search) params.set("search", filters.search);
    if (filters.participant) params.set("participant", filters.participant);
    if (filters.tag) params.set("tag", filters.tag);
    if (filters.sort) params.set("sort", filters.sort);
    const qs = params.toString();
    return request<MeetingRow[]>(`/meetings${qs ? `?${qs}` : ""}`);
  },

  getMeeting(id: number): Promise<MeetingDetail> {
    return request<MeetingDetail>(`/meetings/${id}`);
  },

  createMeeting(payload: MeetingCreatePayload): Promise<MeetingDetail> {
    return request<MeetingDetail>("/meetings", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  updateMeeting(id: number, payload: MeetingUpdatePayload): Promise<MeetingDetail> {
    return request<MeetingDetail>(`/meetings/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  deleteMeeting(id: number): Promise<void> {
    return request<void>(`/meetings/${id}`, { method: "DELETE" });
  },

  uploadTranscript(id: number, content: string, filename: string): Promise<MeetingDetail> {
    const form = new FormData();
    form.set("content", content);
    form.set("filename", filename);
    return fetch(`${BASE}/api/meetings/${id}/transcript`, {
      method: "POST",
      body: form,
    }).then((r) => {
      if (!r.ok) throw new Error("Upload failed");
      return r.json();
    });
  },

  addActionItem(meetingId: number, text: string, assignee = "Unassigned", due = ""): Promise<ActionItem> {
    return request<ActionItem>(`/meetings/${meetingId}/action-items`, {
      method: "POST",
      body: JSON.stringify({ text, assignee, due_date: due }),
    });
  },

  updateActionItem(id: number, patch: Partial<ActionItem>): Promise<ActionItem> {
    return request<ActionItem>(`/action-items/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
  },

  deleteActionItem(id: number): Promise<void> {
    return request<void>(`/action-items/${id}`, { method: "DELETE" });
  },

  search(q: string): Promise<SearchResponse> {
    return request<SearchResponse>(`/search?q=${encodeURIComponent(q)}`);
  },

  addHighlight(meetingId: number, body: Partial<Highlight>): Promise<Highlight> {
    return request<Highlight>(`/meetings/${meetingId}/highlights`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  updateHighlight(id: number, patch: { note?: string; color?: string }): Promise<Highlight> {
    return request<Highlight>(`/highlights/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
  },

  deleteHighlight(id: number): Promise<void> {
    return request<void>(`/highlights/${id}`, { method: "DELETE" });
  },

  ask(meetingId: number, question: string): Promise<AskResponse> {
    return request<AskResponse>(`/meetings/${meetingId}/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },
};

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m >= 60) {
    const h = Math.floor(m / 60);
    return `${h}h ${m % 60}m`;
  }
  return `${m}m ${s.toString().padStart(2, "0")}s`;
}

export function formatTimestamp(ms: number): string {
  const total = Math.floor(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
