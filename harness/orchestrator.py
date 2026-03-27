"""
Orchestrator — routes user intent to the correct agent layer.

Uses a lightweight Claude call to classify intent, then dispatches
to the appropriate specialist agent.
"""

from agents.base import call_once
from state import StateManager, ENGAGEMENT_WEIGHTS

INTENT_SYSTEM = """You are a routing engine for the Creator AI system.

Classify the user's message into EXACTLY ONE of these intents:

INTAKE       — They are uploading content, describing a photo/video/statement, or sharing raw material for the Brain to process
GENERATE     — They want to create platform content (posts, scripts, captions)
SCHEDULE     — They want a deployment calendar or posting schedule
RESPOND      — They received a comment, DM, or interaction and need a reply in their voice
LOG_ENGAGE   — They are logging an engagement/interaction for scoring (someone liked, commented, shared, DMed)
ALERTS       — They want to see who has crossed the high-intent threshold
ANALYTICS    — They want insights on their creative patterns or audience
HELP         — They want to know what they can do or how the system works
UNKNOWN      — None of the above

Respond with ONLY the intent word. Nothing else."""


def classify_intent(user_input: str) -> str:
    result = call_once(
        INTENT_SYSTEM,
        [{"role": "user", "content": user_input}],
        max_tokens=20,
    )
    intent = result.strip().upper()
    valid = {"INTAKE", "GENERATE", "SCHEDULE", "RESPOND", "LOG_ENGAGE", "ALERTS", "ANALYTICS", "HELP", "UNKNOWN"}
    return intent if intent in valid else "UNKNOWN"


