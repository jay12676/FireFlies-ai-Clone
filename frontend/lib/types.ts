export interface Participant {
  id?: number;
  name: string;
  email?: string;
  role?: string;
}

export interface Segment {
  id: number;
  speaker: string;
  start_ms: number;
  end_ms: number;
  text: string;
  order_index: number;
}

export interface Summary {
  id: number;
  overview: string;
  generated_by: string;
}

export interface Topic {
  id: number;
  title: string;
  start_ms: number;
  order_index: number;
}

export interface ActionItem {
  id: number;
  text: string;
  assignee: string;
  due_date: string;
  completed: boolean;
  order_index: number;
}

export interface Tag {
  id: number;
  name: string;
}

export interface Highlight {
  id: number;
  segment_id: number | null;
  quote: string;
  note: string;
  speaker: string;
  color: string;
  start_ms: number;
  end_ms: number;
}

export interface AskCitation {
  segment_id: number;
  speaker: string;
  start_ms: number;
  text: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  citations: AskCitation[];
}

export interface MeetingRow {
  id: number;
  title: string;
  date: string;
  duration_seconds: number;
  participants: Participant[];
  tags: Tag[];
  action_item_count: number;
}

export interface MeetingDetail {
  id: number;
  title: string;
  description: string;
  date: string;
  duration_seconds: number;
  audio_url: string;
  created_at: string;
  updated_at: string;
  participants: Participant[];
  segments: Segment[];
  summary: Summary | null;
  topics: Topic[];
  action_items: ActionItem[];
  highlights: Highlight[];
  tags: Tag[];
}

export interface SearchHit {
  meeting_id: number;
  meeting_title: string;
  segment_id: number;
  speaker: string;
  start_ms: number;
  text: string;
}

export interface SearchResponse {
  query: string;
  count: number;
  hits: SearchHit[];
}

export interface MeetingCreatePayload {
  title: string;
  description?: string;
  date?: string | null;
  duration_seconds?: number;
  participants?: Participant[];
  tags?: string[];
  transcript_text?: string | null;
  transcript_filename?: string | null;
}

export interface MeetingUpdatePayload {
  title?: string;
  description?: string;
  participants?: Participant[];
  tags?: string[];
}
