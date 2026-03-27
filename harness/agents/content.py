"""
Layer 3 — Platform Mini Apps

Generates platform-native content for TikTok, Instagram, Facebook,
LinkedIn, YouTube, Fiverr, and X. Each platform gets its own
specialist prompt section.
"""

from .base import stream_response, build_profile_context

PLATFORMS = ["TikTok", "Instagram", "Facebook", "LinkedIn", "YouTube", "Fiverr", "X"]

PLATFORM_SPECS = {
    "TikTok": """TIKTOK CONTENT:
- Hook (first 3 seconds — must stop the scroll, one punchy line)
- Script (fast-paced, 30-60 seconds, punchy delivery)
- Trending audio suggestion (genre/style, not a specific song)
- On-screen text overlay copy (3-5 words max per overlay)
- Caption (under 150 chars)
- Hashtag set (8-10 tags, mix of niche and broad)""",

    "Instagram": """INSTAGRAM CONTENT:
- Reel concept and script (30-60 seconds, hook in first 2 seconds)
- Carousel post (5 slides — title, slides 2-4 as key points, slide 5 as CTA)
- Static post caption (story-led, 100-200 words)
- Story sequence (3 frames: hook / content / CTA)
- Hashtag set (10-15 tags)
- Call-to-action""",

    "Facebook": """FACEBOOK CONTENT:
- Full post copy (warm, community-focused, shareable, 150-300 words)
- Group post variation (slightly more conversational)
- Comment prompt to drive engagement (a question at the end)
- Optional: event description if content is calendar-based""",

    "LinkedIn": """LINKEDIN CONTENT:
- Hook line (first sentence must stop the scroll)
- Long-form post (thought leadership angle, 200-350 words)
- Key insight formatted for a professional audience
- Hashtag set (3-5 professional tags)
- Call-to-action (connect / comment / DM)""",

    "YouTube": """YOUTUBE CONTENT:
- Video title (SEO-optimised, under 70 characters)
- Thumbnail text concept (5-7 words max, high contrast)
- Full video script (structured: Hook 0-30s / Context 30-90s / Core Content 90s-end / CTA)
- Description copy with keywords (200-300 words)
- Chapter markers (with timestamps as placeholders)
- End screen CTA""",

    "Fiverr": """FIVERR CONTENT:
- Gig title (credibility-led, keyword-rich, under 80 characters)
- Gig description (service-focused, results-oriented, 200-300 words)
- FAQ section (4 questions with answers)
- Package names and 1-line descriptions (Basic / Standard / Premium)
- Profile tagline (under 120 characters)""",

    "X": """X / TWITTER CONTENT:
- Single punchy tweet (under 280 characters, designed to spark engagement)
- Thread (6-8 tweets — each one standalone but building on the last)
- Reply hook variation (short, designed to start a conversation)""",
}


def build_content_system(profile: dict, mood: str, intake_summary: str, platforms: list) -> str:
    profile_ctx = build_profile_context(profile, mood)

    platform_instructions = "\n\n".join(
        PLATFORM_SPECS[p] for p in platforms if p in PLATFORM_SPECS
    )

    return f"""You are the Platform Content Engine — a specialist in native content creation across social platforms.

{profile_ctx}

CONTENT CONTEXT (from The Brain):
{intake_summary}

YOUR ROLE:
Transform the raw material and context above into platform-native content. Every piece must feel like it could ONLY come from this specific creator — their archetype, their voice, their mood today.

Apply these rules to EVERY piece:
- The archetype shapes the angle and energy
- The language style shapes the vocabulary and register
- The tone shapes the delivery approach
- The mood bends everything — same archetype, different energy today

NEVER produce generic content. If something could belong to anyone, rewrite it. Push the voice harder. Make it more them.

PLATFORMS REQUESTED:
{platform_instructions}

FORMAT: Label each section clearly by platform. Separate platforms with a divider line (---).
Make every piece feel native to its platform — not the same post reformatted."""


def run_content_generation(
    intake_summary: str,
    platforms: list,
    profile: dict,
    mood: str,
    raw_material: str = "",
) -> str:
    system = build_content_system(profile, mood, intake_summary, platforms)

    user_content = f"Generate content for: {', '.join(platforms)}"
    if raw_material:
        user_content += f"\n\nRaw material: {raw_material}"

    messages = [{"role": "user", "content": user_content}]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=6000):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full