class Orchestrator:
    """
    Drives a single session. Maintains the active conversation context
    and routes each user message to the right agent.
    """

    def __init__(self, state: StateManager):
        self.state = state
        self.conversation_history: list = []
        self.intake_summary: str = ""
        self.last_generated_content: str = ""
        self.active_platforms: list = []

    # ------------------------------------------------------------------
    # Session startup
    # ------------------------------------------------------------------

    def run_onboarding(self):
        """Full personality quiz + style/tone setup for new users."""
        from agents.personality import (
            run_quiz, run_style_tone,
            extract_archetype, extract_style, extract_tone,
        )
        from rich.console import Console
        console = Console()

        console.print("\n[bold cyan]Welcome to Creator AI.[/bold cyan]")
        console.print("Let's find out who you are.\n")

        # --- Quiz phase ---
        history = []
        archetype = None
        while not archetype:
            user_input = console.input("[bold]> [/bold]").strip()
            if not user_input:
                continue
            history.append({"role": "user", "content": user_input})
            response = run_quiz(history)
            history.append({"role": "assistant", "content": response})
            archetype = extract_archetype(response)

        console.print(f"\n[bold green]Archetype locked in: {archetype}[/bold green]\n")

        # --- Style/Tone phase ---
        style_history = []
        style = tone = None
        while not (style and tone):
            user_input = console.input("[bold]> [/bold]").strip()
            if not user_input:
                continue
            style_history.append({"role": "user", "content": user_input})
            response = run_style_tone(style_history)
            style_history.append({"role": "assistant", "content": response})
            style = style or extract_style(response)
            tone = tone or extract_tone(response)

        self.state.update_profile(
            archetype=archetype,
            language_style=style,
            tone=tone,
            quiz_completed=True,
            created_at=__import__("datetime").datetime.now().isoformat(),
        )
        console.print(f"\n[bold green]Profile saved.[/bold green]")
        self.state.log_action("onboarding_complete", f"{archetype} | {style} | {tone}")

    def run_mood_selection(self):
        """Daily mood selector."""
        from agents.personality import run_mood_selector, extract_mood
        from rich.console import Console
        console = Console()

        console.print("\n[bold cyan]Before we create anything —[/bold cyan]")
        mood_history = []
        mood = None
        while not mood:
            user_input = console.input("[bold]> [/bold]").strip()
            if not user_input:
                run_mood_selector([])
                continue
            mood_history.append({"role": "user", "content": user_input})
            response = run_mood_selector(mood_history)
            mood_history.append({"role": "assistant", "content": response})
            mood = extract_mood(response)

        session_id = self.state.start_session(mood)
        return mood, session_id

    # ------------------------------------------------------------------
    # Intent dispatch
    # ------------------------------------------------------------------

    def handle(self, user_input: str):
        """Classify and route a user message."""
        intent = classify_intent(user_input)
        self.state.log_action("user_input", f"[{intent}] {user_input[:100]}")

        dispatch = {
            "INTAKE": self._handle_intake,
            "GENERATE": self._handle_generate,
            "SCHEDULE": self._handle_schedule,
            "RESPOND": self._handle_respond,
            "LOG_ENGAGE": self._handle_log_engage,
            "ALERTS": self._handle_alerts,
            "ANALYTICS": self._handle_analytics,
            "HELP": self._handle_help,
            "UNKNOWN": self._handle_unknown,
        }
        handler = dispatch.get(intent, self._handle_unknown)
        handler(user_input)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_intake(self, user_input: str):
        from agents.brain import run_intake, run_intake_followup
        from rich.console import Console
        console = Console()

        console.print("\n[bold blue]THE BRAIN[/bold blue] — Tell me more about this content.\n")

        profile = self.state.profile
        mood = self.state.current_session_mood() or ""
        history = self.state.get_content_history(10)

        # Initial intake
        response = run_intake(user_input, profile, mood, history)
        conv = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response},
        ]

        # Allow follow-up dialogue until user is ready
        while True:
            follow = console.input("[bold]> [/bold]").strip()
            if not follow:
                continue
            if follow.lower() in ("done", "ready", "yes", "confirmed", "let's go", "lets go"):
                self.intake_summary = response
                console.print("\n[dim]Content understood. Ready to generate.[/dim]\n")
                self.state.log_action("intake_complete", user_input[:150])
                break
            conv.append({"role": "user", "content": follow})
            response = run_intake_followup(conv, profile, mood, history)
            conv.append({"role": "assistant", "content": response})
            self.intake_summary = response

    def _handle_generate(self, user_input: str):
        from agents.content import run_content_generation, PLATFORMS
        from rich.console import Console
        console = Console()

        if not self.intake_summary:
            console.print("[yellow]Run an intake first — tell The Brain about your content.[/yellow]")
            return

        # Parse which platforms are requested
        platforms = [p for p in PLATFORMS if p.lower() in user_input.lower()]
        if not platforms:
            console.print(
                "\n[bold]Which platforms?[/bold] "
                f"Available: {', '.join(PLATFORMS)}\n"
            )
            answer = console.input("[bold]> [/bold]").strip()
            platforms = [p for p in PLATFORMS if p.lower() in answer.lower()]
        if not platforms:
            platforms = PLATFORMS  # default: all

        self.active_platforms = platforms
        console.print(f"\n[bold blue]CONTENT ENGINE[/bold blue] — generating for: {', '.join(platforms)}\n")

        profile = self.state.profile
        mood = self.state.current_session_mood() or ""
        content = run_content_generation(self.intake_summary, platforms, profile, mood)
        self.last_generated_content = content

        # Log each platform to state
        for p in platforms:
            snippet = content[:200]
            self.state.log_content(p, "mixed", snippet, self.intake_summary[:150])

        self.state.log_action("content_generated", f"Platforms: {', '.join(platforms)}")

    def _handle_schedule(self, user_input: str):
        from agents.sequencer import run_sequencer
        from rich.console import Console
        console = Console()

        if not self.last_generated_content:
            console.print("[yellow]Generate content first before scheduling.[/yellow]")
            return

        console.print("\n[bold blue]SEQUENCER[/bold blue] — building your deployment calendar.\n")
        profile = self.state.profile
        mood = self.state.current_session_mood() or ""
        run_sequencer(self.last_generated_content[:1500], profile, mood, self.active_platforms)
        self.state.log_action("schedule_created", f"Platforms: {', '.join(self.active_platforms)}")

    def _handle_respond(self, user_input: str):
        from agents.responder import run_responder
        from rich.console import Console
        console = Console()

        console.print("\n[bold blue]RESPONSE ENGINE[/bold blue]\n")

        # Ask for platform and interaction type
        console.print("Platform? (TikTok / Instagram / Facebook / LinkedIn / YouTube / Fiverr / X)")
        platform = console.input("[bold]> [/bold]").strip()
        console.print("Interaction type? (e.g. comment, DM, reply)")
        itype = console.input("[bold]> [/bold]").strip()

        profile = self.state.profile
        mood = self.state.current_session_mood() or ""
        run_responder(user_input, platform, itype, profile, mood)
        self.state.log_action("response_generated", f"{platform} | {itype} | {user_input[:80]}")

    def _handle_log_engage(self, user_input: str):
        from rich.console import Console
        console = Console()

        console.print("\n[bold blue]ENGAGEMENT TRACKER[/bold blue]\n")
        console.print("Person ID (a name or handle to track them by):")
        person_id = console.input("[bold]> [/bold]").strip()

        console.print("Platform:")
        platform = console.input("[bold]> [/bold]").strip()

        console.print(f"Interaction type? Options:\n{', '.join(ENGAGEMENT_WEIGHTS.keys())}")
        itype = console.input("[bold]> [/bold]").strip()

        result = self.state.add_engagement(person_id, platform, itype, context=user_input)
        pts = result["total_points"]
        added = result["points_added"]

        console.print(f"\n[green]+{added} points[/green] — {person_id} now has [bold]{pts:.1f}[/bold] total points.")

        if result["alert_triggered"]:
            console.print(
                f"\n[bold red]🚨 ALERT — {person_id} has crossed the threshold ({pts:.1f} points).[/bold red]"
            )
            console.print("[bold]Time to make human contact.[/bold]")
            console.print(f"They've shown high intent. Step in personally and convert this relationship.\n")

    def _handle_alerts(self, user_input: str):
        from rich.console import Console
        console = Console()

        people = self.state.get_high_intent_people()
        if not people:
            console.print("\n[dim]No high-intent alerts yet. Keep logging engagement.[/dim]\n")
            return

        console.print(f"\n[bold red]HIGH-INTENT ALERTS ({len(people)} people)[/bold red]\n")
        for p in people:
            console.print(f"  [bold]{p['id']}[/bold] — {p['total_points']:.1f} points")
            for i in p["interactions"][-3:]:
                console.print(f"    └ {i['platform']} | {i['type']} | {i.get('context', '')[:60]}")
        console.print()

    def _handle_analytics(self, user_input: str):
        from agents.insights import run_creative_analytics, run_audience_intelligence
        from rich.console import Console
        console = Console()

        snapshot = self.state.analytics_snapshot()
        profile = self.state.profile
        mood = self.state.current_session_mood() or ""

        console.print("\n[bold blue]PERSONAL CREATIVE ANALYTICS[/bold blue]\n")
        run_creative_analytics(snapshot, profile, mood)

        console.print("\n[bold blue]AUDIENCE ENGAGEMENT INTELLIGENCE[/bold blue]\n")
        content_history = self.state.get_content_history(50)
        run_audience_intelligence(snapshot["engagement"], content_history, profile)

        self.state.log_action("analytics_viewed", "")

    def _handle_help(self, user_input: str):
        from rich.console import Console
        console = Console()

        console.print(
            "\n[bold cyan]CREATOR AI — What you can do:[/bold cyan]\n"
            "\n[bold]INTAKE[/bold]    — Describe a photo, video, statement, or calendar event"
            "\n[bold]GENERATE[/bold] — Generate platform content (TikTok, Instagram, LinkedIn, etc.)"
            "\n[bold]SCHEDULE[/bold] — Get a deployment calendar after generating content"
            "\n[bold]RESPOND[/bold]  — Get a reply to a comment or DM in your voice"
            "\n[bold]LOG[/bold]      — Log an engagement interaction (like, comment, DM, share)"
            "\n[bold]ALERTS[/bold]   — See who has crossed the high-intent threshold"
            "\n[bold]ANALYTICS[/bold]— Get insights on your creative patterns and audience"
            "\n[bold]QUIT[/bold]     — End session\n"
        )

    def _handle_unknown(self, user_input: str):
        from rich.console import Console
        Console().print(
            "\n[dim]Not sure what you need. Try: intake, generate, schedule, respond, log, alerts, analytics, or help.[/dim]\n"
        )
