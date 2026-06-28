"""Global transcript search endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=schemas.SearchResponse)
def search(q: str = "", db: Session = Depends(get_db)):
    hits = crud.global_search(db, q)
    return schemas.SearchResponse(query=q, count=len(hits), hits=hits)
