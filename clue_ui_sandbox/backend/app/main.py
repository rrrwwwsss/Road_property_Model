from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from app.api.clues import router as clues_router
from app.api.meta import router as meta_router
from app.api.stats import router as stats_router

app = FastAPI(title="Clue UI Sandbox Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta_router)
app.include_router(clues_router)
app.include_router(stats_router)


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}
