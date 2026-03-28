"""Router: Layer 3 — Platform Mini Apps / content generation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..layers.layer3_mini_apps import generate_for_platform
from ..models.content import GeneratedContent, Platform, ContentUpload
from ..models.personality import PersonalityProfile

router = APIRouter(prefix="/content", tags=["content"])

_CONTENT_STORE: dict[str, GeneratedContent] = {}


class GenerateRequest(BaseModel):
    profile: PersonalityProfile
    upload: ContentUpload
    platforms: list[Platform]
    story_context: str = ""


@router.post("/generate", response_model=list[GeneratedContent])
def generate_content(request: GenerateRequest) -> list[GeneratedContent]:
    """Generate platform-ready content for the specified platforms."""
    if not request.platforms:
        raise HTTPException(status_code=422, detail="At least one platform must be specified.")

    results: list[GeneratedContent] = []
    for platform in request.platforms:
        generated = generate_for_platform(
            platform=platform,
            profile=request.profile,
            upload=request.upload,
            story_context=request.story_context,
        )
        _CONTENT_STORE[generated.id] = generated
        results.append(generated)
    return results


@router.get("/{content_id}", response_model=GeneratedContent)
def get_content(content_id: str) -> GeneratedContent:
    """Get generated content by ID."""
    content = _CONTENT_STORE.get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"Content '{content_id}' not found.")
    return content


@router.get("/platforms/list", response_model=list[str])
def list_platforms() -> list[str]:
    """List all available platforms."""
    return [p.value for p in Platform]
