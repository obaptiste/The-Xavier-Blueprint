#!/usr/bin/env python3
"""
Creator AI — Agent Harness
Entry point for the CLI session loop.

Usage:
    cd harness
    python main.py
"""

import os
import sys
from pathlib import Path

# Ensure harness/ is on the path so agents/ and state.py resolve correctly
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv(Path(__file__).parent.parent / ".env")

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set. Add it to .env or export it.")
    sys.exit(1)

from state import StateManager
from orchestrator import Orchestrator


BANNER = """
  ╔═══════════════════════════════════════╗
  ║   CREATOR AI — SOCIAL CONTENT ENGINE  ║
  ║   Agent Harness v1.0                  ║
  ╚═══════════════════════════════════════╝
"""


def main():
    console = Console()
    console.print(f"[bold cyan]{BANNER}[/bold cyan]")

    state = StateManager()
    orchestrator = Orchestrator(state)

    # ------------------------------------------------------------------
    # Onboarding (first-time users only)
    # ------------------------------------------------------------------
    if state.is_new_user():
        console.print(Panel(
            "[bold]First time here.[/bold] Let's build your profile.\n"
            "Answer the questions honestly — there's no wrong answer.\n"
            "This shapes everything the system generates for you.",
            title="SETUP",
            border_style="cyan",
        ))
        orchestrator.run_onboarding()

    # ------------------------------------------------------------------
    # Session start — mood selector
    # ------------------------------------------------------------------
    profile = state.profile
    console.print(
        f"\n[bold green]Welcome back, {profile.get('archetype', 'Creator')}.[/bold green] "
        f"[dim]({profile.get('language_style')} | {profile.get('tone')})[/dim]"
    )

    snapshot = state.analytics_snapshot()
    if snapshot["total_sessions"] > 0:
        console.print(
            f"[dim]Sessions: {snapshot['total_sessions']} | "
            f"Content generated: {snapshot['total_content_generated']} | "
            f"People tracked: {snapshot['engagement']['total_tracked']}[/dim]"
        )

    mood, session_id = orchestrator.run_mood_selection()
    console.print(f"\n[dim]Session {session_id} started. Mood: {mood}[/dim]\n")
    console.print("Type [bold]help[/bold] to see what you can do. Type [bold]quit[/bold] to exit.\n")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    while True:
        try:
            user_input = console.input("[bold cyan]YOU >[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            console.print("[dim]Session saved. See you next time.[/dim]")
            state.log_action("session_ended", "user quit")
            break

        orchestrator.handle(user_input)


if __name__ == "__main__":
    main()
