"""
Layers 2.5 + 6.5 — Personal Creative Analytics + Audience Engagement Intelligence

2.5: Reflects the creator's own creative patterns back to them.
6.5: Business intelligence — what's converting, which platforms are winning.
"""

from .base import stream_response, build_profile_context

CREATIVE_ANALYTICS_SYSTEM = """You are the Personal Creative Analytics engine.

YOUR ROLE:
Reflect the creator's own creative patterns back to them. Be honest, insightful, and specific.

Analyse the data provided and surface:
- When they're most productive (days, sessions)
- What content types they gravitate toward
- How their mood correlates to output (which moods produce the most/best content)
- How their archetype expression is evolving
- Any creative peaks or slumps worth noting

Tone: like a smart friend who has been watching your work and has something real to say.
Not generic. Not fluffy. Pattern-specific and actionable."""


AUDIENCE_INTELLIGENCE_SYSTEM = """You are the Audience Engagement Intelligence engine.

YOUR ROLE:
Analyse the engagement data and feed back strategic intelligence. No fluff. Actionable only.

Surface:
- Which platforms are performing and why
- Which content types are resonating most
- Audience behaviour patterns (what makes them engage, save, share, DM)
- Which story chapters or themes are connecting
- Where the conversion opportunity actually is
- Where to double down and where to strengthen

Format as:
PLATFORM PERFORMANCE: [ranked list with brief reasoning]
TOP CONTENT TYPES: [what's working]
KEY INSIGHT: [the most important thing to act on right now]
RECOMMENDED NEXT MOVE: [one specific strategic action]"""


def run_creative_analytics(snapshot: dict, profile: dict, mood: str) -> str:
    profile_ctx = build_profile_context(profile, mood)
    system = CREATIVE_ANALYTICS_SYSTEM + f"\n\n{profile_ctx}"

    data_summary = (
        f"Total sessions: {snapshot['total_sessions']}\n"
        f"Total content generated: {snapshot['total_content_generated']}\n"
        f"Platform counts: {snapshot['platform_counts']}\n"
        f"Content type counts: {snapshot['content_type_counts']}\n"
        f"Mood distribution: {snapshot['mood_distribution']}\n"
        f"Active days: {snapshot['active_days']}"
    )
    messages = [{"role": "user", "content": f"Here is my creative data:\n\n{data_summary}\n\nWhat do you see?"}]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=1000):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full


def run_audience_intelligence(engagement_data: dict, content_data: list, profile: dict) -> str:
    profile_ctx = build_profile_context(profile)
    system = AUDIENCE_INTELLIGENCE_SYSTEM + f"\n\n{profile_ctx}"

    eng_summary = (
        f"Total people tracked: {engagement_data.get('total_tracked', 0)}\n"
        f"High intent (15+ points): {engagement_data.get('high_intent_count', 0)}\n"
        f"Total interactions logged: {engagement_data.get('total_interactions', 0)}"
    )

    platform_breakdown: dict = {}
    for item in content_data:
        p = item.get("platform", "unknown")
        platform_breakdown[p] = platform_breakdown.get(p, 0) + 1

    messages = [
        {
            "role": "user",
            "content": (
                f"Engagement summary:\n{eng_summary}\n\n"
                f"Platform content breakdown: {platform_breakdown}\n\n"
                f"Give me your intelligence report."
            ),
        }
    ]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=1000):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full
