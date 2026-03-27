"""Creator AI — Social Media Content Engine. FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import alerts, brain, content, personality, response, sequencer

app = FastAPI(
    title="Creator AI — Social Media Content Engine",
    version="0.1.0",
    description=(
        "A multi-layer AI-powered content engine that builds your personality archetype, "
        "ingests your raw content, generates platform-native posts, schedules intelligently, "
        "responds in your voice, and alerts you to high-intent audience members."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(personality.router)
app.include_router(brain.router)
app.include_router(content.router)
app.include_router(sequencer.router)
app.include_router(response.router)
app.include_router(alerts.router)


@app.get("/health", tags=["meta"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0", "service": "Creator AI"}


@app.get("/", tags=["meta"])
def root() -> dict:
    """Root endpoint — links to docs."""
    return {
        "service": "Creator AI — Social Media Content Engine",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
