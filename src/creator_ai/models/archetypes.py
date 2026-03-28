"""Archetype definitions for the Creator AI system."""

from enum import Enum


class Archetype(str, Enum):
    EDUCATOR = "educator"
    ENTERTAINER = "entertainer"
    DISRUPTOR = "disruptor"
    BUILDER = "builder"
    SAGE = "sage"
    CREATOR = "creator"
    CONNECTOR = "connector"
    PROVOCATEUR = "provocateur"
    MENTOR = "mentor"
    VISIONARY = "visionary"


ARCHETYPE_METADATA: dict[str, dict] = {
    Archetype.EDUCATOR: {
        "name": "Educator",
        "tagline": "teaches, illuminates, transforms understanding",
        "description": (
            "You break down complex ideas so anyone can grasp them. "
            "Your content creates those 'aha' moments that people share with friends. "
            "You turn confusion into clarity and ignorance into insight."
        ),
        "content_style": (
            "Structured, clear breakdowns with numbered frameworks. "
            "Before-and-after understanding. Step-by-step logic. "
            "Heavy use of analogies and real-world examples."
        ),
        "strengths": ["clarity", "depth", "trust-building", "authority"],
        "platforms": ["YouTube", "LinkedIn", "TikTok"],
        "hook_patterns": [
            "Here's what nobody told you about {topic}:",
            "The {topic} breakdown that will change how you work:",
            "{number} things you must understand about {topic}:",
        ],
    },
    Archetype.ENTERTAINER: {
        "name": "Entertainer",
        "tagline": "captivates, energises, makes the world more alive",
        "description": (
            "You make people feel something. Joy, excitement, surprise — "
            "you weaponise emotion to build audiences that are genuinely hooked. "
            "You understand that attention is a gift people choose to give."
        ),
        "content_style": (
            "High energy, pattern interrupts, cliffhangers. "
            "Relatable scenarios played for maximum effect. "
            "Hooks so strong people physically stop scrolling."
        ),
        "strengths": ["virality", "reach", "emotional resonance", "memorability"],
        "platforms": ["TikTok", "Instagram", "YouTube"],
        "hook_patterns": [
            "POV: You just found out {topic} 🤯",
            "Nobody talks about {topic} like this 👀",
            "Wait till the end — {topic} will never be the same",
        ],
    },
    Archetype.DISRUPTOR: {
        "name": "Disruptor",
        "tagline": "challenges, exposes, rebuilds from the ground up",
        "description": (
            "You see broken systems everywhere and refuse to pretend they're fine. "
            "Your content pulls back the curtain on things others are too comfortable "
            "or too afraid to challenge. You exist to break what isn't working."
        ),
        "content_style": (
            "Contrarian takes, industry exposés, 'the truth nobody says'. "
            "Challenges dominant narratives with evidence and edge. "
            "Makes incumbents uncomfortable and newcomers feel vindicated."
        ),
        "strengths": ["disruption", "controversy", "category creation", "boldness"],
        "platforms": ["X", "LinkedIn", "TikTok"],
        "hook_patterns": [
            "The {industry} industry doesn't want you to know this:",
            "Everything you've been told about {topic} is wrong:",
            "I'm going to say what nobody in {industry} will say:",
        ],
    },
    Archetype.BUILDER: {
        "name": "Builder",
        "tagline": "creates systems, executes relentlessly, documents the journey",
        "description": (
            "You build things. Products, systems, businesses, frameworks. "
            "Your content documents the real process of creation — the wins, "
            "the failures, the pivots. You make people want to build alongside you."
        ),
        "content_style": (
            "Behind-the-scenes process content. Revenue numbers, growth metrics. "
            "Honest build logs. 'How I built X in Y days.' "
            "Frameworks and templates people can replicate."
        ),
        "strengths": ["credibility", "transparency", "replicability", "trust"],
        "platforms": ["LinkedIn", "X", "YouTube"],
        "hook_patterns": [
            "How I built {thing} from scratch in {timeframe}:",
            "The exact system I use to {outcome}:",
            "I documented everything building {thing} — here's what happened:",
        ],
    },
    Archetype.SAGE: {
        "name": "Sage",
        "tagline": "distils wisdom, sees patterns, speaks timeless truth",
        "description": (
            "You've lived enough, read enough, and reflected enough to speak with "
            "a different kind of authority. Your content doesn't chase trends — "
            "it speaks to eternal truths that land differently because they're real."
        ),
        "content_style": (
            "Measured, philosophical, dense with earned perspective. "
            "Short-form wisdom that rewards re-reading. "
            "Patterns observed across decades and domains."
        ),
        "strengths": ["depth", "longevity", "wisdom", "gravitas"],
        "platforms": ["LinkedIn", "X", "YouTube"],
        "hook_patterns": [
            "After {years} years, I've noticed one pattern in {topic}:",
            "The most important thing I understand about {topic} now:",
            "What {topic} taught me that no book could:",
        ],
    },
    Archetype.CREATOR: {
        "name": "Creator",
        "tagline": "crafts beauty, channels expression, makes the unseen visible",
        "description": (
            "You see the world differently and your content proves it. "
            "Aesthetic, intentional, behind-the-craft content that draws people "
            "into your creative world. You don't just make things — you make people "
            "feel something about the making."
        ),
        "content_style": (
            "Aesthetic-first content. Process videos, creative breakdowns. "
            "'This is what I made and why' storytelling. "
            "Invites people into the creative world rather than just the output."
        ),
        "strengths": ["aesthetics", "originality", "brand distinctiveness", "inspiration"],
        "platforms": ["Instagram", "TikTok", "YouTube"],
        "hook_patterns": [
            "I made something I've never made before:",
            "The creative process behind {work} — nobody shows this part:",
            "What it actually feels like to create {thing}:",
        ],
    },
    Archetype.CONNECTOR: {
        "name": "Connector",
        "tagline": "bridges worlds, builds community, makes everyone belong",
        "description": (
            "You see the people others miss and the links others don't make. "
            "Your content builds belonging — it makes people feel seen, found, "
            "and part of something larger than themselves. "
            "You are the network itself."
        ),
        "content_style": (
            "Community stories, introductions, collab content. "
            "'Meet someone you need to know' energy. "
            "Facilitates conversations and shared identity."
        ),
        "strengths": ["community", "collaboration", "belonging", "warmth"],
        "platforms": ["Instagram", "Facebook", "LinkedIn"],
        "hook_patterns": [
            "I want you to meet {person/group} — here's why:",
            "The community that {achievement} — their story:",
            "What happens when {group} comes together:",
        ],
    },
    Archetype.PROVOCATEUR: {
        "name": "Provocateur",
        "tagline": "challenges comfort, sparks debate, refuses the safe take",
        "description": (
            "You say the thing everyone is thinking but nobody will say. "
            "Your content creates heat — not for shock value, but because "
            "you genuinely believe in the take and refuse to dilute it. "
            "Controversy is your currency."
        ),
        "content_style": (
            "Hot takes, unpopular opinions, debate-starting statements. "
            "Sharp, unapologetic, designed to split the room. "
            "Always argues from a position, never waffles."
        ),
        "strengths": ["virality", "distinctiveness", "debate", "memorability"],
        "platforms": ["X", "TikTok", "LinkedIn"],
        "hook_patterns": [
            "Hot take: {controversial_opinion}",
            "Unpopular opinion that I'll die on: {take}",
            "I said what I said about {topic} and I won't be walking it back:",
        ],
    },
    Archetype.MENTOR: {
        "name": "Mentor",
        "tagline": "guides, transforms, sees potential others miss",
        "description": (
            "You invest in people. Your content doesn't just share information — "
            "it holds space for the person receiving it. You speak to the version "
            "of your audience that hasn't arrived yet, and you help them get there."
        ),
        "content_style": (
            "Personal, empathetic, guidance-focused. "
            "'Here's what I wish someone told me' energy. "
            "Speaks directly to the struggles of a specific person."
        ),
        "strengths": ["depth of connection", "loyalty", "transformation", "trust"],
        "platforms": ["YouTube", "Instagram", "LinkedIn"],
        "hook_patterns": [
            "If I could tell my younger self one thing about {topic}:",
            "The conversation I wish someone had with me about {topic}:",
            "This is for the person who is struggling with {topic} right now:",
        ],
    },
    Archetype.VISIONARY: {
        "name": "Visionary",
        "tagline": "sees the future, maps the shift, pulls people forward",
        "description": (
            "You see around corners. Your content paints a picture of what's "
            "coming before others can see it. You make people feel the urgency "
            "of now and the possibility of what's next. "
            "You are the permission slip for bold thinking."
        ),
        "content_style": (
            "Future-focused, trend synthesis, big-picture frameworks. "
            "'The world is about to change and here's how' energy. "
            "Connects current signals to future outcomes."
        ),
        "strengths": ["inspiration", "leadership", "thought leadership", "category creation"],
        "platforms": ["LinkedIn", "YouTube", "X"],
        "hook_patterns": [
            "The future of {topic} is closer than you think:",
            "In {timeframe}, {prediction} — here's why:",
            "What nobody is talking about in {industry} that's about to change everything:",
        ],
    },
}
