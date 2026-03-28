"""Layer 5 — Live Response Engine: generate archetype-voiced responses to comments and DMs."""

from __future__ import annotations

from enum import Enum

from ..models.archetypes import Archetype
from ..models.content import Platform
from ..models.personality import PersonalityProfile

# ---------------------------------------------------------------------------
# Response step enum
# ---------------------------------------------------------------------------


class ResponseStep(str, Enum):
    OWN_THE_MOMENT = "own_the_moment"
    STAY_IN_VOICE = "stay_in_voice"
    PULL_BACK_IN = "pull_back_in"


# ---------------------------------------------------------------------------
# Platform tone modifiers
# ---------------------------------------------------------------------------

PLATFORM_TONE_MODIFIERS: dict[Platform, str] = {
    Platform.TIKTOK: "Keep it short, punchy, and native to the comment section. Use a casual TikTok register.",
    Platform.INSTAGRAM: "Warm and visual. Use emojis naturally. Match the energy of the post.",
    Platform.FACEBOOK: "Community-first. Friendly and conversational. Invite further discussion.",
    Platform.LINKEDIN: "Professional but human. Show thought leadership without being stiff.",
    Platform.YOUTUBE: "Engaged creator talking to a real person. Thank them and add value.",
    Platform.X: "Sharp and direct. Brevity is wit. Don't over-explain.",
    Platform.FIVERR: "Professional, trust-building, conversion-oriented. Be helpful and clear.",
}

# ---------------------------------------------------------------------------
# Intent parsing
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "curiosity": ["how", "what", "why", "where", "when", "can you", "do you", "tell me", "explain"],
    "agreement": ["yes", "exactly", "agree", "same", "totally", "absolutely", "100%", "facts", "true", "this", "preach"],
    "challenge": ["wrong", "disagree", "no", "but", "actually", "not true", "false", "prove", "source"],
    "praise": ["love", "amazing", "great", "best", "incredible", "fire", "🔥", "🙏", "wow", "thank", "goat"],
    "purchase_intent": ["price", "how much", "buy", "hire", "work with", "dm", "services", "book", "available"],
    "share_intent": ["sharing", "shared", "sent this", "tagged", "showed", "forwarded"],
    "emotional": ["cry", "crying", "feel", "felt", "needed this", "resonates", "hit different", "💙", "❤️", "😭"],
}


def parse_interaction_intent(comment: str) -> str:
    """Classify the intent of an incoming comment or DM."""
    lower = comment.lower()
    scores: dict[str, int] = {intent: 0 for intent in _INTENT_KEYWORDS}
    for intent, keywords in _INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                scores[intent] += 1

    top_intent = max(scores, key=lambda k: scores[k])
    if scores[top_intent] == 0:
        return "general_engagement"
    return top_intent


# ---------------------------------------------------------------------------
# Archetype response templates (3-step logic)
# ---------------------------------------------------------------------------

