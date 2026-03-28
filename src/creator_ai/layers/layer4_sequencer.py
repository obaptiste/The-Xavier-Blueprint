"""Layer 4 — Intelligent Sequencer: schedule content for narrative-synced deployment."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..models.content import GeneratedContent, Platform

# ---------------------------------------------------------------------------
# Platform cadence data
# ---------------------------------------------------------------------------

PLATFORM_CADENCE: dict[Platform, dict] = {
    Platform.TIKTOK: {
        "frequency_per_week": 7,
        "peak_hours": [8, 12, 19],
        "lifespan_hours": 72,
    },
    Platform.INSTAGRAM: {
        "frequency_per_week": 5,
        "peak_hours": [8, 11, 17, 21],
        "lifespan_hours": 48,
    },
    Platform.FACEBOOK: {
        "frequency_per_week": 3,
        "peak_hours": [9, 13, 20],
        "lifespan_hours": 120,
    },
    Platform.LINKEDIN: {
        "frequency_per_week": 2,
        "peak_hours": [8, 12, 17],
        "lifespan_hours": 168,
    },
    Platform.YOUTUBE: {
        "frequency_per_week": 1,
        "peak_hours": [14, 15, 16],
        "lifespan_hours": 9999,
    },
    Platform.FIVERR: {
        "frequency_per_week": 1,
        "peak_hours": [9, 10, 11],
        "lifespan_hours": 9999,
    },
    Platform.X: {
        "frequency_per_week": 7,
        "peak_hours": [8, 12, 17, 21],
        "lifespan_hours": 48,
    },
}

# Narrative deployment order: build story arc from awareness → conversion
_NARRATIVE_ORDER: list[Platform] = [
    Platform.TIKTOK,      # awareness — widest reach, highest velocity
    Platform.INSTAGRAM,   # engagement — aesthetic, saves, DMs
    Platform.X,           # discourse — thread conversation, amplification
    Platform.FACEBOOK,    # community — shares, longer shelf life
    Platform.LINKEDIN,    # authority — professional credibility
    Platform.YOUTUBE,     # depth — long-form trust building
    Platform.FIVERR,      # conversion — high-intent inbound
]

_NARRATIVE_DELAY_HOURS: dict[Platform, int] = {
    Platform.TIKTOK: 0,
    Platform.INSTAGRAM: 2,
    Platform.X: 4,
    Platform.FACEBOOK: 6,
    Platform.LINKEDIN: 24,
    Platform.YOUTUBE: 48,
    Platform.FIVERR: 72,
}


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def calculate_optimal_schedule(
    platform: Platform,
    reference_datetime: datetime,
    content_count: int = 1,
) -> list[datetime]:
    """Return optimal posting datetimes for a platform given a reference datetime."""
    cadence = PLATFORM_CADENCE.get(platform, PLATFORM_CADENCE[Platform.X])
    peak_hours: list[int] = cadence["peak_hours"]
    freq_per_week: int = cadence["frequency_per_week"]

    ref = reference_datetime
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)

    results: list[datetime] = []
    day_offset = 0
    posts_per_week = freq_per_week

    while len(results) < content_count:
        candidate_date = ref + timedelta(days=day_offset)
        for hour in peak_hours:
            if len(results) >= content_count:
                break
            candidate = candidate_date.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            if candidate > ref:
                results.append(candidate)

        day_offset += max(1, 7 // posts_per_week)

    return results[:content_count]


def schedule_content(
    generated_items: list[GeneratedContent],
    start_datetime: datetime,
    narrative_sync: bool = True,
) -> list[GeneratedContent]:
    """Assign scheduled_at datetimes to each piece of content for deployment.

    With narrative_sync=True the content is spread across platforms following
    the awareness → engagement → authority → conversion arc, with platform-
    appropriate delays and peak-hour alignment.
    """
    if not generated_items:
        return []

    ref = start_datetime
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)

    scheduled: list[GeneratedContent] = []

    if narrative_sync:
        platform_counters: dict[Platform, int] = {}
        for item in generated_items:
            delay_hours = _NARRATIVE_DELAY_HOURS.get(item.platform, 0)
            base_time = ref + timedelta(hours=delay_hours)

            count = platform_counters.get(item.platform, 0)
            optimal_times = calculate_optimal_schedule(item.platform, base_time, count + 1)
            post_time = optimal_times[count] if optimal_times else base_time

            platform_counters[item.platform] = count + 1
            scheduled.append(item.model_copy(update={"scheduled_at": post_time}))
    else:
        platform_counters = {}
        for item in generated_items:
            count = platform_counters.get(item.platform, 0)
            optimal_times = calculate_optimal_schedule(item.platform, ref, count + 1)
            post_time = optimal_times[count] if optimal_times else ref + timedelta(hours=count)
            platform_counters[item.platform] = count + 1
            scheduled.append(item.model_copy(update={"scheduled_at": post_time}))

    return scheduled
