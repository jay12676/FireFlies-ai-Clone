"""Generate the full project-explanation PDF for interview prep.

Run with the backend venv (fpdf2 + matplotlib installed there):
    ../backend/.venv/Scripts/python.exe generate_explanation_pdf.py
Output: Fireflies_Clone_Explanation.pdf
"""
import os
import matplotlib
from fpdf import FPDF

FONT_DIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
DIAG = os.path.join(os.path.dirname(__file__), "diagrams")

BRAND = (108, 92, 231)
BRAND_DK = (76, 56, 180)
INK = (31, 41, 55)
GRAY = (107, 114, 128)
GREEN = (14, 159, 110)
LIGHTBG = (238, 241, 255)
CODEBG = (243, 244, 246)


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Fireflies.ai Clone  —  Project Explanation", align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(220, 220, 230)
        self.line(self.l_margin, 18, self.w - self.r_margin, 18)
        self.ln(6)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Author: Jayant (jay12676)  ·  github.com/jay12676/FireFlies-ai-Clone", align="C")


pdf = PDF(format="A4")
pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
pdf.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
pdf.add_font("Mono", "", os.path.join(FONT_DIR, "DejaVuSansMono.ttf"))
pdf.set_auto_page_break(True, margin=16)
EPW = pdf.w - pdf.l_margin - pdf.r_margin


def h1(text):
    if pdf.get_y() > pdf.h - 60:
        pdf.add_page()
    pdf.ln(2)
    pdf.set_font("DejaVu", "B", 15)
    pdf.set_text_color(*BRAND_DK)
    pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*BRAND)
    pdf.set_line_width(0.6)
    y = pdf.get_y() + 1
    pdf.line(pdf.l_margin, y, pdf.l_margin + 40, y)
    pdf.ln(4)


def h2(text):
    if pdf.get_y() > pdf.h - 40:
        pdf.add_page()
    pdf.ln(1)
    pdf.set_font("DejaVu", "B", 11.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def body(text, color=INK):
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5.4, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def bullets(items, color=INK):
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*color)
    for it in items:
        x = pdf.get_x()
        pdf.set_x(x + 2)
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(*BRAND)
        pdf.cell(4, 5.2, "•")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(*color)
        pdf.multi_cell(EPW - 6, 5.2, it, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.4)
    pdf.ln(1)


def file_entry(name, reason):
    pdf.set_font("Mono", "", 9.5)
    pdf.set_text_color(*GREEN)
    pdf.multi_cell(0, 5.4, name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9.5)
    pdf.set_text_color(*INK)
    pdf.set_x(pdf.l_margin + 4)
    pdf.multi_cell(EPW - 4, 5.0, reason, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def code(text):
    pdf.ln(1)
    pdf.set_font("Mono", "", 8.6)
    pdf.set_fill_color(*CODEBG)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 4.8, text, fill=True, new_x="LMARGIN", new_y="NEXT",
                   border=0, padding=2)
    pdf.ln(2)


def qa(q, a):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(*BRAND_DK)
    pdf.multi_cell(0, 5.4, "Q.  " + q, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 5.4, "A.  " + a, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.5)


def image_fit(path, max_w=EPW):
    if pdf.get_y() > pdf.h - 90:
        pdf.add_page()
    pdf.image(path, x=pdf.l_margin, w=max_w)
    pdf.ln(3)


