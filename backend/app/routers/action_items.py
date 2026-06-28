"""Standalone action-item update/delete endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.patch("/{item_id}", response_model=schemas.ActionItemRead)
def update_action_item(
    item_id: int, payload: schemas.ActionItemUpdate, db: Session = Depends(get_db)
):
    item = crud.update_action_item(db, item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_action_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_action_item(db, item_id):
        raise HTTPException(status_code=404, detail="Action item not found")
    return None
