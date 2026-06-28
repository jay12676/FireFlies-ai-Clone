"""Database operations — the only layer that touches the ORM directly."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from . import models, schemas
from .services import generator, parser

DEFAULT_AUDIO = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"


# ---------- Tags ----------
def _get_or_create_tags(db: Session, names: list[str]) -> list[models.Tag]:
    tags: list[models.Tag] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        tag = db.scalar(select(models.Tag).where(models.Tag.name == name))
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


# ---------- Transcript + generation ----------
def _apply_transcript(db: Session, meeting: models.Meeting, content: str, filename: str) -> None:
    """Parse a transcript, replace segments, and regenerate summary/topics/actions."""
    segments = parser.parse_transcript(content, filename)

    meeting.segments.clear()
    meeting.topics.clear()
    if meeting.summary:
        db.delete(meeting.summary)
        meeting.summary = None
    # Drop only auto-generated action items? We replace all on transcript upload.
    meeting.action_items.clear()
    db.flush()

    for i, seg in enumerate(segments):
        meeting.segments.append(
            models.TranscriptSegment(
                speaker=seg.speaker, start_ms=seg.start_ms, end_ms=seg.end_ms,
                text=seg.text, order_index=i,
            )
        )
    if segments and not meeting.duration_seconds:
        meeting.duration_seconds = max(s.end_ms for s in segments) // 1000

    content_gen = generator.generate_all(segments)
    meeting.summary = models.Summary(overview=content_gen.overview, generated_by="rule")
    for i, topic in enumerate(content_gen.topics):
        meeting.topics.append(
            models.KeyTopic(title=topic.title, start_ms=topic.start_ms, order_index=i)
        )
    for i, item in enumerate(content_gen.action_items):
        meeting.action_items.append(
            models.ActionItem(
                text=item.text, assignee=item.assignee, due_date=item.due_date, order_index=i
            )
        )


# ---------- Meetings ----------
def list_meetings(
    db: Session,
    search: str | None = None,
    participant: str | None = None,
    tag: str | None = None,
    sort: str = "recent",
) -> list[models.Meeting]:
    stmt = select(models.Meeting).options(
        selectinload(models.Meeting.participants),
        selectinload(models.Meeting.tags),
        selectinload(models.Meeting.action_items),
    )
    if search:
        stmt = stmt.where(models.Meeting.title.ilike(f"%{search}%"))
    if participant:
        stmt = stmt.where(
            models.Meeting.participants.any(models.Participant.name.ilike(f"%{participant}%"))
        )
    if tag:
        stmt = stmt.where(models.Meeting.tags.any(models.Tag.name.ilike(f"%{tag}%")))

    if sort == "oldest":
        stmt = stmt.order_by(models.Meeting.date.asc())
    elif sort == "title":
        stmt = stmt.order_by(models.Meeting.title.asc())
    else:  # recent (default)
        stmt = stmt.order_by(models.Meeting.date.desc())
    return list(db.scalars(stmt).unique())


def get_meeting(db: Session, meeting_id: int) -> models.Meeting | None:
    return db.scalar(
        select(models.Meeting)
        .where(models.Meeting.id == meeting_id)
        .options(
            selectinload(models.Meeting.participants),
            selectinload(models.Meeting.segments),
            selectinload(models.Meeting.summary),
            selectinload(models.Meeting.topics),
            selectinload(models.Meeting.action_items),
            selectinload(models.Meeting.tags),
        )
    )


def create_meeting(db: Session, payload: schemas.MeetingCreate) -> models.Meeting:
    meeting = models.Meeting(
        title=payload.title,
        description=payload.description,
        date=payload.date or datetime.now(timezone.utc),
        duration_seconds=payload.duration_seconds,
        audio_url=payload.audio_url or DEFAULT_AUDIO,
    )
    meeting.participants = [
        models.Participant(name=p.name, email=p.email, role=p.role) for p in payload.participants
    ]
    meeting.tags = _get_or_create_tags(db, payload.tags)
    db.add(meeting)
    db.flush()

    if payload.transcript_text:
        _apply_transcript(
            db, meeting, payload.transcript_text,
            payload.transcript_filename or "transcript.txt",
        )
    db.commit()
    db.refresh(meeting)
    return get_meeting(db, meeting.id)


def update_meeting(
    db: Session, meeting_id: int, payload: schemas.MeetingUpdate
) -> models.Meeting | None:
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        return None
    data = payload.model_dump(exclude_unset=True)
    if "participants" in data and data["participants"] is not None:
        meeting.participants = [
            models.Participant(name=p["name"], email=p.get("email", ""), role=p.get("role", ""))
            for p in data.pop("participants")
        ]
    else:
        data.pop("participants", None)
    if "tags" in data and data["tags"] is not None:
        meeting.tags = _get_or_create_tags(db, data.pop("tags"))
    else:
        data.pop("tags", None)
    for key, value in data.items():
        setattr(meeting, key, value)
    db.commit()
    return get_meeting(db, meeting_id)


def delete_meeting(db: Session, meeting_id: int) -> bool:
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        return False
    db.delete(meeting)
    db.commit()
    return True


def replace_transcript(
    db: Session, meeting_id: int, content: str, filename: str
) -> models.Meeting | None:
    meeting = get_meeting(db, meeting_id)
    if not meeting:
        return None
    _apply_transcript(db, meeting, content, filename)
    db.commit()
    return get_meeting(db, meeting_id)


# ---------- Action items ----------
def add_action_item(
    db: Session, meeting_id: int, payload: schemas.ActionItemCreate
) -> models.ActionItem | None:
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        return None
    next_index = db.scalar(
        select(func.coalesce(func.max(models.ActionItem.order_index), -1) + 1).where(
            models.ActionItem.meeting_id == meeting_id
        )
    )
    item = models.ActionItem(
        meeting_id=meeting_id, text=payload.text, assignee=payload.assignee,
        due_date=payload.due_date, completed=payload.completed, order_index=next_index or 0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_action_item(
    db: Session, item_id: int, payload: schemas.ActionItemUpdate
) -> models.ActionItem | None:
    item = db.get(models.ActionItem, item_id)
    if not item:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_action_item(db: Session, item_id: int) -> bool:
    item = db.get(models.ActionItem, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


# ---------- Search ----------
def global_search(db: Session, query: str, limit: int = 50) -> list[schemas.SearchHit]:
    if not query.strip():
        return []
    stmt = (
        select(models.TranscriptSegment, models.Meeting.title)
        .join(models.Meeting, models.TranscriptSegment.meeting_id == models.Meeting.id)
        .where(
            or_(
                models.TranscriptSegment.text.ilike(f"%{query}%"),
                models.TranscriptSegment.speaker.ilike(f"%{query}%"),
            )
        )
        .order_by(models.TranscriptSegment.meeting_id, models.TranscriptSegment.order_index)
        .limit(limit)
    )
    hits: list[schemas.SearchHit] = []
    for seg, title in db.execute(stmt):
        hits.append(
            schemas.SearchHit(
                meeting_id=seg.meeting_id, meeting_title=title, segment_id=seg.id,
                speaker=seg.speaker, start_ms=seg.start_ms, text=seg.text,
            )
        )
    return hits
