"""Seed the database with realistic sample meetings.

Run directly:  python -m app.seed [--reset]
On app startup, ``seed_if_empty`` runs automatically when the DB has no meetings.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from . import models

AUDIO = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
AUDIO2 = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"

_now = datetime.now(timezone.utc)


def _segments(rows: list[tuple[str, int, str]]) -> list[models.TranscriptSegment]:
    segs = []
    for i, (speaker, start_ms, text) in enumerate(rows):
        end = rows[i + 1][1] if i + 1 < len(rows) else start_ms + 5000
        segs.append(
            models.TranscriptSegment(
                speaker=speaker, start_ms=start_ms, end_ms=end, text=text, order_index=i
            )
        )
    return segs


def _build_meeting(spec: dict, tag_cache: dict[str, models.Tag]) -> models.Meeting:
    m = models.Meeting(
        title=spec["title"],
        description=spec.get("description", ""),
        date=spec["date"],
        audio_url=spec.get("audio_url", AUDIO),
    )
    m.participants = [models.Participant(**p) for p in spec["participants"]]
    m.segments = _segments(spec["transcript"])
    m.duration_seconds = (m.segments[-1].end_ms // 1000) if m.segments else 0
    m.summary = models.Summary(overview=spec["summary"], generated_by="seed")
    m.topics = [
        models.KeyTopic(title=t[0], start_ms=t[1], order_index=i)
        for i, t in enumerate(spec["topics"])
    ]
    m.action_items = [
        models.ActionItem(
            text=a["text"], assignee=a.get("assignee", "Unassigned"),
            due_date=a.get("due_date", ""), completed=a.get("completed", False), order_index=i,
        )
        for i, a in enumerate(spec["action_items"])
    ]
    tags = []
    for name in spec.get("tags", []):
        if name not in tag_cache:
            tag_cache[name] = models.Tag(name=name)
        tags.append(tag_cache[name])
    m.tags = tags
    return m


MEETINGS: list[dict] = [
    {
        "title": "Q3 Product Roadmap Planning",
        "description": "Aligning engineering and design on Q3 priorities.",
        "date": _now - timedelta(days=1, hours=3),
        "audio_url": AUDIO,
        "tags": ["product", "roadmap", "planning"],
        "participants": [
            {"name": "Sarah Chen", "email": "sarah@acme.io", "role": "Product Lead"},
            {"name": "Miguel Torres", "email": "miguel@acme.io", "role": "Engineering Manager"},
            {"name": "Priya Nair", "email": "priya@acme.io", "role": "Design Lead"},
        ],
        "transcript": [
            ("Sarah Chen", 0, "Welcome everyone to our Q3 roadmap planning session. Our main goal today is to align on the top three priorities for the quarter."),
            ("Miguel Torres", 9000, "Thanks Sarah. From engineering, the biggest theme is platform stability. We need to reduce our P1 incident rate before we add major features."),
            ("Priya Nair", 19000, "On the design side, the onboarding redesign is ready for handoff. We saw a forty percent drop-off in the current flow."),
            ("Sarah Chen", 29000, "That onboarding number is concerning. Let's make the onboarding redesign a top priority for Q3."),
            ("Miguel Torres", 38000, "I will put together a stability roadmap with concrete SLO targets by Friday."),
            ("Priya Nair", 47000, "We need to schedule usability testing for the new onboarding flow next week."),
            ("Sarah Chen", 56000, "Great. The third priority should be the analytics dashboard that customers keep requesting."),
            ("Miguel Torres", 65000, "Agreed. I'll scope the analytics dashboard work and share estimates by end of week."),
            ("Sarah Chen", 74000, "Perfect. Let's follow up on these in our sync on Monday. Thanks everyone."),
        ],
        "summary": (
            "The team aligned on three priorities for Q3: improving platform stability "
            "by reducing the P1 incident rate, shipping the onboarding redesign to address "
            "a 40% drop-off, and building the customer-requested analytics dashboard. "
            "Engineering will define SLO targets and scope the dashboard, while design will "
            "run usability testing on the new onboarding flow."
        ),
        "topics": [("Roadmap goals", 0), ("Platform stability", 9000), ("Onboarding redesign", 19000), ("Analytics dashboard", 56000)],
        "action_items": [
            {"text": "Put together a stability roadmap with concrete SLO targets.", "assignee": "Miguel Torres", "due_date": "by Friday"},
            {"text": "Schedule usability testing for the new onboarding flow.", "assignee": "Priya Nair", "due_date": "next week"},
            {"text": "Scope the analytics dashboard work and share estimates.", "assignee": "Miguel Torres", "due_date": "by end of week"},
        ],
    },
    {
        "title": "Engineering Daily Standup",
        "description": "Quick sync on yesterday's progress and today's plan.",
        "date": _now - timedelta(hours=5),
        "audio_url": AUDIO2,
        "tags": ["engineering", "standup"],
        "participants": [
            {"name": "Miguel Torres", "email": "miguel@acme.io", "role": "Engineering Manager"},
            {"name": "Dev Patel", "email": "dev@acme.io", "role": "Backend Engineer"},
            {"name": "Anna Kowalski", "email": "anna@acme.io", "role": "Frontend Engineer"},
        ],
        "transcript": [
            ("Miguel Torres", 0, "Morning everyone, let's keep this quick. Dev, want to start?"),
            ("Dev Patel", 5000, "Yesterday I finished the payments API refactor. Today I'll start on the webhook retry logic."),
            ("Anna Kowalski", 13000, "I shipped the new settings page. I'm blocked on the design tokens for dark mode though."),
            ("Miguel Torres", 21000, "I'll get you the design tokens this morning. Anything else blocking?"),
            ("Anna Kowalski", 28000, "No, that's the only blocker. Once I have tokens I can finish dark mode today."),
            ("Dev Patel", 35000, "One heads up, the staging database was slow last night. We need to investigate the query performance."),
            ("Miguel Torres", 43000, "Good catch. Dev, can you take care of profiling the slow queries after the webhook work?"),
            ("Dev Patel", 51000, "Will do. I'll add it to my list for this afternoon."),
        ],
        "summary": (
            "Dev completed the payments API refactor and will move on to webhook retry logic "
            "and profiling slow staging queries. Anna shipped the settings page and is only "
            "blocked on dark-mode design tokens, which Miguel will deliver this morning so she "
            "can finish dark mode today."
        ),
        "topics": [("Standup kickoff", 0), ("Payments API", 5000), ("Dark mode blocker", 13000), ("Database performance", 35000)],
        "action_items": [
            {"text": "Deliver dark-mode design tokens to Anna.", "assignee": "Miguel Torres", "due_date": "today"},
            {"text": "Finish dark mode implementation once tokens are available.", "assignee": "Anna Kowalski", "due_date": "today", "completed": False},
            {"text": "Profile and investigate slow staging database queries.", "assignee": "Dev Patel", "due_date": "today"},
        ],
    },
    {
        "title": "Acme Corp Customer Discovery Call",
        "description": "Discovery call with a prospective enterprise customer.",
        "date": _now - timedelta(days=2, hours=1),
        "audio_url": AUDIO,
        "tags": ["sales", "customer", "discovery"],
        "participants": [
            {"name": "Jordan Lee", "email": "jordan@acme.io", "role": "Account Executive"},
            {"name": "Rachel Kim", "email": "rachel@bigco.com", "role": "VP of Operations"},
            {"name": "Tom Becker", "email": "tom@bigco.com", "role": "IT Director"},
        ],
        "transcript": [
            ("Jordan Lee", 0, "Thanks for taking the time today. I'd love to understand your current meeting workflow and where the pain points are."),
            ("Rachel Kim", 9000, "Sure. Our biggest issue is that meeting notes are scattered and action items get lost. Nothing is searchable."),
            ("Tom Becker", 18000, "From an IT perspective, we also need strong security and SSO support before we can roll anything out."),
            ("Jordan Lee", 27000, "That makes sense. Searchable transcripts and automated action items are core to our platform, and we support SSO."),
            ("Rachel Kim", 36000, "That sounds promising. How long does a typical rollout take for a team of two hundred people?"),
            ("Jordan Lee", 45000, "Usually two to three weeks. I will send you a detailed rollout plan and a security overview by Monday."),
            ("Tom Becker", 54000, "Great. We need to review the security overview with our compliance team before moving forward."),
            ("Rachel Kim", 62000, "Let's schedule a follow up demo with the wider operations team next week."),
        ],
        "summary": (
            "BigCo's key pain points are scattered, unsearchable meeting notes and lost action "
            "items, with IT requiring strong security and SSO before rollout. Acme's searchable "
            "transcripts, automated action items, and SSO support map well to these needs. Next "
            "steps are a rollout plan and security overview for compliance review, plus a follow-up "
            "demo with the wider operations team."
        ),
        "topics": [("Current pain points", 9000), ("Security & SSO", 18000), ("Rollout timeline", 36000), ("Next steps", 54000)],
        "action_items": [
            {"text": "Send a detailed rollout plan and security overview to BigCo.", "assignee": "Jordan Lee", "due_date": "by Monday"},
            {"text": "Review the security overview with the compliance team.", "assignee": "Tom Becker", "due_date": "next week"},
            {"text": "Schedule a follow-up demo with the wider operations team.", "assignee": "Jordan Lee", "due_date": "next week"},
        ],
    },
    {
        "title": "Weekly 1:1 — Sarah & Dev",
        "description": "Manager and report weekly check-in.",
        "date": _now - timedelta(days=3, hours=2),
        "audio_url": AUDIO2,
        "tags": ["1-on-1", "people"],
        "participants": [
            {"name": "Sarah Chen", "email": "sarah@acme.io", "role": "Product Lead"},
            {"name": "Dev Patel", "email": "dev@acme.io", "role": "Backend Engineer"},
        ],
        "transcript": [
            ("Sarah Chen", 0, "Hey Dev, how's the week going? Anything on your mind?"),
            ("Dev Patel", 4000, "Pretty good. The payments work is satisfying, but I'd like more clarity on career growth and the path to senior."),
            ("Sarah Chen", 13000, "That's a fair ask. Let's define a concrete growth plan with clear milestones for the senior promotion."),
            ("Dev Patel", 22000, "That would help a lot. I'd also like to take on more system design work."),
            ("Sarah Chen", 30000, "Absolutely. I'll connect you with Miguel to own the design of the new notifications service."),
            ("Dev Patel", 38000, "Awesome, that sounds like a great stretch project."),
            ("Sarah Chen", 44000, "Great. I will draft the growth plan and we can review it together next week."),
        ],
        "summary": (
            "Dev is enjoying the payments work but wants clearer career growth and a defined path "
            "to senior, along with more system-design responsibility. Sarah agreed to draft a "
            "growth plan with milestones and to connect Dev with Miguel to own the design of the "
            "new notifications service as a stretch project."
        ),
        "topics": [("Check-in", 0), ("Career growth", 4000), ("System design opportunities", 22000), ("Growth plan", 44000)],
        "action_items": [
            {"text": "Draft a growth plan with milestones for the senior promotion.", "assignee": "Sarah Chen", "due_date": "next week"},
            {"text": "Connect Dev with Miguel to own the notifications service design.", "assignee": "Sarah Chen", "due_date": ""},
        ],
    },
    {
        "title": "Sprint 14 Retrospective",
        "description": "What went well, what didn't, and improvements for next sprint.",
        "date": _now - timedelta(days=4),
        "audio_url": AUDIO,
        "tags": ["engineering", "retro", "agile"],
        "participants": [
            {"name": "Miguel Torres", "email": "miguel@acme.io", "role": "Engineering Manager"},
            {"name": "Dev Patel", "email": "dev@acme.io", "role": "Backend Engineer"},
            {"name": "Anna Kowalski", "email": "anna@acme.io", "role": "Frontend Engineer"},
            {"name": "Priya Nair", "email": "priya@acme.io", "role": "Design Lead"},
        ],
        "transcript": [
            ("Miguel Torres", 0, "Let's run our sprint 14 retro. Start with what went well."),
            ("Anna Kowalski", 5000, "The new component library really sped up frontend work. We shipped two features ahead of schedule."),
            ("Dev Patel", 14000, "Agreed. Pairing on the payments refactor caught a lot of bugs early."),
            ("Priya Nair", 22000, "What didn't go well was that design handoffs were late, which blocked engineering a couple of times."),
            ("Miguel Torres", 31000, "That's a recurring theme. We need to tighten the design handoff process."),
            ("Priya Nair", 39000, "I will create a design handoff checklist and share it before the next sprint."),
            ("Dev Patel", 47000, "We also had too many context switches. Let's reduce mid-sprint scope changes."),
            ("Miguel Torres", 55000, "Good point. I'll talk to product about freezing scope once the sprint starts."),
        ],
        "summary": (
            "Sprint 14 went well thanks to the new component library, which accelerated frontend "
            "delivery, and pairing on the payments refactor, which caught bugs early. The main "
            "problems were late design handoffs and frequent mid-sprint scope changes. The team "
            "agreed to introduce a design handoff checklist and to freeze scope once a sprint begins."
        ),
        "topics": [("What went well", 5000), ("Component library wins", 5000), ("Design handoff issues", 22000), ("Scope changes", 47000)],
        "action_items": [
            {"text": "Create a design handoff checklist and share before next sprint.", "assignee": "Priya Nair", "due_date": "next week"},
            {"text": "Talk to product about freezing scope once the sprint starts.", "assignee": "Miguel Torres", "due_date": ""},
        ],
    },
]


def seed_if_empty(db: Session) -> bool:
    """Seed only when there are no meetings. Returns True if seeding ran."""
    if db.query(models.Meeting).count() > 0:
        return False
    tag_cache: dict[str, models.Tag] = {}
    for spec in MEETINGS:
        db.add(_build_meeting(spec, tag_cache))
    db.commit()
    return True


def reset_and_seed(db: Session) -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    tag_cache: dict[str, models.Tag] = {}
    for spec in MEETINGS:
        db.add(_build_meeting(spec, tag_cache))
    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if "--reset" in sys.argv:
            reset_and_seed(db)
            print(f"Reset and seeded {len(MEETINGS)} meetings.")
        else:
            seeded = seed_if_empty(db)
            print(f"Seeded {len(MEETINGS)} meetings." if seeded else "Database already has meetings; skipping.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
