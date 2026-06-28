"""Pydantic v2 request/response schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Participants ----------
class ParticipantBase(BaseModel):
    name: str
    email: str = ""
    role: str = ""


class ParticipantRead(_ORM, ParticipantBase):
    id: int


# ---------- Transcript segments ----------
class SegmentBase(BaseModel):
    speaker: str = "Speaker"
    start_ms: int = 0
    end_ms: int = 0
    text: str = ""
    order_index: int = 0


class SegmentRead(_ORM, SegmentBase):
    id: int


# ---------- Summary ----------
class SummaryRead(_ORM):
    id: int
    overview: str
    generated_by: str


# ---------- Topics ----------
class TopicRead(_ORM):
    id: int
    title: str
    start_ms: int
    order_index: int


# ---------- Action items ----------
class ActionItemBase(BaseModel):
    text: str
    assignee: str = "Unassigned"
    due_date: str = ""
    completed: bool = False


class ActionItemCreate(ActionItemBase):
    pass


class ActionItemUpdate(BaseModel):
    text: str | None = None
    assignee: str | None = None
    due_date: str | None = None
    completed: bool | None = None


class ActionItemRead(_ORM, ActionItemBase):
    id: int
    order_index: int


# ---------- Tags ----------
class TagRead(_ORM):
    id: int
    name: str


# ---------- Meetings ----------
class MeetingBase(BaseModel):
    title: str
    description: str = ""
    date: datetime | None = None
    duration_seconds: int = 0
    audio_url: str = ""


class MeetingCreate(MeetingBase):
    participants: list[ParticipantBase] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    # Optional transcript supplied at creation time (pasted or uploaded text).
    transcript_text: str | None = None
    transcript_filename: str | None = None


class MeetingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: datetime | None = None
    duration_seconds: int | None = None
    audio_url: str | None = None
    participants: list[ParticipantBase] | None = None
    tags: list[str] | None = None


class MeetingSummaryRow(_ORM):
    """Compact row used by the library/dashboard list."""
    id: int
    title: str
    date: datetime
    duration_seconds: int
    participants: list[ParticipantRead] = []
    tags: list[TagRead] = []
    action_item_count: int = 0


class MeetingDetail(_ORM):
    id: int
    title: str
    description: str
    date: datetime
    duration_seconds: int
    audio_url: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead] = []
    segments: list[SegmentRead] = []
    summary: SummaryRead | None = None
    topics: list[TopicRead] = []
    action_items: list[ActionItemRead] = []
    tags: list[TagRead] = []


# ---------- Transcript upload ----------
class TranscriptUpload(BaseModel):
    content: str
    filename: str = "transcript.txt"


# ---------- Search ----------
class SearchHit(BaseModel):
    meeting_id: int
    meeting_title: str
    segment_id: int
    speaker: str
    start_ms: int
    text: str


class SearchResponse(BaseModel):
    query: str
    count: int
    hits: list[SearchHit]
