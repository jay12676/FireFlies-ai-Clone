"""Meeting + transcript + action-item endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _to_row(m) -> schemas.MeetingSummaryRow:
    row = schemas.MeetingSummaryRow.model_validate(m)
    row.action_item_count = len(m.action_items)
    return row


@router.get("", response_model=list[schemas.MeetingSummaryRow])
def list_meetings(
    search: str | None = None,
    participant: str | None = None,
    tag: str | None = None,
    sort: str = "recent",
    db: Session = Depends(get_db),
):
    meetings = crud.list_meetings(db, search=search, participant=participant, tag=tag, sort=sort)
    return [_to_row(m) for m in meetings]


@router.post("", response_model=schemas.MeetingDetail, status_code=201)
def create_meeting(payload: schemas.MeetingCreate, db: Session = Depends(get_db)):
    return crud.create_meeting(db, payload)


@router.get("/{meeting_id}", response_model=schemas.MeetingDetail)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.patch("/{meeting_id}", response_model=schemas.MeetingDetail)
def update_meeting(
    meeting_id: int, payload: schemas.MeetingUpdate, db: Session = Depends(get_db)
):
    meeting = crud.update_meeting(db, meeting_id, payload)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    if not crud.delete_meeting(db, meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found")
    return None


@router.post("/{meeting_id}/transcript", response_model=schemas.MeetingDetail)
async def upload_transcript(
    meeting_id: int,
    file: UploadFile | None = File(default=None),
    content: str | None = Form(default=None),
    filename: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    """Accept either a multipart file upload or pasted form text."""
    if file is not None:
        raw = (await file.read()).decode("utf-8", errors="ignore")
        name = file.filename or "transcript.txt"
    elif content is not None:
        raw = content
        name = filename or "transcript.txt"
    else:
        raise HTTPException(status_code=400, detail="Provide a file or content")
    meeting = crud.replace_transcript(db, meeting_id, raw, name)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("/{meeting_id}/action-items", response_model=schemas.ActionItemRead, status_code=201)
def add_action_item(
    meeting_id: int, payload: schemas.ActionItemCreate, db: Session = Depends(get_db)
):
    item = crud.add_action_item(db, meeting_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return item
