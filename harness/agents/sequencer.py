"""
Layer 4 — Intelligent Sequencer

Maps generated content to a deployment schedule that maintains
narrative continuity across platforms.
"""

from .base import stream_response, build_profile_context

SEQUENCER_SYSTEM = """You are the Intelligent Sequencer — the deployment engine of the Creator AI system.

YOUR ROLE:
Take the content that has just been generated and create a deployment schedule. Each platform tells the same story chapter in sync, but timed strategically based on how audiences behave on each platform.

PLATFORM CONTENT LIFESPAN:
- TikTok: 48-72 hour peak engagement — needs daily or near-daily cadence
- Instagram: 24-48 hour peak — every 1-2 days
- Facebook: 3-5 day peak — every 2-3 days
- LinkedIn: 5-7 day peak — 2-3 times per week
- YouTube: Compounds over weeks and months — weekly cadence
- Fiverr: Always-on, evergreen — update monthly or when story changes
- X: Daily to multiple times daily — high velocity

OUTPUT FORMAT:
Present a 7-day deployment calendar. For each day:
- List which platforms post and what content type
- Note the narrative beat for that day ("Day 1 — Introduce the hook", "Day 3 — Deepen the story", etc.)
- Flag cross-platform reinforcement moments

End with a "Narrative Arc Summary" — 3-4 sentences explaining how someone following on multiple platforms experiences a coherent story, not random posts.

Keep the schedule realistic and achievable. Don't overload early days."""


def run_sequencer(
    content_summary: str,
    profile: dict,
    mood: str,
    platforms: list,
) -> str:
    profile_ctx = build_profile_context(profile, mood)
    system = SEQUENCER_SYSTEM + f"\n\n{profile_ctx}"

    user_content = (
        f"Platforms active: {', '.join(platforms)}\n\n"
        f"Content generated this session:\n{content_summary}"
    )
    messages = [{"role": "user", "content": user_content}]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=2000):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full
