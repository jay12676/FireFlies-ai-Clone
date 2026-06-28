# Fireflies.ai Clone — Meeting Notes & Transcription Platform

A functional clone of the [Fireflies.ai](https://fireflies.ai) meeting assistant.
Browse a library of meetings, read **interactive transcripts** with speaker labels
and timestamps, view **AI-generated summaries, action items, and key topics**,
**search across all transcripts**, and manage meetings end-to-end (create, edit,
delete, upload transcripts, manage action items).

> Real speech-to-text is intentionally out of scope. Transcripts are seeded,
> pasted, or uploaded (`.txt` / `.vtt` / `.json`), and summaries/action-items/
> topics are produced by a **deterministic rule-based generator** — no API keys,
> no cost, works fully offline.

---

## Tech Stack

| Layer       | Technology |
|-------------|------------|
| Frontend    | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend     | FastAPI, SQLAlchemy 2.x, Pydantic v2 |
| Database    | SQLite |
| Tests       | pytest (backend) |
| Packaging   | Docker + docker-compose |

---

## Features

**Core**
- 📚 **Meetings library / dashboard** — card grid with title, date, duration,
  participants, tags & action-item counts; search by title; filter by participant
  or tag; sort by recency / oldest / title.
- 🎧 **Interactive transcript detail view** — media player (sample audio) with a
  working seek bar, **two-way synced** to the transcript: clicking a line seeks
  the player, and playback highlights & auto-scrolls the active line.
- 🔎 **In-transcript search** with match highlighting and prev/next navigation.
- ✨ **AI summary & notes** — overview, key topics/chapters (click to seek),
  and extracted action items.
- 📝 **Full CRUD** — create meetings (form + paste/upload transcript), edit
  metadata & participants, delete, and add / edit / complete / delete action items.
- 💾 Everything persists in SQLite.

**Bonus included**
- 🌐 Global search across all meetings' transcripts (grouped results).
- ⬇️ Export transcript + summary to **Markdown** or **TXT**.
- 🌙 Dark mode (persisted).
- 🏷️ Tags + filtering.
- 🔔 Toast notifications, modals, loading skeletons, empty states.

**Stubbed "Coming Soon"** (as allowed by the brief): live meeting bot, real STT,
Zoom/Meet/calendar/CRM integrations, team/sharing, real authentication
(a default logged-in user is assumed).

---

## Architecture Overview

```
┌─────────────────────────┐         HTTP/JSON (/api)        ┌──────────────────────────┐
│   Next.js Frontend       │  ───────────────────────────▶  │   FastAPI Backend         │
│   (App Router, TS)       │                                 │                           │
│                          │                                 │  routers ─▶ crud ─▶ models│
│  app/         pages      │ ◀───────────────────────────   │            │              │
│  components/  UI units   │                                 │            ▼              │
│  context/     theme,toast│                                 │     services/             │
│  lib/         api client │                                 │     ├─ parser  (txt/vtt/  │
└─────────────────────────┘                                 │     │           json)     │
                                                             │     └─ generator (summary,│
                                                             │         action items,     │
                                                             │         topics)           │
                                                             │            │              │
                                                             │            ▼   SQLAlchemy  │
                                                             │        SQLite (fireflies.db)│
                                                             └──────────────────────────┘
```

**Backend layering (separation of concerns):**
- `routers/` — thin HTTP layer (validation, status codes), no business logic.
- `crud.py` — the only layer that touches the ORM; all DB operations live here.
- `services/parser.py` — converts uploaded `.txt`/`.vtt`/`.json` into segments.
- `services/generator.py` — rule-based summary / action items / topics.
- `models.py` / `schemas.py` — ORM models vs. Pydantic request/response models.
- `seed.py` — sample data; auto-seeds on startup when the DB is empty.

**Frontend structure:**
- `app/` — routes: `/` (dashboard), `/meetings/[id]` (detail), `/search`, `/settings`.
- `components/` — focused, reusable UI units (cards, panels, player, modals…).
- `context/` — `ThemeContext` (dark mode) and `ToastContext` (notifications).
- `lib/api.ts` — typed API client; `lib/export.ts` — Markdown/TXT export.

---

## Database Schema

```
meetings
  id PK · title · description · date · duration_seconds · audio_url
  created_at · updated_at

participants            transcript_segments          summaries (1:1 meeting)
  id PK                   id PK                         id PK
  meeting_id FK ─┐        meeting_id FK ─┐              meeting_id FK (unique) ─┐
  name           │        speaker        │             overview                │
  email          │        start_ms       │             generated_by            │
  role           │        end_ms         │                                     │
                 │        text           │             key_topics              │
action_items     │        order_index    │               id PK                 │
  id PK          │                       │               meeting_id FK ────────┤
  meeting_id FK ─┤      tags             │               title                 │
  text           │        id PK          │               start_ms              │
  assignee       │        name (unique)  │               order_index           │
  due_date       │                       │                                     │
  completed      │      meeting_tags (M2M)                                      │
  order_index    │        meeting_id FK ──┘                                     │
  created_at     │        tag_id FK ──────────────────────────────────────────┘
```

**Relationships**
- `Meeting` 1─N `Participant`, `TranscriptSegment`, `KeyTopic`, `ActionItem`
- `Meeting` 1─1 `Summary`
- `Meeting` M─N `Tag` (via `meeting_tags`)
- All children **cascade-delete** when a meeting is deleted.

---

## API Overview

Base path: `/api`

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/health` | Health check |
| GET    | `/meetings` | List meetings — query: `search`, `participant`, `tag`, `sort` (`recent`\|`oldest`\|`title`) |
| POST   | `/meetings` | Create meeting (metadata + optional pasted/uploaded transcript) |
| GET    | `/meetings/{id}` | Full meeting detail (segments, summary, topics, action items, participants, tags) |
| PATCH  | `/meetings/{id}` | Update title / description / participants / tags |
| DELETE | `/meetings/{id}` | Delete meeting (cascades) |
| POST   | `/meetings/{id}/transcript` | Upload a transcript file **or** form text → parse + regenerate summary/topics/actions |
| POST   | `/meetings/{id}/action-items` | Add an action item |
| PATCH  | `/action-items/{id}` | Edit / toggle complete |
| DELETE | `/action-items/{id}` | Delete an action item |
| GET    | `/search?q=` | Global search across all transcript segments |

Interactive API docs are available at **`http://localhost:8000/docs`** (Swagger UI).

---

## Getting Started (Local)

### Prerequisites
- Python 3.11+ and Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

# (optional) seed/reset sample data manually:
python -m app.seed          # seed if empty
python -m app.seed --reset  # drop & reseed

uvicorn app.main:app --reload --port 8000
```

The backend auto-creates tables and seeds 5 sample meetings on first startup.
API: <http://localhost:8000> · Docs: <http://localhost:8000/docs>

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local      # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

App: <http://localhost:3000>

### Run backend tests

```bash
cd backend
pytest          # 19 tests: parser, generator, models, full API lifecycle
```

---

## Getting Started (Docker)

```bash
docker-compose up --build
```

- Frontend → <http://localhost:3000>
- Backend  → <http://localhost:8000>

---

## Deployment Notes

The app is deployment-agnostic. A common split:

- **Frontend → Vercel** — import `frontend/`, set `NEXT_PUBLIC_API_URL` to the
  deployed backend URL.
- **Backend → Render / Railway** — start command
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, set `CORS_ORIGINS` to the
  deployed frontend URL. (SQLite persists on the instance disk; for ephemeral
  hosts the DB simply re-seeds on boot, which is fine for a demo.)

Both Dockerfiles are production-ready if you prefer a single container host.

---

## Assumptions

- **Single default user** ("Gyana M.") — no real auth, per the brief.
- **Audio is illustrative** — meetings reference a public sample MP3; the seek
  bar and transcript-sync are fully functional against it. Seeded transcript
  timestamps are independent of the audio length, so the highlight maps to
  transcript time rather than literal spoken words.
- **AI is rule-based**, not an LLM — summaries rank sentences by keyword
  frequency; action items are detected via cue phrases (e.g. "will", "need to",
  "follow up", "by Friday"); topics are frequent-keyword clusters anchored to
  their first timestamp. Output is deterministic and reproducible.
- Uploading a transcript **replaces** existing segments and regenerates the
  summary, topics, and action items for that meeting.

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # app factory, CORS, startup seeding
│   │   ├── database.py      # engine/session/Base
│   │   ├── models.py        # SQLAlchemy ORM
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # DB operations
│   │   ├── seed.py          # sample data
│   │   ├── routers/         # meetings, action_items, search
│   │   └── services/        # parser, generator
│   ├── tests/               # pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                 # routes (dashboard, detail, search, settings)
│   ├── components/          # UI components
│   ├── context/             # theme + toast providers
│   ├── lib/                 # api client, types, export helpers
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
