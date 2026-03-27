"""Layer 1 — Personality Archive: quiz, archetype calculation, mood modulation."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models.archetypes import Archetype
from ..models.personality import (
    LanguageStyle,
    Mood,
    PersonalityProfile,
    QuizAnswer,
    QuizOption,
    QuizQuestion,
    QuizResult,
    ToneApproach,
)

# ---------------------------------------------------------------------------
# Quiz questions
# ---------------------------------------------------------------------------

QUIZ_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion(
        id="q1",
        question=(
            "When everything goes sideways on a project, what's your natural first move?"
        ),
        options=[
            QuizOption(
                text="Break down exactly what went wrong and explain it clearly so everyone understands",
                archetype_weights={"educator": 3, "mentor": 1, "sage": 1},
            ),
            QuizOption(
                text="Crack a joke to ease the tension, then rally everyone around a new plan",
                archetype_weights={"entertainer": 3, "connector": 2},
            ),
            QuizOption(
                text="Challenge the entire approach — if it broke, the foundation was flawed from the start",
                archetype_weights={"disruptor": 3, "provocateur": 2},
            ),
            QuizOption(
                text="Draw a new roadmap on the spot and start executing immediately",
                archetype_weights={"builder": 3, "visionary": 1},
            ),
            QuizOption(
                text="Take a step back, reflect on the pattern, and share the deeper lesson",
                archetype_weights={"sage": 3, "mentor": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q2",
        question=(
            "What's the most satisfying moment in your creative or professional work?"
        ),
        options=[
            QuizOption(
                text="When someone says 'I never thought of it that way' — I shifted their thinking",
                archetype_weights={"educator": 3, "sage": 1, "mentor": 1},
            ),
            QuizOption(
                text="When the room stops scrolling and locks in — I captured the moment",
                archetype_weights={"entertainer": 3, "creator": 1},
            ),
            QuizOption(
                text="When I ship something that didn't exist before — I built it from nothing",
                archetype_weights={"builder": 3, "creator": 2},
            ),
            QuizOption(
                text="When I connect two people who needed to meet and something incredible happens",
                archetype_weights={"connector": 3, "mentor": 1},
            ),
            QuizOption(
                text="When my bold prediction lands and people say 'you saw this coming'",
                archetype_weights={"visionary": 3, "disruptor": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q3",
        question=(
            "How do you actually feel about controversy and conflict in your content?"
        ),
        options=[
            QuizOption(
                text="I avoid it — I want to teach and illuminate, not polarise",
                archetype_weights={"educator": 3, "sage": 1},
            ),
            QuizOption(
                text="I use it strategically when it gets genuine attention for real ideas",
                archetype_weights={"entertainer": 2, "provocateur": 2, "disruptor": 1},
            ),
            QuizOption(
                text="I live for it — controversy usually means I'm challenging something that needs challenging",
                archetype_weights={"disruptor": 3, "provocateur": 3},
            ),
            QuizOption(
                text="I only engage with it if I've earned something true to say",
                archetype_weights={"sage": 3, "mentor": 1},
            ),
            QuizOption(
                text="I use it to spark the conversation the community needs to have",
                archetype_weights={"connector": 2, "provocateur": 2, "creator": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q4",
        question="When you think about the legacy you'll leave, what matters most to you?",
        options=[
            QuizOption(
                text="The knowledge I transferred and the number of minds I permanently changed",
                archetype_weights={"educator": 3, "mentor": 2},
            ),
            QuizOption(
                text="The experiences I created and the feelings I sparked in people",
                archetype_weights={"entertainer": 3, "creator": 2},
            ),
            QuizOption(
                text="The systems and businesses I built that outlast me and keep generating value",
                archetype_weights={"builder": 3, "visionary": 1},
            ),
            QuizOption(
                text="The future I helped people see and move toward before anyone else",
                archetype_weights={"visionary": 3, "disruptor": 1},
            ),
            QuizOption(
                text="The community I built where people found each other and belonged",
                archetype_weights={"connector": 3, "mentor": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q5",
        question="How do you naturally step into leadership?",
        options=[
            QuizOption(
                text="By sharing everything I know — I lead through radical knowledge transfer",
                archetype_weights={"educator": 3, "sage": 1},
            ),
            QuizOption(
                text="By energising people and making the journey feel worth it",
                archetype_weights={"entertainer": 3, "connector": 1},
            ),
            QuizOption(
                text="By questioning every assumption and pushing harder than anyone is comfortable with",
                archetype_weights={"disruptor": 3, "provocateur": 2},
            ),
            QuizOption(
                text="By guiding from hard-earned wisdom — I've been there and I'll show the way",
                archetype_weights={"mentor": 3, "sage": 2},
            ),
            QuizOption(
                text="By building the thing and letting the results lead for me",
                archetype_weights={"builder": 3, "visionary": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q6",
        question="How do you relate to your audience when you create content?",
        options=[
            QuizOption(
                text="They're my students — I owe them clarity, honesty, and depth",
                archetype_weights={"educator": 3, "mentor": 1},
            ),
            QuizOption(
                text="They're my crowd — I want them entertained, moved, and lit up",
                archetype_weights={"entertainer": 3, "creator": 1},
            ),
            QuizOption(
                text="They're co-conspirators — we're challenging the broken system together",
                archetype_weights={"disruptor": 3, "connector": 1},
            ),
            QuizOption(
                text="They're my network — every piece of content is an introduction or a bridge",
                archetype_weights={"connector": 3, "mentor": 1},
            ),
            QuizOption(
                text="They're fellow travellers I'm pulling forward toward a future they can't fully see yet",
                archetype_weights={"visionary": 3, "mentor": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q7",
        question="When you sit down to create content, what's your true starting point?",
        options=[
            QuizOption(
                text="A concept I want to break down so clearly it becomes obvious",
                archetype_weights={"educator": 3, "sage": 1},
            ),
            QuizOption(
                text="An emotion I want to spark — I engineer the feeling first",
                archetype_weights={"entertainer": 3, "creator": 2},
            ),
            QuizOption(
                text="A wrong idea I want to demolish with a better one",
                archetype_weights={"disruptor": 3, "provocateur": 2},
            ),
            QuizOption(
                text="A story — about me, someone I know, or something I witnessed",
                archetype_weights={"creator": 2, "mentor": 2, "connector": 1},
            ),
            QuizOption(
                text="A process I want to document — this is how I built or thought through something",
                archetype_weights={"builder": 3, "educator": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q8",
        question=(
            "What uncomfortable truth do you carry about your industry or field?"
        ),
        options=[
            QuizOption(
                text="Most people teach to feel smart, not to actually transfer value",
                archetype_weights={"educator": 2, "disruptor": 2, "provocateur": 1},
            ),
            QuizOption(
                text="Entertainment is taken less seriously than it deserves — joy is serious, powerful work",
                archetype_weights={"entertainer": 3, "creator": 1},
            ),
            QuizOption(
                text="The gatekeepers are protecting a broken system and calling it 'standards'",
                archetype_weights={"disruptor": 3, "provocateur": 2},
            ),
            QuizOption(
                text="Most people are too afraid to say what they actually think, so nothing real changes",
                archetype_weights={"provocateur": 3, "disruptor": 1},
            ),
            QuizOption(
                text="Everyone is building for today instead of designing for where things are going",
                archetype_weights={"visionary": 3, "builder": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q9",
        question="How do you feel about vulnerability and openness in your public content?",
        options=[
            QuizOption(
                text="I'm transparent about my thinking process but I keep personal stuff private",
                archetype_weights={"educator": 3, "builder": 1},
            ),
            QuizOption(
                text="Vulnerability is my superpower — it's what makes the connection real",
                archetype_weights={"connector": 3, "mentor": 2},
            ),
            QuizOption(
                text="I share strategic vulnerability — enough to build trust without losing authority",
                archetype_weights={"mentor": 3, "sage": 1},
            ),
            QuizOption(
                text="I prefer provocation to vulnerability — I'd rather make you think than make you feel sorry for me",
                archetype_weights={"provocateur": 3, "disruptor": 1},
            ),
            QuizOption(
                text="I let the work speak — the creative output is the most honest version of me",
                archetype_weights={"creator": 3, "visionary": 1},
            ),
        ],
    ),
    QuizQuestion(
        id="q10",
        question="Where do you honestly see yourself in 10 years?",
        options=[
            QuizOption(
                text="Having built a body of educational work that fundamentally changes how a field thinks",
                archetype_weights={"educator": 3, "sage": 1},
            ),
            QuizOption(
                text="At the centre of a cultural movement or creative moment that mattered",
                archetype_weights={"entertainer": 2, "creator": 2, "visionary": 1},
            ),
            QuizOption(
                text="Having disrupted and rebuilt something significant that was broken",
                archetype_weights={"disruptor": 3, "builder": 2},
            ),
            QuizOption(
                text="Mentoring the next generation — being the person I needed when I was starting out",
                archetype_weights={"mentor": 3, "connector": 1},
            ),
            QuizOption(
                text="Running systems and businesses I built that operate and grow without me",
                archetype_weights={"builder": 3, "visionary": 1},
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def calculate_archetype(
    answers: list[QuizAnswer],
) -> tuple[Archetype, dict[Archetype, float]]:
    """Tally weighted votes from quiz answers and return top archetype + scores."""
    scores: dict[str, float] = {a.value: 0.0 for a in Archetype}

    question_map: dict[str, QuizQuestion] = {q.id: q for q in QUIZ_QUESTIONS}

    for answer in answers:
        question = question_map.get(answer.question_id)
        if question is None:
            continue
        if answer.selected_option_index >= len(question.options):
            continue
        option = question.options[answer.selected_option_index]
        for archetype_val, weight in option.archetype_weights.items():
            if archetype_val in scores:
                scores[archetype_val] += weight

    top_archetype_val = max(scores, key=lambda k: scores[k])
    top_archetype = Archetype(top_archetype_val)

    typed_scores: dict[Archetype, float] = {Archetype(k): v for k, v in scores.items()}
    return top_archetype, typed_scores


def create_personality_profile(
    answers: list[QuizAnswer],
    language_style: LanguageStyle,
    tone_approach: ToneApproach,
    mood: Mood,
) -> PersonalityProfile:
    """Calculate archetype from quiz and create full personality profile."""
    archetype, _ = calculate_archetype(answers)
    return PersonalityProfile(
        archetype=archetype,
        language_style=language_style,
        tone_approach=tone_approach,
        mood=mood,
    )


# ---------------------------------------------------------------------------
# Mood modulation
# ---------------------------------------------------------------------------

_MOOD_VOICE_MAP: dict[Mood, dict[str, str]] = {
    Mood.FIRED_UP: {
        "instruction": "Deliver with raw urgency and fire. Short sentences. Punchy rhythm. No hedging whatsoever.",
        "opener_prefix": "RIGHT NOW —",
        "intensity": "maximum",
    },
    Mood.HAPPY: {
        "instruction": "Warm, joyful energy. Let the positivity be genuine and contagious.",
        "opener_prefix": "Here's something good:",
        "intensity": "bright",
    },
    Mood.FOCUSED: {
        "instruction": "Laser-precise. Every word earns its place. No filler. Structured and clean.",
        "opener_prefix": "One thing:",
        "intensity": "sharp",
    },
    Mood.PISSED_OFF: {
        "instruction": "Controlled intensity. Righteous frustration that turns into a sharp point.",
        "opener_prefix": "Let's be real —",
        "intensity": "sharp-edge",
    },
    Mood.REFLECTIVE: {
        "instruction": "Slower, more philosophical. Pause-worthy lines. Invite the audience to sit with the idea.",
        "opener_prefix": "I've been thinking —",
        "intensity": "thoughtful",
    },
    Mood.CONFIDENT: {
        "instruction": "No qualifiers. Declarative statements. Own every word without apology.",
        "opener_prefix": "Here's the truth:",
        "intensity": "assured",
    },
    Mood.PLAYFUL: {
        "instruction": "Light touch, quick wit. Keep it fun but don't lose the substance.",
        "opener_prefix": "Okay so —",
        "intensity": "light",
    },
    Mood.SERIOUS: {
        "instruction": "Gravity and weight. This matters. Measured tone, no jokes, full presence.",
        "opener_prefix": "This is important:",
        "intensity": "grave",
    },
}

_ARCHETYPE_BASE_VOICE: dict[Archetype, str] = {
    Archetype.EDUCATOR: "structured, clear, teaching-focused — break it down so anyone can understand",
    Archetype.ENTERTAINER: "high energy, emotionally vivid — make them feel before they think",
    Archetype.DISRUPTOR: "contrarian, sharp — challenge what's accepted, expose what's broken",
    Archetype.BUILDER: "process-oriented, transparent — document the real work and real results",
    Archetype.SAGE: "measured, philosophical — distil hard-earned wisdom into timeless statements",
    Archetype.CREATOR: "aesthetic, intentional — invite them into the creative world",
    Archetype.CONNECTOR: "warm, relational — every piece of content creates belonging",
    Archetype.PROVOCATEUR: "bold, unapologetic — say the thing nobody else will say",
    Archetype.MENTOR: "personal, empathetic — speak directly to the person who needs this most",
    Archetype.VISIONARY: "forward-looking, expansive — show them the future before they can see it",
}


def apply_mood_modulation(profile: PersonalityProfile, content_context: str) -> str:
    """Return a tone instruction string that bends archetype voice by current mood."""
    mood_data = _MOOD_VOICE_MAP.get(profile.mood, _MOOD_VOICE_MAP[Mood.FOCUSED])
    archetype_voice = _ARCHETYPE_BASE_VOICE.get(profile.archetype, "authentic and direct")

    language_map = {
        LanguageStyle.STREET_RAW: "raw, unfiltered street vernacular — keep it real",
        LanguageStyle.CASUAL: "conversational and relaxed — like talking to a friend",
        LanguageStyle.PROFESSIONAL: "polished and credible — expert without being stiff",
        LanguageStyle.ACADEMIC: "precise and well-reasoned — citations and structure matter",
        LanguageStyle.INSPIRATIONAL: "uplifting and motivational — move them to action",
    }
    tone_map = {
        ToneApproach.AUTHORITATIVE: "with full authority — this is not a suggestion",
        ToneApproach.PLAYFUL: "with a light, witty touch that still lands the point",
        ToneApproach.VULNERABLE: "with honest openness — show the human behind the content",
        ToneApproach.DIRECT: "straight to the point — no preamble, no fluff",
        ToneApproach.STORYTELLING: "through story — draw them in narratively before the lesson",
        ToneApproach.PROVOCATIVE: "with intentional provocation — challenge their assumptions",
    }

    language_instruction = language_map.get(profile.language_style, "naturally")
    tone_instruction = tone_map.get(profile.tone_approach, "authentically")

    return (
        f"VOICE: {archetype_voice}. "
        f"MOOD LAYER: {mood_data['instruction']} "
        f"LANGUAGE: Speak {language_instruction}. "
        f"TONE: Deliver {tone_instruction}. "
        f"OPENER SIGNAL: '{mood_data['opener_prefix']}' — "
        f"INTENSITY: {mood_data['intensity']}. "
        f"CONTEXT: {content_context}"
    )
