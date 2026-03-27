"""Base agent class — shared streaming logic and profile injection."""

import os
import anthropic
from typing import Generator

MODEL = "claude-opus-4-6"


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def stream_response(
    system: str,
    messages: list,
    max_tokens: int = 4096,
) -> Generator[str, None, str]:
    """
    Streams a Claude response. Yields text chunks.
    Returns the full response text when the generator is exhausted.
    """
    client = get_client()
    full_text = ""

    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            yield text

    return full_text


def call_once(
    system: str,
    messages: list,
    max_tokens: int = 2048,
) -> str:
    """Single blocking call — for structured data extraction, scoring, routing."""
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def build_profile_context(profile: dict, mood: str = "") -> str:
    """Injects user profile into a system prompt section."""
    if not profile.get("quiz_completed"):
        return ""
    lines = [
        f"CREATOR PROFILE:",
        f"  Archetype: {profile['archetype']}",
        f"  Language style: {profile['language_style']}",
        f"  Tone: {profile['tone']}",
    ]
    if mood:
        lines.append(f"  Today's mood: {mood}")
    return "\n".join(lines)
