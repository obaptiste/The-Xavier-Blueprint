"""Engagement interaction scoring models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from .content import Platform


def _new_id() -> str:
    return str(uuid.uuid4())


class InteractionType(str, Enum):
    FIVERR_DM = "fiverr_dm"
    LINKEDIN_DM = "linkedin_dm"
    INSTAGRAM_DM = "instagram_dm"
    YOUTUBE_LINK_CLICK = "youtube_link_click"
    INSTAGRAM_SAVE = "instagram_save"
    TIKTOK_DUET_STITCH = "tiktok_duet_stitch"
    FACEBOOK_SHARE = "facebook_share"
    COMMENT_WITH_QUESTION = "comment_with_question"
    STANDARD_COMMENT = "standard_comment"
    LIKE = "like"


INTERACTION_WEIGHTS: dict[InteractionType, float] = {
    InteractionType.FIVERR_DM: 8.0,
    InteractionType.LINKEDIN_DM: 6.0,
    InteractionType.INSTAGRAM_DM: 5.0,
    InteractionType.YOUTUBE_LINK_CLICK: 3.0,
    InteractionType.INSTAGRAM_SAVE: 2.0,
    InteractionType.TIKTOK_DUET_STITCH: 4.0,
    InteractionType.FACEBOOK_SHARE: 3.0,
    InteractionType.COMMENT_WITH_QUESTION: 4.0,
    InteractionType.STANDARD_COMMENT: 1.0,
    InteractionType.LIKE: 0.5,
}

ALERT_THRESHOLD: float = 15.0


class Interaction(BaseModel):
    """A single recorded interaction from a user with a creator's content."""

    id: str = Field(default_factory=_new_id)
    user_id: str
    creator_id: str
    platform: Platform
    interaction_type: InteractionType
    post_id: str = Field(default="")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EngagementScore(BaseModel):
    """Aggregated engagement score for a user–creator pair."""

    user_id: str
    creator_id: str
    total_score: float = Field(default=0.0)
    interactions: list[Interaction] = Field(default_factory=list)
    alert_triggered: bool = Field(default=False)
