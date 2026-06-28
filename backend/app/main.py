"""FastAPI application factory."""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import action_items, meetings, search


def create_app() -> FastAPI:
    app = FastAPI(title="Fireflies Clone API", version="1.0.0")

    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = "/api"
    app.include_router(meetings.router, prefix=api_prefix)
    app.include_router(action_items.router, prefix=api_prefix)
    app.include_router(search.router, prefix=api_prefix)

    @app.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @app.on_event("startup")
    def _startup():
        Base.metadata.create_all(bind=engine)
        if os.getenv("AUTO_SEED", "1") == "1":
            from .seed import seed_if_empty

            db = SessionLocal()
            try:
                seed_if_empty(db)
            finally:
                db.close()

    return app


app = create_app()
