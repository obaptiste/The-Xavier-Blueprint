"""Router: Layer 2 — The Brain endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..layers.layer2_brain import (
    build_story_context,
    generate_intake_questions,
    ingest_content,
    route_content,
)
from ..models.content import BrainSession, ContentUpload, IntakeAnswer, Platform

router = APIRouter(prefix="/brain", tags=["brain"])

_SESSIONS: dict[str, BrainSession] = {}


class SessionCreateRequest(BaseModel):
    user_id: str


class AnswersSubmission(BaseModel):
    answers: list[IntakeAnswer]


class RouteRequest(BaseModel):
    session_id: str
    platforms: list[Platform]


@router.post("/session", response_model=BrainSession)
def create_session(request: SessionCreateRequest) -> BrainSession:
    """Create a new Brain session for a creator."""
    session = BrainSession(user_id=request.user_id)
    _SESSIONS[session.id] = session
    return session


@router.post("/upload", response_model=BrainSession)
def upload_content(upload: ContentUpload, session_id: str) -> BrainSession:
    """Upload content to an existing Brain session."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    updated = ingest_content(upload, session)
    _SESSIONS[session_id] = updated
    return updated


@router.get("/session/{session_id}/questions", response_model=list[str])
def get_intake_questions(session_id: str) -> list[str]:
    """Get adaptive intake questions for the current session."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    if not session.uploads:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one piece of content before generating intake questions.",
        )
    return generate_intake_questions(session.uploads[-1], session)


@router.post("/session/{session_id}/answers", response_model=BrainSession)
def submit_answers(session_id: str, submission: AnswersSubmission) -> BrainSession:
    """Submit intake answers and update the session's story context."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    updated_answers = session.intake_answers + submission.answers
    updated_session = session.model_copy(update={"intake_answers": updated_answers})
    updated_session = updated_session.model_copy(
        update={"current_story_context": build_story_context(updated_session)}
    )
    _SESSIONS[session_id] = updated_session
    return updated_session


@router.get("/session/{session_id}/context", response_model=dict)
def get_story_context(session_id: str) -> dict:
    """Get the current story context for a session."""
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"session_id": session_id, "context": session.current_story_context}