_ARCHETYPE_STEP_TEMPLATES: dict[Archetype, dict[ResponseStep, list[str]]] = {
    Archetype.EDUCATOR: {
        ResponseStep.OWN_THE_MOMENT: [
            "Great question — this is exactly what people need to understand.",
            "You just hit on the most important part of this.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "The key insight here is {core_point}.",
            "To break this down further: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "If you want to go deeper on this, everything you need is in my next post.",
            "There's a full breakdown coming — stay close.",
        ],
    },
    Archetype.ENTERTAINER: {
        ResponseStep.OWN_THE_MOMENT: [
            "OKAY this comment made my whole day 😭",
            "The way you said this is sending me 🙌",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "But for real though — {core_point}.",
            "No but seriously — {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "Follow because I've got something even better coming.",
            "You think THAT was something? Wait for what's next.",
        ],
    },
    Archetype.DISRUPTOR: {
        ResponseStep.OWN_THE_MOMENT: [
            "This is exactly the conversation we need to be having.",
            "You're one of the few actually paying attention.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "Here's what the mainstream version gets wrong: {core_point}.",
            "The honest answer that nobody gives: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "The full argument is coming. Don't look away.",
            "This is part of a bigger picture I'm mapping out.",
        ],
    },
    Archetype.BUILDER: {
        ResponseStep.OWN_THE_MOMENT: [
            "This is a great observation — it comes up in the build all the time.",
            "You're asking exactly the right question.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "From a systems perspective: {core_point}.",
            "Here's how I'd approach this in the build: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "I'm documenting the next phase — follow to see how this plays out.",
            "The full build log addresses this — stay tuned.",
        ],
    },
    Archetype.SAGE: {
        ResponseStep.OWN_THE_MOMENT: [
            "You've touched on something important here.",
            "That's worth sitting with.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "The deeper truth is: {core_point}.",
            "What most people miss about this: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "There's more to explore here. I'll be sharing more soon.",
            "This deserves a longer conversation — follow for that.",
        ],
    },
    Archetype.CREATOR: {
        ResponseStep.OWN_THE_MOMENT: [
            "This means everything — thank you for seeing it 🙏",
            "The fact that this landed for you makes the whole process worth it.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "The thing I was trying to capture was {core_point}.",
            "The intention behind this was {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "Behind-the-scenes of what's coming next is going up soon.",
            "The next piece is already in progress — you'll want to see it.",
        ],
    },
    Archetype.CONNECTOR: {
        ResponseStep.OWN_THE_MOMENT: [
            "This comment is why I do this. Thank you for being here 💙",
            "You just made me feel this whole thing was worth creating.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "What I love about this community is that {core_point}.",
            "This is exactly the kind of connection I was hoping to create: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "Come join the conversation in [community/DM] — this deserves more space.",
            "I want to introduce you to someone — DM me.",
        ],
    },
    Archetype.PROVOCATEUR: {
        ResponseStep.OWN_THE_MOMENT: [
            "Finally, someone who actually engages with this properly.",
            "I respect this — you're not running from the take.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "The honest version of this is: {core_point}.",
            "Here's the part that makes people uncomfortable: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "More takes coming. Some of them are going to land even harder.",
            "If that challenged you, wait for what I'm posting next.",
        ],
    },
    Archetype.MENTOR: {
        ResponseStep.OWN_THE_MOMENT: [
            "This comment tells me you're exactly who I made this for.",
            "The fact that you're asking this puts you ahead of 90% of people.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "What I'd tell you directly is: {core_point}.",
            "The most important thing for someone in your position: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "DM me — I want to make sure you get the full picture.",
            "I'm doing a deeper breakdown of this soon. Make sure you're following.",
        ],
    },
    Archetype.VISIONARY: {
        ResponseStep.OWN_THE_MOMENT: [
            "You're seeing what others are going to realise in five years.",
            "This comment shows you're thinking ahead — that's rare.",
        ],
        ResponseStep.STAY_IN_VOICE: [
            "The direction this is all heading: {core_point}.",
            "What most people aren't seeing yet: {core_point}.",
        ],
        ResponseStep.PULL_BACK_IN: [
            "I'm mapping the full picture — follow to see where this goes.",
            "The next post connects all of this. Don't miss it.",
        ],
    },
}


def _extract_core_point(comment: str, post_context: str) -> str:
    """Extract a short core point from the comment or post context for template filling."""
    if len(post_context) > 10:
        words = post_context.split()
        return " ".join(words[:8]) + ("…" if len(words) > 8 else "")
    words = comment.split()
    return " ".join(words[:6]) + ("…" if len(words) > 6 else "")


def generate_response(
    comment: str,
    platform: Platform,
    profile: PersonalityProfile,
    post_context: str,
) -> str:
    """Generate a 3-step archetype response: own moment → stay in voice → pull back in.

    Step 1 — Own the Moment: acknowledge the interaction authentically.
    Step 2 — Stay in Voice: deliver value or insight in archetype voice.
    Step 3 — Pull Back In: create reason to keep engaging.
    """
    templates = _ARCHETYPE_STEP_TEMPLATES.get(
        profile.archetype,
        _ARCHETYPE_STEP_TEMPLATES[Archetype.EDUCATOR],
    )
    platform_modifier = PLATFORM_TONE_MODIFIERS.get(platform, "")
    intent = parse_interaction_intent(comment)
    core_point = _extract_core_point(comment, post_context)

    step1 = templates[ResponseStep.OWN_THE_MOMENT][0]
    step2 = templates[ResponseStep.STAY_IN_VOICE][0].replace("{core_point}", core_point)
    step3 = templates[ResponseStep.PULL_BACK_IN][0]

    if intent == "challenge":
        step2 = templates[ResponseStep.STAY_IN_VOICE][-1].replace("{core_point}", core_point)
    elif intent == "purchase_intent":
        step3 = "DM me directly — let's talk about how I can help you specifically."
    elif intent == "praise":
        step1 = templates[ResponseStep.OWN_THE_MOMENT][-1]

    response = f"{step1} {step2} {step3}"
    return response
