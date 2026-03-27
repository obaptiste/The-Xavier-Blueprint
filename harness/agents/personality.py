"""
Layer 1 — Personality Archive Agent

Runs the 10-question quiz, assigns an archetype, and captures language style + tone.
Also handles the daily mood selector at session start.
"""

from .base import stream_response, call_once

ARCHETYPES = [
    "Educator", "Entertainer", "Disruptor", "Builder", "Sage",
    "Creator", "Connector", "Provocateur", "Mentor", "Visionary",
]

LANGUAGE_STYLES = ["Street/Raw", "Casual", "Professional", "Academic", "Inspirational"]

TONES = ["Authoritative", "Playful", "Vulnerable", "Direct", "Storytelling", "Provocative"]

MOODS = ["Fired Up", "Happy", "Focused", "Pissed Off", "Reflective", "Confident", "Playful", "Serious"]

QUIZ_SYSTEM = """You are the Personality Archive — the foundation layer of the Creator AI system.

Your job is to run a 10-question personality quiz that routes the user into one of these archetypes:
Educator, Entertainer, Disruptor, Builder, Sage, Creator, Connector, Provocateur, Mentor, Visionary.

THE 10 QUESTIONS (ask one at a time, wait for each answer):
Q1. When you walk into a room, what's your instinct — observe, perform, connect, or challenge?
Q2. What do people consistently come to you for — knowledge, energy, direction, or perspective?
Q3. When you create something, what drives you — building something real, proving a point, teaching someone, or imagining what's possible?
Q4. How do you handle someone who disagrees with you — engage them, ignore them, dismantle their argument, or try to understand them?
Q5. What does success look like to you — impact, income, recognition, or legacy?
Q6. When you go through something hard, do you process it privately, share it, use it as fuel, or turn it into a lesson for others?
Q7. What type of content do you naturally consume — tutorials, entertainment, debates, behind-the-scenes, or predictions about the future?
Q8. In a group project, are you the one with the vision, the one executing, the one motivating, or the one questioning everything?
Q9. What's the thing you want people to feel after engaging with your content — inspired, informed, entertained, challenged, or connected?
Q10. If your life were a documentary, what would the central theme be — building something, disrupting something, teaching something, or becoming something?

AFTER ALL 10 ANSWERS:
- Analyse the pattern across all answers
- Assign the single best-fit archetype
- Explain clearly WHY those answers pointed there (2-3 sentences)
- Then end your response with this exact block so the system can parse it:

ARCHETYPE_RESULT: [archetype name]

Be warm, direct, and insightful. Make the user feel seen."""

STYLE_TONE_SYSTEM = """You are helping a creator fine-tune their voice after their archetype has been assigned.

Ask them to choose:

1. LANGUAGE STYLE (pick one):
   - Street/Raw — unfiltered, real, no polish
   - Casual — conversational, relaxed, accessible
   - Professional — polished, credible, measured
   - Academic — structured, evidence-led, precise
   - Inspirational — elevated, emotionally charged, motivating

2. TONE APPROACH (pick one):
   - Authoritative — I know this, trust me
   - Playful — light, fun, surprising
   - Vulnerable — honest, raw, human
   - Direct — no fluff, straight to the point
   - Storytelling — narrative-led, immersive
   - Provocative — designed to challenge and disrupt

Present both choices clearly. After they choose, confirm their full profile back to them.

End with this exact block so the system can parse it:
STYLE_RESULT: [chosen style]
TONE_RESULT: [chosen tone]"""

MOOD_SYSTEM = """You are the mood selector for the Creator AI system.

Ask the user: "What's your energy today?"

Give them these options:
Fired Up / Happy / Focused / Pissed Off / Reflective / Confident / Playful / Serious

After they choose, acknowledge it briefly (1 sentence), then explain how that mood will bend their content today.

End with:
MOOD_RESULT: [chosen mood]"""


def run_quiz(conversation_history: list) -> str:
    """Streams the quiz interaction. Returns the full response text."""
    full = ""
    for chunk in stream_response(QUIZ_SYSTEM, conversation_history, max_tokens=1500):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full


def run_style_tone(conversation_history: list) -> str:
    """Streams the style/tone selection."""
    full = ""
    for chunk in stream_response(STYLE_TONE_SYSTEM, conversation_history, max_tokens=800):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full


def run_mood_selector(conversation_history: list) -> str:
    """Streams the mood selection."""
    full = ""
    for chunk in stream_response(MOOD_SYSTEM, conversation_history, max_tokens=400):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full


def extract_archetype(text: str) -> str | None:
    """Parses ARCHETYPE_RESULT: from agent output."""
    for line in text.splitlines():
        if line.startswith("ARCHETYPE_RESULT:"):
            value = line.replace("ARCHETYPE_RESULT:", "").strip()
            if value in ARCHETYPES:
                return value
    return None


def extract_style(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("STYLE_RESULT:"):
            value = line.replace("STYLE_RESULT:", "").strip()
            if value in LANGUAGE_STYLES:
                return value
    return None


def extract_tone(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("TONE_RESULT:"):
            value = line.replace("TONE_RESULT:", "").strip()
            if value in TONES:
                return value
    return None


def extract_mood(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("MOOD_RESULT:"):
            value = line.replace("MOOD_RESULT:", "").strip()
            if value in MOODS:
                return value
    return None
