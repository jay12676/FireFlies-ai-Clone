"""SQLAlchemy ORM models for the Fireflies clone.

Schema (see design spec §4):
    Meeting 1─N Participant / TranscriptSegment / KeyTopic / ActionItem
    Meeting 1─1 Summary
    Meeting M─N Tag (via meeting_tags)

All Meeting children cascade-delete when the meeting is removed.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Association table for Meeting <-> Tag many-to-many.
meeting_tags = Table(
    "meeting_tags",
    Base.metadata,
    Column("meeting_id", ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    audio_url: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    participants: Mapped[list["Participant"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan", order_by="Participant.id"
    )
    segments: Mapped[list["TranscriptSegment"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.order_index",
    )
    summary: Mapped["Summary | None"] = relationship(
        back_populates="meeting", cascade="all, delete-orphan", uselist=False
    )
    topics: Mapped[list["KeyTopic"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan", order_by="KeyTopic.order_index"
    )
    action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan", order_by="ActionItem.order_index"
    )
    highlights: Mapped[list["Highlight"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan", order_by="Highlight.start_ms"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=meeting_tags, back_populates="meetings"
    )


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(120), default="")

    meeting: Mapped["Meeting"] = relationship(back_populates="participants")


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    speaker: Mapped[str] = mapped_column(String(200), default="Speaker")
    start_ms: Mapped[int] = mapped_column(Integer, default=0)
    end_ms: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    meeting: Mapped["Meeting"] = relationship(back_populates="segments")


class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = (UniqueConstraint("meeting_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    overview: Mapped[str] = mapped_column(Text, default="")
    generated_by: Mapped[str] = mapped_column(String(20), default="rule")  # 'seed' | 'rule'

    meeting: Mapped["Meeting"] = relationship(back_populates="summary")


class KeyTopic(Base):
    __tablename__ = "key_topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    start_ms: Mapped[int] = mapped_column(Integer, default=0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    meeting: Mapped["Meeting"] = relationship(back_populates="topics")


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    assignee: Mapped[str] = mapped_column(String(200), default="Unassigned")
    due_date: Mapped[str] = mapped_column(String(50), default="")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")


class Highlight(Base):
    """A highlighted transcript segment, optionally with a comment/note.

    Doubles as a "soundbite": it snapshots the quote, speaker, and time range so
    the saved clip survives even if the underlying transcript is later replaced.
    """
    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    segment_id: Mapped[int | None] = mapped_column(
        ForeignKey("transcript_segments.id", ondelete="SET NULL"), nullable=True
    )
    quote: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="")
    speaker: Mapped[str] = mapped_column(String(200), default="")
    color: Mapped[str] = mapped_column(String(20), default="yellow")
    start_ms: Mapped[int] = mapped_column(Integer, default=0)
    end_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    meeting: Mapped["Meeting"] = relationship(back_populates="highlights")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    meetings: Mapped[list["Meeting"]] = relationship(
        secondary=meeting_tags, back_populates="tags"
    )
