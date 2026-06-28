# Fireflies.ai Clone Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a functional Fireflies.ai clone — meetings library, interactive transcript detail view, AI summaries/action items/topics, full CRUD, global search, export, and dark mode — with a FastAPI/SQLite backend and a Next.js/Tailwind frontend.

**Architecture:** Layered FastAPI backend (routers → crud → models, plus parser/generator services) over SQLite via SQLAlchemy. Next.js App Router frontend with a typed API client and React Context for theme + toasts. Backend logic (parser, generator, API) is TDD'd with pytest; frontend is verified by running the app.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic v2, SQLite, pytest; Next.js 14 (App Router), TypeScript, Tailwind CSS; Docker + docker-compose.

---

## Phase A — Backend

### Task 1: Backend scaffold + database

**Files:**
- Create: `backend/requirements.txt`, `backend/app/__init__.py`, `backend/app/database.py`, `backend/app/main.py`, `backend/pytest.ini`, `backend/tests/__init__.py`, `backend/tests/conftest.py`

- [ ] requirements.txt: fastapi, uvicorn[standard], sqlalchemy, pydantic, python-multipart, pytest, httpx.
- [ ] database.py: SQLite engine (`sqlite:///./fireflies.db`), `SessionLocal`, `Base`, `get_db` dependency.
- [ ] main.py: app factory, CORS (allow localhost:3000 + env origin), mount `/api` routers, `GET /api/health`.
- [ ] conftest.py: pytest fixture with in-memory SQLite + FastAPI `TestClient`.
- [ ] Verify: `pytest -q` collects, `GET /api/health` returns `{"status":"ok"}`.

### Task 2: ORM models

**Files:** Create `backend/app/models.py`

- [ ] Define Meeting, Participant, TranscriptSegment, Summary (1:1), KeyTopic, ActionItem, Tag + `meeting_tags` association, per spec §4. Use `relationship(..., cascade="all, delete-orphan")` on Meeting children.
- [ ] Test (`tests/test_models.py`): create a Meeting with children, commit, assert cascade delete removes segments/summary/action items.

### Task 3: Pydantic schemas

**Files:** Create `backend/app/schemas.py`

- [ ] Base/Create/Update/Read models for each entity; `MeetingDetail` aggregates participants, segments, summary, topics, action_items, tags. `from_attributes=True`.
- [ ] Test (`tests/test_schemas.py`): a model instance serializes into `MeetingDetail` with nested lists.

### Task 4: Transcript parser service

**Files:** Create `backend/app/services/parser.py`; Test `backend/tests/test_parser.py`

- [ ] `parse_transcript(content: str, filename: str) -> list[ParsedSegment]` dispatching by extension/content.
- [ ] `.txt`: lines `Speaker: text`, optional leading `[mm:ss]` / `[hh:mm:ss]`; synthesize start_ms sequentially (~4s/segment) when absent.
- [ ] `.vtt`: parse cue `HH:MM:SS.mmm --> HH:MM:SS.mmm` + text; speaker from `<v Name>` or `Name:` prefix.
- [ ] `.json`: array of `{speaker,start_ms,end_ms,text}` or `{start,end}` seconds.
- [ ] Tests cover each format incl. missing timestamps and multi-speaker.

### Task 5: Rule-based generator service

**Files:** Create `backend/app/services/generator.py`; Test `backend/tests/test_generator.py`

- [ ] `generate_summary(segments) -> str`: rank sentences by keyword frequency (stopword-filtered), return top N joined.
- [ ] `extract_action_items(segments) -> list[ActionItemDraft]`: match cues (`will`, `need to`, `todo`, `let's`, `action item`, `follow up`, `by <weekday/date>`); assignee = nearest preceding speaker or "Unassigned".
- [ ] `extract_topics(segments) -> list[TopicDraft]`: cluster by top keywords, attach first occurrence start_ms as chapter time.
- [ ] Deterministic (no randomness). Tests assert action items found and topics non-empty for a sample transcript.

### Task 6: CRUD layer

**Files:** Create `backend/app/crud.py`; Test `backend/tests/test_crud.py`

- [ ] Functions: list_meetings(filters: search/participant/tag/sort), get_meeting, create_meeting, update_meeting, delete_meeting; add/update/delete action_item; replace_transcript (parse → segments → regenerate summary/topics/action items); global_search(q).
- [ ] Tests: create→get, filter by participant, sort recency, update, delete cascade, action-item toggle, search matches segment text.

### Task 7: Routers

**Files:** Create `backend/app/routers/{__init__,meetings,action_items,search}.py`; Test `backend/tests/test_api.py`

- [ ] Implement all endpoints from spec §5 wiring to crud; transcript endpoint accepts multipart file OR JSON `{content, filename}`.
- [ ] Tests via TestClient: full CRUD lifecycle, filters, transcript upload regenerates summary, search endpoint.

### Task 8: Seed data

