"""
State Manager — persists all Creator AI data between sessions.

Tracks:
  - User profile (archetype, language style, tone)
  - Session history (mood per session, actions taken)
  - Content log (generated content per platform)
  - Engagement scores (per person, per platform)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

ENGAGEMENT_WEIGHTS = {
    "fiverr_dm": 5.0,
    "linkedin_dm": 4.0,
    "instagram_dm": 4.0,
    "youtube_link_click": 4.0,
    "instagram_save": 3.0,
    "tiktok_duet": 3.0,
    "tiktok_stitch": 3.0,
    "facebook_share": 3.0,
    "comment_with_question": 2.0,
    "standard_comment": 1.0,
    "like": 0.5,
}

ALERT_THRESHOLD = 15.0


class StateManager:
    """Central state store. All data lives in JSON files in /data."""

    def __init__(self):
        self._profile_path = DATA_DIR / "user_profile.json"
        self._content_path = DATA_DIR / "content_log.json"
        self._engagement_path = DATA_DIR / "engagement_log.json"
        self._sessions_path = DATA_DIR / "sessions.json"
        self._analytics_path = DATA_DIR / "analytics.json"
        self._current_session_id: Optional[str] = None
        self._ensure_files()

    # ------------------------------------------------------------------
    # File initialisation
    # ------------------------------------------------------------------

    def _ensure_files(self):
        defaults = {
            self._profile_path: {
                "archetype": None,
                "language_style": None,
                "tone": None,
                "quiz_completed": False,
                "created_at": None,
            },
            self._content_path: {"items": []},
            self._engagement_path: {"people": {}},
            self._sessions_path: {"sessions": []},
            self._analytics_path: {
                "mood_history": [],
                "platform_counts": {},
                "content_type_counts": {},
                "peak_days": [],
            },
        }
        for path, default in defaults.items():
            if not path.exists():
                self._write(path, default)

    def _read(self, path: Path) -> Any:
        with open(path, "r") as f:
            return json.load(f)

    def _write(self, path: Path, data: Any):
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    @property
    def profile(self) -> dict:
        return self._read(self._profile_path)

    def update_profile(self, **kwargs):
        data = self.profile
        data.update(kwargs)
        self._write(self._profile_path, data)

    def is_new_user(self) -> bool:
        return not self.profile.get("quiz_completed", False)

    def profile_context(self) -> str:
        """Returns a compact string summary of the user profile for injection into prompts."""
        p = self.profile
        if not p.get("quiz_completed"):
            return "No profile set yet."
        return (
            f"Archetype: {p['archetype']} | "
            f"Language style: {p['language_style']} | "
            f"Tone: {p['tone']}"
        )

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def start_session(self, mood: str) -> str:
        sessions = self._read(self._sessions_path)
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sessions["sessions"].append(
            {
                "id": session_id,
                "mood": mood,
                "started_at": datetime.now().isoformat(),
                "actions": [],
            }
        )
        self._write(self._sessions_path, sessions)
        self._current_session_id = session_id

        # Track mood in analytics
        analytics = self._read(self._analytics_path)
        analytics["mood_history"].append(
            {"mood": mood, "date": datetime.now().date().isoformat()}
        )
        self._write(self._analytics_path, analytics)

        return session_id

    def log_action(self, action_type: str, detail: str):
        if not self._current_session_id:
            return
        sessions = self._read(self._sessions_path)
        for s in sessions["sessions"]:
            if s["id"] == self._current_session_id:
                s["actions"].append(
                    {
                        "type": action_type,
                        "detail": detail,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                break
        self._write(self._sessions_path, sessions)

    def current_session_mood(self) -> Optional[str]:
        if not self._current_session_id:
            return None
        sessions = self._read(self._sessions_path)
        for s in sessions["sessions"]:
            if s["id"] == self._current_session_id:
                return s.get("mood")
        return None

    # ------------------------------------------------------------------
    # Content log
    # ------------------------------------------------------------------

    def log_content(
        self,
        platform: str,
        content_type: str,
        snippet: str,
        source_material: str = "",
    ):
        content = self._read(self._content_path)
        content["items"].append(
            {
                "platform": platform,
                "type": content_type,
                "snippet": snippet[:300],
                "source_material": source_material[:200],
                "mood": self.current_session_mood(),
                "archetype": self.profile.get("archetype"),
                "generated_at": datetime.now().isoformat(),
                "session_id": self._current_session_id,
            }
        )
        self._write(self._content_path, content)

        # Track platform/type in analytics
        analytics = self._read(self._analytics_path)
        analytics["platform_counts"][platform] = (
            analytics["platform_counts"].get(platform, 0) + 1
        )
        analytics["content_type_counts"][content_type] = (
            analytics["content_type_counts"].get(content_type, 0) + 1
        )
        today = datetime.now().date().isoformat()
        if today not in analytics["peak_days"]:
            analytics["peak_days"].append(today)
        self._write(self._analytics_path, analytics)

    def get_content_history(self, limit: int = 20) -> list:
        items = self._read(self._content_path)["items"]
        return items[-limit:]

    # ------------------------------------------------------------------
    # Engagement scoring
    # ------------------------------------------------------------------

    def add_engagement(
        self,
        person_id: str,
        platform: str,
        interaction_type: str,
        context: str = "",
    ) -> dict:
        """
        Logs an interaction, returns {points_added, total_points, alert_triggered}.
        """
        points = ENGAGEMENT_WEIGHTS.get(interaction_type, 1.0)
        eng = self._read(self._engagement_path)

        if person_id not in eng["people"]:
            eng["people"][person_id] = {
                "total_points": 0.0,
                "interactions": [],
                "alerted": False,
            }

        eng["people"][person_id]["interactions"].append(
            {
                "platform": platform,
                "type": interaction_type,
                "points": points,
                "context": context,
                "timestamp": datetime.now().isoformat(),
            }
        )
        eng["people"][person_id]["total_points"] += points
        total = eng["people"][person_id]["total_points"]

        alert_triggered = False
        if total >= ALERT_THRESHOLD and not eng["people"][person_id]["alerted"]:
            eng["people"][person_id]["alerted"] = True
            alert_triggered = True

        self._write(self._engagement_path, eng)
        self.log_action(
            "engagement_logged",
            f"{person_id} +{points}pts on {platform} ({interaction_type})",
        )

        return {
            "points_added": points,
            "total_points": total,
            "alert_triggered": alert_triggered,
        }

    def get_high_intent_people(self) -> list:
        eng = self._read(self._engagement_path)
        return [
            {"id": pid, **pdata}
            for pid, pdata in eng["people"].items()
            if pdata["total_points"] >= ALERT_THRESHOLD
        ]

    def get_engagement_summary(self) -> dict:
        eng = self._read(self._engagement_path)
        people = eng["people"]
        return {
            "total_tracked": len(people),
            "high_intent_count": sum(
                1 for p in people.values() if p["total_points"] >= ALERT_THRESHOLD
            ),
            "total_interactions": sum(
                len(p["interactions"]) for p in people.values()
            ),
        }

    # ------------------------------------------------------------------
    # Analytics snapshot
    # ------------------------------------------------------------------

    def analytics_snapshot(self) -> dict:
        analytics = self._read(self._analytics_path)
        sessions = self._read(self._sessions_path)
        content = self._read(self._content_path)
        eng_summary = self.get_engagement_summary()

        mood_counts: dict = {}
        for entry in analytics["mood_history"]:
            m = entry["mood"]
            mood_counts[m] = mood_counts.get(m, 0) + 1

        return {
            "total_sessions": len(sessions["sessions"]),
            "total_content_generated": len(content["items"]),
            "platform_counts": analytics["platform_counts"],
            "content_type_counts": analytics["content_type_counts"],
            "mood_distribution": mood_counts,
            "active_days": len(set(analytics["peak_days"])),
            "engagement": eng_summary,
        }