# ============================================================ COVER
pdf.add_page()
pdf.ln(30)
pdf.set_fill_color(*BRAND)
pdf.rect(0, pdf.get_y(), pdf.w, 46, style="F")
pdf.ln(8)
pdf.set_font("DejaVu", "B", 26)
pdf.set_text_color(255, 255, 255)
pdf.multi_cell(0, 12, "Fireflies.ai Clone", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DejaVu", "", 13)
pdf.multi_cell(0, 8, "Meeting Notes & Transcription Platform", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(24)
pdf.set_font("DejaVu", "B", 14)
pdf.set_text_color(*INK)
pdf.multi_cell(0, 8, "Complete Project Explanation", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DejaVu", "", 10.5)
pdf.set_text_color(*GRAY)
pdf.multi_cell(0, 6, "How it works  ·  Every file & why it exists  ·  Workflow  ·  "
              "Database schema  ·  API  ·  Interview Q&A", align="C",
              new_x="LMARGIN", new_y="NEXT")
pdf.ln(16)
pdf.set_font("DejaVu", "", 11)
pdf.set_text_color(*INK)
pdf.multi_cell(0, 7, "Author:  Jayant  (jay12676)", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.multi_cell(0, 7, "Stack:  Next.js (TypeScript)  +  FastAPI (Python)  +  SQLite",
              align="C", new_x="LMARGIN", new_y="NEXT")
pdf.multi_cell(0, 7, "Repo:  github.com/jay12676/FireFlies-ai-Clone", align="C",
              new_x="LMARGIN", new_y="NEXT")

# ============================================================ 1. OVERVIEW
pdf.add_page()
h1("1.  Project Overview")
body("This is a functional clone of Fireflies.ai, a meeting-assistant web app. After a "
     "meeting, users browse a library of past meetings, open a meeting to read its "
     "interactive transcript (speaker labels + timestamps), view AI-generated notes "
     "(summary, action items, key topics), search across all transcripts, highlight "
     "and comment on transcript lines, ask questions about the meeting, and export the "
     "notes. Everything persists in a database.")
h2("What is real vs. mocked")
bullets([
    "Real: the full post-meeting workflow — library, interactive transcript synced to a "
    "media player, AI notes, search, CRUD, highlights/comments, export, dark mode.",
    "Mocked (allowed by the brief): live meeting-bot recording and real speech-to-text. "
    "Transcripts are seeded, pasted, or uploaded (.txt / .vtt / .json).",
    "The 'AI' is a deterministic rule-based engine (no API key, no cost, fully offline) "
    "with a clean hook to swap in a real LLM later.",
])
h2("Core features delivered")
bullets([
    "Meetings dashboard: search, filter by participant/tag, sort, responsive cards.",
    "Meeting detail: media player + interactive transcript with TWO-WAY sync.",
    "AI notes: summary (Gist), keywords, key topics/outline, action items.",
    "Full CRUD: create (form/paste/upload), edit, delete, action-item management.",
    "Bonus: global search, highlights/comments/soundbites, Ask-this-meeting chat, "
    "export to Markdown/TXT/PDF, dark mode, tags.",
])

# ============================================================ 2. TECH STACK
h1("2.  Tech Stack & Why")
h2("Frontend — Next.js 14 (App Router) + TypeScript + Tailwind CSS")
body("Next.js gives file-based routing, fast rendering, and a first-class TypeScript "
     "experience. TypeScript catches type errors at build time (the API response shapes "
     "are typed end-to-end). Tailwind lets us build the polished Fireflies look quickly "
     "with utility classes and a dark-mode variant.")
h2("Backend — FastAPI (Python)")
body("FastAPI is modern, async-capable, and auto-generates interactive API docs "
     "(Swagger at /docs) from Python type hints. Pydantic (built in) validates every "
     "request and serializes every response, so bad input is rejected before it reaches "
     "our logic.")
h2("ORM — SQLAlchemy 2.x  ·  Database — SQLite")
body("SQLAlchemy maps Python classes to tables and expresses relationships cleanly. "
     "SQLite is a zero-config, file-based database — perfect for a self-contained demo "
     "that runs anywhere with no separate DB server. The schema is standard SQL, so it "
     "would port to Postgres by changing one connection string.")
h2("Testing — pytest  ·  Packaging — Docker")
body("22 backend tests cover the parser, generator, models (cascade delete), and the "
     "full API lifecycle. Dockerfiles + docker-compose let the whole stack run with one "
     "command.")

# ============================================================ 3. ARCHITECTURE
h1("3.  High-Level Architecture (HLD)")
body("The system has three tiers with a strict one-directional dependency flow. The "
     "browser talks only to the frontend; the frontend talks to the backend only over "
     "HTTP/JSON; the backend is the only thing that touches the database.")
image_fit(os.path.join(DIAG, "hld_architecture.png"))
h2("Backend layering (separation of concerns)")
bullets([
    "Routers (thin HTTP layer): validate input, call CRUD, return responses. No business "
    "logic. One router per resource.",
    "CRUD (crud.py): the ONLY layer that touches the ORM. All database reads/writes live "
    "here, so data access is centralised and testable.",
    "Services (parser, generator, ask): pure functions for transcript parsing and the "
    "rule-based AI. They know nothing about HTTP or the database.",
    "Models (SQLAlchemy) + Schemas (Pydantic): models are the DB tables; schemas are the "
    "request/response contracts. Keeping them separate means the API shape can differ "
    "from the storage shape.",
])
body("Why this matters: each layer can be understood and tested on its own, and a change "
     "in one layer (e.g. swapping SQLite for Postgres, or the rule-based generator for an "
     "LLM) touches only that layer.")

# ============================================================ 4. WORKFLOW
h1("4.  How a Request Flows (Walkthroughs)")
h2("A) Opening the dashboard")
body("Browser loads app/page.tsx -> lib/api.ts calls GET /api/meetings -> the meetings "
     "router calls crud.list_meetings() -> SQLAlchemy runs one query (plus batched "
     "selectinload queries for participants/tags/action-items to avoid N+1) -> Pydantic "
     "serialises rows into MeetingSummaryRow JSON -> React renders the card grid.")
h2("B) Opening a meeting (the two-way sync)")
body("app/meetings/[id]/page.tsx calls GET /api/meetings/{id} for the full detail. The "
     "page holds the <audio> element as the single source of truth for time:")
bullets([
    "Click a transcript line / topic / citation -> seekTo(ms) sets audio.currentTime and "
    "updates currentMs.",
    "Audio playback -> onTimeUpdate fires -> currentMs updates -> TranscriptPanel "
    "highlights and auto-scrolls the line whose [start_ms, next.start_ms) window contains "
    "currentMs.",
    "Time is stored in milliseconds everywhere; we divide by 1000 only at the audio "
    "boundary (the HTML audio API uses seconds).",
])
h2("C) Creating / uploading a transcript")
body("POST /api/meetings (or /transcript) sends the raw text + filename. The backend "
     "runs services/parser.py to turn it into ordered segments, then services/generator.py "
     "to produce the summary, action items, and topics, and stores everything. Re-uploading "
     "replaces the old segments and regenerates the AI notes so they never drift out of sync.")
h2("D) Asking a question about the meeting")
body("POST /api/meetings/{id}/ask sends the question. services/ask.py classifies intent "
     "(action items / decision / who / general). Action-item questions return the extracted "
     "tasks; general questions score transcript segments by keyword overlap (with light "
     "stemming) and return the best matches with citations (speaker + timestamp) that the "
     "UI turns into clickable chips that seek the player.")

# ============================================================ 5. BACKEND FILES
h1("5.  Backend — Every File & Why It Exists")
body("Folder: backend/app/", GRAY)
file_entry("main.py", "The FastAPI application factory. Creates the app, configures CORS "
           "(so the browser on :3000 may call the API on :8000), mounts all routers under "
           "/api, exposes /api/health, and auto-seeds sample data on startup if the DB is "
           "empty. Entry point run by uvicorn.")
file_entry("database.py", "Sets up the SQLAlchemy engine, session factory (SessionLocal), "
           "declarative Base, and the get_db() dependency that hands each request a DB "
           "session and closes it afterwards. One place to configure the database URL.")
file_entry("models.py", "The SQLAlchemy ORM models = the database tables (Meeting, "
           "Participant, TranscriptSegment, Summary, KeyTopic, ActionItem, Highlight, Tag). "
           "Defines columns, foreign keys, relationships, and cascade-delete rules.")
file_entry("schemas.py", "Pydantic models = the API request/response contracts "
           "(Create/Update/Read variants). Validate incoming JSON and serialize outgoing "
           "JSON. Separate from models so the API shape is decoupled from storage.")
file_entry("crud.py", "The data-access layer — the ONLY module that touches the ORM. "
           "Functions like list_meetings, create_meeting, replace_transcript, "
           "add_action_item, global_search, ask_meeting. Centralises all queries.")
file_entry("routers/meetings.py", "HTTP endpoints for meetings: list, create, get, update, "
           "delete, upload transcript, add action item, add highlight, ask. Thin — delegates "
           "to crud.")
file_entry("routers/action_items.py", "Standalone update/toggle-complete/delete endpoints "
           "for action items (PATCH/DELETE /action-items/{id}).")
file_entry("routers/highlights.py", "Update/delete endpoints for highlights/comments "
           "(soundbites).")
file_entry("routers/search.py", "GET /search?q= — global full-text search across all "
           "transcript segments.")
file_entry("services/parser.py", "Converts an uploaded .txt / .vtt / .json transcript into a "
           "uniform list of segments (speaker, start_ms, end_ms, text). Picks the handler by "
           "extension, falls back to content sniffing, synthesises timestamps when missing.")
file_entry("services/generator.py", "The rule-based AI: extractive summary (rank sentences "
           "by keyword frequency), action-item extraction (cue phrases like 'will', 'need to', "
           "'by Friday'), and topic clustering (frequent keywords anchored to timestamps). "
           "Deterministic — same input always gives the same output.")
file_entry("services/ask.py", "The rule-based 'ask this meeting' engine. Classifies the "
           "question's intent, then either returns structured data (action items) or retrieves "
           "the most relevant transcript segments by keyword overlap with citations.")
file_entry("seed.py", "Builds 5 realistic sample meetings (standup, roadmap, sales call, 1:1, "
           "retro) with full transcripts, summaries, topics, action items, participants, tags. "
           "Auto-runs on first startup so the app is usable immediately.")
file_entry("tests/", "pytest suite: test_parser, test_generator, test_models (cascade), "
           "test_api (full CRUD + search + highlights + ask). 22 tests.")

# ============================================================ 6. FRONTEND FILES
h1("6.  Frontend — Every File & Why It Exists")
body("Folder: frontend/", GRAY)
file_entry("app/layout.tsx", "The root shell wrapping every page: sidebar + navbar + Theme "
           "and Toast context providers. Rendered once around all routes.")
file_entry("app/page.tsx", "The dashboard / meetings library: card grid with debounced "
           "search, participant & tag filters, sort, loading skeletons, and the New-Meeting "
           "modal.")
file_entry("app/meetings/[id]/page.tsx", "The meeting detail page. Owns the audio element and "
           "the currentMs/seekTo state that drives the two-way transcript sync; wires the "
           "player, transcript, notes tabs, edit/delete, export, and highlights.")
file_entry("app/search/page.tsx", "Global search results grouped by meeting with highlighted "
           "snippets.")
file_entry("app/settings/page.tsx", "Profile, dark-mode toggle, and 'Coming Soon' "
           "placeholders (bot, integrations, team, live transcription).")
file_entry("components/", "Reusable UI units: Sidebar, Navbar, MeetingCard, Avatars, Modal, "
           "NewMeetingModal, EditMeetingModal, MediaPlayer, TranscriptPanel, MeetingTabs, "
           "ActionItems, AskChat, ExportMenu, Highlight. Each has one responsibility.")
file_entry("context/ThemeContext.tsx", "Dark-mode state, persisted to localStorage and "
           "applied as a class on <html>.")
file_entry("context/ToastContext.tsx", "App-wide toast notifications via a simple queue + "
           "portal.")
file_entry("lib/api.ts", "The single typed API client. Every backend call goes through one "
           "request() helper (base URL, JSON headers, error unwrapping). Also holds date/"
           "time/duration formatting helpers.")
file_entry("lib/types.ts", "TypeScript interfaces mirroring the backend schemas — end-to-end "
           "type safety.")
file_entry("lib/export.ts", "Builds Markdown / TXT / PDF exports of a meeting (jsPDF for the "
           "PDF), all client-side.")

# ============================================================ 7. DATABASE
h1("7.  Database Schema")
body("Meetings is the central table. Everything else hangs off it. All child rows "
     "cascade-delete when their meeting is deleted, so there are never orphan records.")
image_fit(os.path.join(DIAG, "er_diagram.png"))
h2("Relationships & why")
bullets([
    "Meeting 1:N Participant / TranscriptSegment / KeyTopic / ActionItem / Highlight — a "
    "meeting has many of each.",
    "Meeting 1:1 Summary — each meeting has exactly one summary (enforced by a UNIQUE "
    "constraint on summaries.meeting_id).",
    "Meeting M:N Tag via the meeting_tags join table — a tag can belong to many meetings "
    "and a meeting can have many tags.",
    "Highlight -> TranscriptSegment (nullable FK) — a highlight snapshots the quote/speaker/"
    "time so the saved soundbite survives even if the transcript is later replaced.",
    "start_ms / end_ms on segments (milliseconds) drive the player seek and the active-line "
    "highlight; order_index preserves display order.",
])

# ============================================================ 8. API
h1("8.  API Reference  (prefix /api)")
body("REST conventions: nouns for resources, HTTP verbs for actions, correct status codes "
     "(201 created, 204 no-content, 404 not found). Interactive docs live at "
     "http://localhost:8000/docs.")
endpoints = [
    ("GET", "/meetings", "List meetings (?search, participant, tag, sort)"),
    ("POST", "/meetings", "Create meeting (+ optional pasted/uploaded transcript)"),
    ("GET", "/meetings/{id}", "Full meeting detail"),
    ("PATCH", "/meetings/{id}", "Update title / participants / tags"),
    ("DELETE", "/meetings/{id}", "Delete meeting (cascades to children)"),
    ("POST", "/meetings/{id}/transcript", "Upload/paste transcript -> parse -> regenerate"),
    ("POST", "/meetings/{id}/action-items", "Add an action item"),
    ("PATCH", "/action-items/{id}", "Edit / toggle complete"),
    ("DELETE", "/action-items/{id}", "Delete an action item"),
    ("POST", "/meetings/{id}/highlights", "Add a highlight / comment (soundbite)"),
    ("PATCH", "/highlights/{id}", "Edit a highlight"),
    ("DELETE", "/highlights/{id}", "Delete a highlight"),
    ("POST", "/meetings/{id}/ask", "Ask a question -> answer + cited segments"),
    ("GET", "/search?q=", "Global search across all transcripts"),
]
pdf.set_font("Mono", "", 8.6)
for method, path, desc in endpoints:
    pdf.set_text_color(*BRAND)
    pdf.cell(16, 5.4, method)
    pdf.set_text_color(*INK)
    pdf.cell(56, 5.4, path)
    pdf.set_text_color(*GRAY)
    pdf.multi_cell(EPW - 72, 5.4, desc, new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

# ============================================================ 9. THE AI
h1("9.  The 'AI' Explained (Rule-Based, No LLM)")
body("A common interview question: 'how does the AI work?' The answer is honest — it is "
     "classic NLP heuristics, chosen deliberately so the demo is deterministic, free, and "
     "works offline. Each piece has a clean seam to swap in a real LLM.")
h2("Summary — extractive, frequency-based")
body("Count how often each meaningful word appears (after removing stopwords). Score each "
     "sentence by the average frequency of its words, take the top N, and re-sort them into "
     "reading order. This is the idea behind Luhn's algorithm / TextRank.")
h2("Action items — cue-phrase matching")
body("Scan sentences for action cues ('will', 'I'll', 'need to', 'let's', 'follow up', "
     "'action item', 'by Friday', ...). The nearest preceding speaker becomes the assignee; "
     "a date phrase becomes the due date.")
h2("Topics / outline — keyword clustering")
body("Take the most frequent meaningful keywords and anchor each to the first timestamp "
     "where it appears, producing time-linked chapters.")
h2("Ask this meeting — intent routing + retrieval")
body("Classify the question (action / decision / who / general). Action questions return "
     "the structured action items; general questions score segments by keyword overlap "
     "(with light stemming so 'payments' matches 'payment') and return the best matches "
     "with timestamped citations.")
body("Upgrade path: every one of these is a single pure function. To use a real LLM, replace "
     "the body of that function with an API call that sends the same retrieved context — "
     "nothing else in the app changes.")

# ============================================================ 10. DECISIONS
h1("10.  Key Design Decisions & Trade-offs")
bullets([
    "Layered backend (routers -> crud -> models + services): separation of concerns; each "
    "layer is independently testable.",
    "Rule-based AI instead of an LLM: deterministic, free, offline, and reproducible for a "
    "graded demo — with a clear upgrade seam.",
    "SQLite: zero-config and portable; standard SQL means an easy move to Postgres.",
    "Milliseconds everywhere for time: integer math avoids floating-point drift; we convert "
    "to seconds only at the HTML audio boundary.",
    "Naive local datetimes for display: the shown clock time never shifts due to timezone "
    "conversion. New meetings capture the live creation time.",
    "Single typed API client on the frontend: base URL, headers, and error handling live in "
    "one place; components never call fetch() directly.",
    "Replace-and-regenerate on transcript upload: keeps AI notes consistent with the actual "
    "words; makes the parse->generate pipeline idempotent.",
])

# ============================================================ 11. Q&A
h1("11.  Likely Interview Questions & Answers")
qa("Walk me through what happens when I click a transcript line.",
   "The line's onClick calls seekTo(startMs), which sets the shared <audio> element's "
   "currentTime and plays it. As it plays, onTimeUpdate updates currentMs; TranscriptPanel "
   "recomputes which segment is active (last one with start_ms <= currentMs) and highlights "
   "+ auto-scrolls it. That's the two-way sync.")
qa("How is your database structured and why?",
   "Meetings is the central table; participants, transcript_segments, key_topics, "
   "action_items, and highlights are 1:N children; summaries is 1:1; tags is M:N via a join "
   "table. Children cascade-delete with their meeting so there are no orphans.")
qa("Why FastAPI and how is the backend organised?",
   "FastAPI gives type-driven validation and auto docs. It's layered: routers handle HTTP, "
   "crud.py is the only ORM layer, services hold parsing + the rule-based AI, models are the "
   "tables, schemas are the API contracts.")
qa("How does the AI summary work? Is it a real model?",
   "It's deterministic rule-based NLP: extractive frequency-based summary, cue-phrase action "
   "items, keyword-clustered topics. I chose it so the demo is free, offline, and "
   "reproducible, and I left each function as a clean seam to drop in an LLM.")
qa("How do you avoid the N+1 query problem?",
   "In crud.list_meetings I use SQLAlchemy selectinload for participants/tags/action_items, "
   "so related rows are fetched in a few batched queries instead of one query per meeting.")
qa("What happens on transcript upload?",
   "The parser normalises .txt/.vtt/.json into uniform segments; then the generator rebuilds "
   "the summary, topics, and action items. I replace the old data entirely so the notes can't "
   "drift from the transcript.")
qa("How would you scale or productionise this?",
   "Swap SQLite for Postgres (one connection string), add authentication (JWT), move the "
   "rule-based services to real LLM calls behind the same function signatures, add caching, "
   "and deploy the frontend (Vercel) and backend (Render/Railway) — Dockerfiles are already "
   "provided.")
qa("How is the frontend kept type-safe and DRY?",
   "lib/types.ts mirrors the backend schemas, and every network call goes through one typed "
   "request() helper in lib/api.ts, so base URL, headers, and error handling exist in exactly "
   "one place.")

# ============================================================ 12. RUN
h1("12.  How to Run & Test")
h2("Backend")
code("cd backend\n"
     "python -m venv .venv\n"
     ".venv\\Scripts\\activate            # Windows\n"
     "pip install -r requirements.txt\n"
     "uvicorn app.main:app --reload --port 8000\n"
     "# API: http://localhost:8000    Docs: http://localhost:8000/docs")
h2("Frontend")
code("cd frontend\n"
     "cp .env.example .env.local        # NEXT_PUBLIC_API_URL=http://localhost:8000\n"
     "npm install\n"
     "npm run dev                       # http://localhost:3000")
h2("Tests / seed")
code("cd backend\n"
     "pytest                            # 22 tests\n"
     "python -m app.seed --reset        # wipe & reseed sample meetings")

out = os.path.join(os.path.dirname(__file__), "Fireflies_Clone_Explanation.pdf")
pdf.output(out)
print("wrote", out)
