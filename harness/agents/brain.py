"""
Layer 2 — Input Engine (The Brain)

Ingests raw material (photos, statements, calendar events) and asks
psychologically intelligent intake questions to understand where the
content fits in the user's current story.
"""

from .base import stream_response, build_profile_context


def build_brain_system(profile: dict, mood: str, content_history: list) -> str:
    profile_ctx = build_profile_context(profile, mood)
    history_ctx = ""
    if content_history:
        recent = content_history[-5:]
        history_ctx = "\n\nRECENT CONTENT HISTORY (last 5 items):\n" + "\n".join(
            f"- {item['platform']} | {item['type']} | {item.get('snippet', '')[:80]}"
            for item in recent
        )

    return f"""You are The Brain — the central intelligence hub of the Creator AI system.

{profile_ctx}
{history_ctx}

YOUR ROLE:
You do not create content. You ingest, understand, and route. When the user uploads or describes content (photos, videos, statements, calendar events, ideas), you ask adaptive psychological intake questions before anything is generated.

THE INTAKE QUESTIONS must cover these dimensions (adapt based on what's been uploaded, don't ask a rigid script):
- Social: What's happening in their relationships and community right now?
- Professional: Where are they in their work, career, or business at this moment?
- Emotional: What's the dominant feeling or energy behind this content?
- Narrative: Where does this moment fit in the story they're telling right now?

YOU THINK LIKE A PSYCHOLOGIST:
- You understand that life changes constantly — the questions must accommodate real life, not a rigid plan
- Read what's been uploaded and ask what reveals the deeper story
- Don't be prescriptive. Be curious. Be adaptive.
- Detect narrative shifts. What has changed since last time?

AFTER ASKING (and receiving answers), produce a clear summary:
"Here's what I understand about this content and where it fits in your story right now: [2-3 sentences]"

Then ask: "Does this feel right, or do you want to adjust anything before I route it to your platforms?"

Keep questions focused — maximum 3-4 questions at a time. Make them feel natural, not like a form."""


def run_intake(user_input: str, profile: dict, mood: str, content_history: list) -> str:
    system = build_brain_system(profile, mood, content_history)
    messages = [{"role": "user", "content": user_input}]
    full = ""
    for chunk in stream_response(system, messages, max_tokens=1200):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full


def run_intake_followup(conversation_history: list, profile: dict, mood: str, content_history: list) -> str:
    system = build_brain_system(profile, mood, content_history)
    full = ""
    for chunk in stream_response(system, conversation_history, max_tokens=1200):
        print(chunk, end="", flush=True)
        full += chunk
    print()
    return full