**Files:** Create `backend/app/seed.py`, `backend/app/static/sample-audio.mp3` (or reference a hosted sample), `backend/seed_data/*.json`

- [ ] 4–5 realistic meetings (standup, product sync, customer call, 1:1, sprint retro) with multi-speaker timestamped transcripts, seeded summaries, topics, action items, participants, tags.
- [ ] `python -m app.seed` (idempotent: skip if meetings exist; `--reset` flag drops + reseeds).
- [ ] App startup seeds if DB empty.

## Phase B — Frontend

### Task 9: Frontend scaffold + Tailwind + theme/toast context

**Files:** `frontend/` Next.js app; `frontend/app/layout.tsx`, `frontend/lib/api.ts`, `frontend/lib/types.ts`, `frontend/context/{ThemeContext,ToastContext}.tsx`, `frontend/tailwind.config.ts`, `frontend/app/globals.css`

- [ ] `create-next-app` (TS, App Router, Tailwind). Fireflies palette (purple/indigo accent, neutral grays) via Tailwind theme + `darkMode: 'class'`.
- [ ] `lib/api.ts`: typed fetch client using `NEXT_PUBLIC_API_URL`.
- [ ] ThemeContext (persist dark mode in localStorage), ToastContext (toast queue + portal).
- [ ] Layout: sidebar (Home, Search, Settings, Coming-Soon items) + top navbar (profile avatar placeholder, dark-mode toggle).
- [ ] Verify: `npm run dev` renders shell.

### Task 10: Meetings dashboard

**Files:** `frontend/app/page.tsx`, `frontend/components/{MeetingCard,SearchBar,FilterBar,SortDropdown,NewMeetingModal}.tsx`

- [ ] Fetch `/meetings`; responsive card grid (title, date, duration, participant avatars, tags).
- [ ] SearchBar (title), FilterBar (participant, tag), SortDropdown (recency) → query params.
- [ ] "New Meeting" button → modal: form (title/date/participants) + transcript paste/upload tabs → POST; toast on success; refresh list.
- [ ] Empty state + loading skeletons.

### Task 11: Meeting detail — media player + transcript

**Files:** `frontend/app/meetings/[id]/page.tsx`, `frontend/components/{MediaPlayer,TranscriptPanel,TranscriptLine,TranscriptSearch}.tsx`

- [ ] Fetch `/meetings/{id}`. Layout: player on top, transcript left, summary/tabs right.
- [ ] MediaPlayer: HTML5 audio (sample file), play/pause, seek bar, current-time; expose `currentMs` + `seekTo(ms)`.
- [ ] TranscriptPanel: lines with speaker label + `[mm:ss]`; active line (currentMs within segment) highlighted + auto-scrolled; click line → `seekTo(start_ms)`.
- [ ] TranscriptSearch: filter/highlight matches within transcript, prev/next match navigation.

### Task 12: Meeting detail — summary, topics, action items, edit/delete

**Files:** `frontend/components/{SummaryPanel,TopicsList,ActionItems,EditMeetingModal,ExportMenu}.tsx`

- [ ] Tabbed right panel: Summary (overview), Topics/Chapters (click → seek), Action Items.
- [ ] ActionItems: list with checkbox (PATCH toggle), add (POST), edit, delete; assignee + due date.
- [ ] Edit meeting metadata modal (PATCH); Delete meeting (confirm → DELETE → toast → route home).
- [ ] ExportMenu: download transcript and summary as Markdown / TXT (client-side blob).

### Task 13: Global search + settings

**Files:** `frontend/app/search/page.tsx`, `frontend/app/settings/page.tsx`

- [ ] Search page: query `/search?q=`, group results by meeting with snippet highlights, link to detail.
- [ ] Settings: placeholder sections (Profile, Integrations "Coming Soon", Bot "Coming Soon", Team "Coming Soon") styled like Fireflies.

## Phase C — Docs & Deploy

### Task 14: Docker + compose

**Files:** `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.env.example` files

- [ ] Backend image (uvicorn), frontend image (next build/start), compose wiring with `NEXT_PUBLIC_API_URL`.
- [ ] Verify `docker-compose up` serves both.

### Task 15: README + final verification

**Files:** `README.md`, `.gitignore`

- [ ] README: overview, tech stack, architecture diagram, DB schema, API table, setup (local + Docker), seed instructions, assumptions, deployment notes (Vercel/Render/Railway).
- [ ] Run full backend test suite; run both servers; smoke-test every core feature.

## Self-Review Notes

- Spec coverage: dashboard (T10), detail/transcript/player (T11), summary/topics/action items (T12), CRUD (T7/T10/T12), search (T6/T7/T13), export/dark mode/tags (T9/T10/T12), parser/generator (T4/T5), seed (T8), docs/deploy (T14/T15). All spec sections mapped.
- Stubs: live bot, STT, integrations, team, auth → Settings/sidebar "Coming Soon" (T9/T13).
