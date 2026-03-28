"""Router: Layer 5 — Live Response Engine endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ..layers.layer5_response import generate_response, parse_interaction_intent
from ..models.content import Platform
from ..models.personality import PersonalityProfile

router = APIRouter(prefix="/response", tags=["response"])


class ResponseRequest(BaseModel):
    comment: str
    platform: Platform
    profile: PersonalityProfile
    post_context: str = ""


class IntentRequest(BaseModel):
    comment: str


@router.post("/generate", response_model=dict)
def generate_comment_response(request: ResponseRequest) -> dict:
    """Generate a 3-step archetype response to a comment or DM."""
    intent = parse_interaction_intent(request.comment)
    response_text = generate_response(
        comment=request.comment,
        platform=request.platform,
        profile=request.profile,
        post_context=request.post_context,
    )
    return {
        "response": response_text,
        "intent_detected": intent,
        "platform": request.platform.value,
        "archetype": request.profile.archetype.value,
    }


@router.post("/intent", response_model=dict)
def get_intent(request: IntentRequest) -> dict:
    """Parse the intent of an incoming comment or DM."""
    intent = parse_interaction_intent(request.comment)
    return {"comment": request.comment, "intent": intent}
