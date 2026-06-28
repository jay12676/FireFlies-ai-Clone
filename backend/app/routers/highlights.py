"""Standalone highlight (comment/soundbite) update + delete endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.patch("/{highlight_id}", response_model=schemas.HighlightRead)
def update_highlight(
    highlight_id: int, payload: schemas.HighlightUpdate, db: Session = Depends(get_db)
):
    hl = crud.update_highlight(db, highlight_id, payload)
    if not hl:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return hl


@router.delete("/{highlight_id}", status_code=204)
def delete_highlight(highlight_id: int, db: Session = Depends(get_db)):
    if not crud.delete_highlight(db, highlight_id):
        raise HTTPException(status_code=404, detail="Highlight not found")
    return None
