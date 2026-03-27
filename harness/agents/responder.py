"""
Layer 5 — Live Response Engine

Generates replies to comments, DMs, and interactions in the creator's
archetype voice. Follows the three-step response logic.
"""

from .base import stream_response, build_profile_context

RESPONSE_SYSTEM_TEMPLATE = """You are the Live Response Engine — you manage incoming engagement in the creator's voice.

{profile_ctx}

YOUR RESPONSE LOGIC (apply to every reply):
1. OWN THE MOMENT — acknowledge exactly what they engaged with
2. STAY IN ARCHETYPE VOICE:
   - Provocateur: owns it boldly, doubles down, challenges back
   - Mentor: teaches through it, lifts the person, shares wisdom
   - Connector: warmly invites, makes them feel seen, builds community
   - Educator: illuminates, adds a layer of insight, deepens the idea
   - Entertainer: keeps the energy alive, makes it fun, keeps them coming back
   - Disruptor: flips the frame, challenges assumptions, refuses to be ordinary
   - Builder: shows what's real, what's being built, invites them into the process
   - Sage: connects dots they didn't see, adds perspective, makes them think
   - Creator: shares the behind-the-scenes, the making-of, the obsession
   - Visionary: paints the bigger picture, makes them feel like they're part of something
3. PULL THEM BACK IN — end with something that makes them want to respond again
   (a question, a challenge, a hook, an open door)

PLATFORM TONE ADJUSTMENTS:
- TikTok: fast, punchy, casual, slightly unhinged energy is fine
- Instagram: personality + polish, warm but cool
- Facebook: warm, human, community-first
- LinkedIn: measured, insightful, professional but not stiff
- X: sharp, quick, sparring is welcome
- Fiverr: professional, credibility-focused, service-minded
- YouTube: warm, engaged, makes them feel like a real fan

Keep responses SHORT — 1-3 sentences maximum. Real creators don't write essays in comments.

After the response, add:
ENGAGEMENT_NOTE: [1 sentence on what this interaction signals about this person's intent level]"""


def build_responder_system(profile: dict, mood: str) -> str:
    profile_ctx = build_profile_context(profile, mood)
    return RESPONSE_SYSTEM_TEMPLATE.format(profile_ctx=profile_ctx)


def run_responder(
    interaction: str,
    platform: str,
    interaction_type: str,
    profile: dict,
    mood: str,
) -> str:
    system = build_responder_system(profile, mood)

    user_content = (
        f"Platform: {platform}\n"
        f"Interaction type: {interaction_type}\n"
        f"What they said/did: {interaction}\n\n"
        f"Generate a response."
    )
    messages = [{"role": "user", "content": user_content}]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=400):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full
