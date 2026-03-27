"""Router: Layer 4 — Intelligent Sequencer endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..layers.layer4_sequencer import calculate_optimal_schedule, schedule_content
from ..models.content import GeneratedContent, Platform

router = APIRouter(prefix="/schedule", tags=["sequencer"])


class ScheduleRequest(BaseModel):
    generated_items: list[GeneratedContent]
    start_datetime: datetime
    narrative_sync: bool = True


class OptimalScheduleRequest(BaseModel):
    platform: Platform
    reference_datetime: datetime
    content_count: int = 1


@router.post("", response_model=list[GeneratedContent])
def schedule(request: ScheduleRequest) -> list[GeneratedContent]:
    """Schedule content for deployment with optional narrative synchronisation."""
    if not request.generated_items:
        raise HTTPException(status_code=422, detail="No content items provided.")
    return schedule_content(
        generated_items=request.generated_items,
        start_datetime=request.start_datetime,
        narrative_sync=request.narrative_sync,
    )


@router.get("/optimal", response_model=list[datetime])
def get_optimal_times(
    platform: Platform,
    content_count: int = 1,
) -> list[datetime]:
    """Get optimal posting times for a platform, starting from now."""
    reference = datetime.now(timezone.utc)
    return calculate_optimal_schedule(
        platform=platform,
        reference_datetime=reference,
        content_count=content_count,
    )
