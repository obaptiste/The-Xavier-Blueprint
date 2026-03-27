"""Layer 3 — Platform Mini Apps: archetype-voiced, platform-specific content generation."""

from __future__ import annotations

from ..models.archetypes import Archetype, ARCHETYPE_METADATA
from ..models.content import ContentUpload, ContentType, GeneratedContent, Platform
from ..models.personality import LanguageStyle, Mood, PersonalityProfile, ToneApproach

# ---------------------------------------------------------------------------
# Archetype Voice Engine
# ---------------------------------------------------------------------------


class ArchetypeVoiceEngine:
    """Transforms raw content into archetype + mood + language-appropriate voice."""

    _OPENING_FRAMES: dict[str, list[str]] = {
        Archetype.EDUCATOR: [
            "Here's what most people get wrong about {topic}:",
            "The real breakdown nobody gave you on {topic}:",
            "Let me show you exactly how {topic} actually works:",
        ],
        Archetype.ENTERTAINER: [
            "POV: {topic} just changed everything 🤯",
            "Nobody is talking about {topic} like this 👀",
            "Stop scrolling — {topic} is about to blow your mind:",
        ],
        Archetype.DISRUPTOR: [
            "The {topic} industry is lying to you and here's the proof:",
            "Everything you've been told about {topic} is wrong:",
            "I'm going to say what nobody in {topic} will say:",
        ],
        Archetype.BUILDER: [
            "Here's exactly how I built {topic} from scratch:",
            "The system I used to go from zero to {topic}:",
            "I documented every step of building {topic} — here's what happened:",
        ],
        Archetype.SAGE: [
            "After years of {topic}, I've noticed one pattern:",
            "What {topic} teaches you that no one tells you upfront:",
            "The most important truth I know about {topic}:",
        ],
        Archetype.CREATOR: [
            "I made something I've never made before — {topic}:",
            "The creative process behind {topic} — the part nobody shows:",
            "What it actually feels like to create {topic}:",
        ],
        Archetype.CONNECTOR: [
            "I want you to meet the people behind {topic}:",
            "The community that made {topic} possible:",
            "What happens when the right people come together around {topic}:",
        ],
        Archetype.PROVOCATEUR: [
            "Hot take: {topic} is not what you think it is.",
            "Unpopular opinion I'll die on — {topic}:",
            "I said what I said about {topic} and I won't walk it back:",
        ],
        Archetype.MENTOR: [
            "If I could tell my younger self one thing about {topic}:",
            "This is for the person struggling with {topic} right now:",
            "The conversation I wish someone had with me about {topic}:",
        ],
        Archetype.VISIONARY: [
            "The future of {topic} is closer than anyone thinks:",
            "What nobody is talking about in {topic} that's about to change everything:",
            "In {timeframe}, {topic} will look completely different — here's why:",
        ],
    }

    _MOOD_AMPLIFIERS: dict[str, str] = {
        Mood.FIRED_UP: "🔥 ",
        Mood.HAPPY: "✨ ",
        Mood.FOCUSED: "",
        Mood.PISSED_OFF: "⚡ ",
        Mood.REFLECTIVE: "💭 ",
        Mood.CONFIDENT: "💪 ",
        Mood.PLAYFUL: "😄 ",
        Mood.SERIOUS: "",
    }

    _LANGUAGE_CLOSERS: dict[str, str] = {
        LanguageStyle.STREET_RAW: "No cap. This is the real.",
        LanguageStyle.CASUAL: "Honestly, this is the real deal.",
        LanguageStyle.PROFESSIONAL: "The data and experience support this entirely.",
        LanguageStyle.ACADEMIC: "The evidence is consistent across contexts.",
        LanguageStyle.INSPIRATIONAL: "You already have everything you need to make this real.",
    }

    def get_opening(self, archetype: Archetype, topic: str) -> str:
        """Return the best opening frame for the given archetype and topic."""
        frames = self._OPENING_FRAMES.get(archetype, self._OPENING_FRAMES[Archetype.EDUCATOR])
        frame = frames[0]
        return frame.replace("{topic}", topic).replace("{timeframe}", "5 years").replace("{thing}", topic)

    def get_mood_prefix(self, mood: Mood) -> str:
        return self._MOOD_AMPLIFIERS.get(mood, "")

    def get_closer(self, language_style: LanguageStyle) -> str:
        return self._LANGUAGE_CLOSERS.get(language_style, "This is the truth.")

    def transform(
        self,
        raw_text: str,
        archetype: Archetype,
        mood: Mood,
        language_style: LanguageStyle,
        topic: str,
    ) -> str:
        """Full voice transformation of raw text."""
        prefix = self.get_mood_prefix(mood)
        opening = self.get_opening(archetype, topic)
        closer = self.get_closer(language_style)
        return f"{prefix}{opening}\n\n{raw_text}\n\n{closer}"


_ENGINE = ArchetypeVoiceEngine()


def _extract_topic(upload: ContentUpload) -> str:
    """Pull a short topic summary from the upload's raw content."""
    words = upload.raw_content.strip().split()
    return " ".join(words[:6]) if words else "this"


# ---------------------------------------------------------------------------
# Platform generators
# ---------------------------------------------------------------------------


def generate_tiktok_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a TikTok-ready script with hook, body, and CTA."""
    topic = _extract_topic(upload)
    opening = _ENGINE.get_opening(profile.archetype, topic)
    mood_prefix = _ENGINE.get_mood_prefix(profile.mood)

    body_lines = [
        upload.raw_content[:200] if len(upload.raw_content) > 200 else upload.raw_content,
    ]

    archetype_cta = {
        Archetype.EDUCATOR: "Save this. Share it with someone who needs to understand this.",
        Archetype.ENTERTAINER: "Duet this if you felt that. Drop a 🔥 if you're not sleeping on this.",
        Archetype.DISRUPTOR: "Tell me in the comments — did you already know this, or did I just change your perspective?",
        Archetype.BUILDER: "Follow for the full build. I'm documenting everything.",
        Archetype.SAGE: "Sit with that. Come back to it tomorrow.",
        Archetype.CREATOR: "Behind-the-scenes of the full process is coming. Stay close.",
        Archetype.CONNECTOR: "Tag someone who needs to be in this conversation.",
        Archetype.PROVOCATEUR: "Disagree? Good. Tell me why in the comments.",
        Archetype.MENTOR: "Screenshot this and keep it. You'll need it.",
        Archetype.VISIONARY: "This is early. Follow to be ahead of the curve.",
    }
    cta = archetype_cta.get(profile.archetype, "Follow for more.")

    script = (
        f"[HOOK — first 3 seconds]\n"
        f"{mood_prefix}{opening}\n\n"
        f"[BODY]\n"
        f"{body_lines[0]}\n\n"
        f"[CTA]\n"
        f"{cta}"
    )

    hashtags = [
        "#fyp",
        "#foryoupage",
        f"#{profile.archetype.value}",
        "#contentcreator",
        "#viral",
        "#realtalk",
        "#creatoreconomy",
    ]

    return GeneratedContent(
        platform=Platform.TIKTOK,
        content_text=script,
        hashtags=hashtags,
        metadata={"suggested_sound": "trending", "format": "talking_head_or_b_roll"},
    )


def generate_instagram_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate an Instagram caption with story-driven narrative and save-worthy CTA."""
    topic = _extract_topic(upload)
    opening = _ENGINE.get_opening(profile.archetype, topic)
    mood_prefix = _ENGINE.get_mood_prefix(profile.mood)
    closer = _ENGINE.get_closer(profile.language_style)

    raw = upload.raw_content[:300] if len(upload.raw_content) > 300 else upload.raw_content

    archetype_cta = {
        Archetype.EDUCATOR: "Save this post for the next time you need it. And share it with someone who does.",
        Archetype.ENTERTAINER: "Double tap if this hit different 💛 Tag someone who needs to see this.",
        Archetype.DISRUPTOR: "Save this before it challenges someone powerful enough to have it removed.",
        Archetype.BUILDER: "Follow the build. I share every step.",
        Archetype.SAGE: "Save this. Read it again on a hard day.",
        Archetype.CREATOR: "Save to revisit the process. New work drops every week.",
        Archetype.CONNECTOR: "Tag the person who introduced you to something important this year.",
        Archetype.PROVOCATEUR: "Agree or disagree — I want to hear it. Drop it in the comments.",
        Archetype.MENTOR: "Save this. Share it with someone younger than you who needs to hear it.",
        Archetype.VISIONARY: "Follow — I'm mapping where this is all going.",
    }
    cta = archetype_cta.get(profile.archetype, "Save and share.")

    caption = (
        f"{mood_prefix}{opening}\n\n"
        f"{raw}\n\n"
        f"{closer}\n\n"
        f"—\n{cta}"
    )

    hashtags = [
        f"#{profile.archetype.value}",
        "#instagram",
        "#contentcreator",
        "#mindset",
        "#growth",
        "#reels",
        "#instadaily",
        "#motivation",
        "#success",
        "#entrepreneur",
        "#creative",
        "#community",
        "#instagood",
        "#inspiration",
        "#realness",
    ]

    return GeneratedContent(
        platform=Platform.INSTAGRAM,
        content_text=caption,
        hashtags=hashtags,
        metadata={"format": "feed_post_or_reel", "cta_type": "save"},
    )


def generate_facebook_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a warm, community-oriented Facebook post with shareable angle."""
    topic = _extract_topic(upload)
    opening = _ENGINE.get_opening(profile.archetype, topic)
    raw = upload.raw_content[:400] if len(upload.raw_content) > 400 else upload.raw_content

    archetype_conversation_starter = {
        Archetype.EDUCATOR: f"What's one thing about {topic} that surprised you when you first learned it?",
        Archetype.ENTERTAINER: "Who else has felt exactly like this? Drop a 🙌 below.",
        Archetype.DISRUPTOR: f"What's the biggest myth about {topic} you've had to unlearn?",
        Archetype.BUILDER: "What are you building right now? Share it below — I read every comment.",
        Archetype.SAGE: "What's the most important thing you know now that you didn't know 5 years ago?",
        Archetype.CREATOR: "What are you creating this week? Drop it below — let's support each other.",
        Archetype.CONNECTOR: "Who is someone in your network who deserves a shout-out today? Tag them.",
        Archetype.PROVOCATEUR: f"Do you agree, or do you think I've got {topic} completely wrong?",
        Archetype.MENTOR: "What's the best advice you ever received? Share it below for someone who needs it.",
        Archetype.VISIONARY: f"Where do you think {topic} is headed in the next 3 years?",
    }
    question = archetype_conversation_starter.get(profile.archetype, "What do you think?")

    post_text = (
        f"{opening}\n\n"
        f"{raw}\n\n"
        f"—\n"
        f"{question}\n\n"
        f"Share this with someone in your world who needs to read it today. 💙"
    )

    return GeneratedContent(
        platform=Platform.FACEBOOK,
        content_text=post_text,
        hashtags=[],
        metadata={"format": "text_post_or_link", "engagement_type": "conversation"},
    )


def generate_linkedin_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a LinkedIn thought-leadership post with professional insight and SEO keywords."""
    topic = _extract_topic(upload)
    raw = upload.raw_content[:500] if len(upload.raw_content) > 500 else upload.raw_content

    archetype_linkedin_frame = {
        Archetype.EDUCATOR: f"Most professionals misunderstand {topic}. Here's the breakdown that changes everything:",
        Archetype.ENTERTAINER: f"I took an unconventional approach to {topic} — here's what happened:",
        Archetype.DISRUPTOR: f"The conventional wisdom on {topic} is holding you back. Here's why:",
        Archetype.BUILDER: f"I built {topic} from scratch. Here's the exact system I used:",
        Archetype.SAGE: f"After years in this field, here's what I've learned about {topic} that nobody writes about:",
        Archetype.CREATOR: f"The creative process behind {topic} — what it actually takes:",
        Archetype.CONNECTOR: f"The best opportunities I've seen in {topic} came through one thing: the right relationships.",
        Archetype.PROVOCATEUR: f"The {topic} playbook everyone follows is outdated. Here's the honest take:",
        Archetype.MENTOR: f"I've mentored hundreds of people navigating {topic}. This is what actually moves the needle:",
        Archetype.VISIONARY: f"The future of {topic} is being written right now — most people aren't paying attention.",
    }
    opening = archetype_linkedin_frame.get(profile.archetype, f"Here's what I know about {topic}:")

    post_text = (
        f"{opening}\n\n"
        f"{raw}\n\n"
        f"What's your experience with this? I'd value your perspective in the comments."
    )

    hashtags = [
        f"#{topic.replace(' ', '').lower()[:20]}",
        f"#{profile.archetype.value}mindset",
        "#leadership",
        "#growth",
        "#professional",
    ]

    return GeneratedContent(
        platform=Platform.LINKEDIN,
        content_text=post_text,
        hashtags=hashtags,
        metadata={"format": "text_post", "tone": "thought_leadership"},
    )


def generate_youtube_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a YouTube video title, description, chapters outline, and tags."""
    topic = _extract_topic(upload)
    raw = upload.raw_content

    archetype_title_frames = {
        Archetype.EDUCATOR: f"The Complete {topic} Guide (Everything They Don't Teach You)",
        Archetype.ENTERTAINER: f"I Tried {topic} For 30 Days — Here's What Actually Happened",
        Archetype.DISRUPTOR: f"The TRUTH About {topic} (Why Everyone Is Getting This Wrong)",
        Archetype.BUILDER: f"How I Built {topic} From Scratch — Full Breakdown",
        Archetype.SAGE: f"What {topic} Taught Me After {10} Years (Deep Dive)",
        Archetype.CREATOR: f"The Full Creative Process: How I Made {topic}",
        Archetype.CONNECTOR: f"Inside The Community That Changed {topic} Forever",
        Archetype.PROVOCATEUR: f"Why {topic} Is A Lie (Unpopular Opinion)",
        Archetype.MENTOR: f"Everything I Wish I Knew About {topic} (For Beginners & Beyond)",
        Archetype.VISIONARY: f"The Future Of {topic} — What's Coming That Nobody Is Talking About",
    }
    title = archetype_title_frames.get(profile.archetype, f"Deep Dive Into {topic}")

    description = (
        f"{title}\n\n"
        f"{'=' * 50}\n"
        f"In this video:\n{raw[:300]}\n\n"
        f"{'=' * 50}\n"
        f"CHAPTERS:\n"
        f"0:00 — Introduction\n"
        f"1:30 — The setup and context\n"
        f"5:00 — The core insight\n"
        f"12:00 — How to apply this\n"
        f"18:00 — Real-world examples\n"
        f"24:00 — Key takeaways\n"
        f"26:00 — What to do next\n\n"
        f"{'=' * 50}\n"
        f"Subscribe for more: New videos every week.\n"
        f"Leave a comment — I read and respond to everything."
    )

    tags = [
        topic,
        profile.archetype.value,
        "how to",
        "tutorial",
        "deep dive",
        "strategy",
        "2024",
        "creator economy",
        "content creation",
        "social media",
    ]

    return GeneratedContent(
        platform=Platform.YOUTUBE,
        content_text=description,
        hashtags=[f"#{t.replace(' ', '')}" for t in tags[:5]],
        metadata={
            "title": title,
            "tags": tags,
            "format": "long_form_video",
            "seo_optimised": True,
        },
    )


def generate_fiverr_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a Fiverr gig description with credibility bullets and testimonial angle."""
    topic = _extract_topic(upload)
    raw = upload.raw_content[:300] if len(upload.raw_content) > 300 else upload.raw_content

    archetype_value_prop = {
        Archetype.EDUCATOR: f"I don't just deliver — I explain. Every deliverable comes with clear context so you understand the strategy behind it.",
        Archetype.ENTERTAINER: f"I make your brand impossible to ignore. Engaging, memorable, and designed to stop the scroll.",
        Archetype.DISRUPTOR: f"I don't do safe, forgettable work. I challenge your brief to produce something that actually moves the needle.",
        Archetype.BUILDER: f"I build systems, not just deliverables. Every piece of work integrates into a larger architecture.",
        Archetype.SAGE: f"Years of hard-won expertise, distilled into exactly what your project needs.",
        Archetype.CREATOR: f"Every project gets my full creative investment. Craft, not templates.",
        Archetype.CONNECTOR: f"I don't work for clients, I work with them. Collaboration and communication are built in.",
        Archetype.PROVOCATEUR: f"I give you the honest take, not the comfortable one. That's why the work performs.",
        Archetype.MENTOR: f"I guide you through the process so you come out understanding it — not just receiving a file.",
        Archetype.VISIONARY: f"I don't just solve today's problem. I build with tomorrow in mind.",
    }
    value_prop = archetype_value_prop.get(profile.archetype, "I deliver exceptional work, on time, every time.")

    gig_text = (
        f"✅ WHAT YOU GET:\n{raw}\n\n"
        f"💡 MY APPROACH:\n{value_prop}\n\n"
        f"🏆 WHY THIS WORKS:\n"
        f"• Tailored to your specific goals and audience\n"
        f"• Built on proven frameworks that drive results\n"
        f"• Delivered with full transparency and context\n"
        f"• Revision-friendly process — we get it right\n\n"
        f"📩 Message me before ordering — I want to make sure this is the perfect fit for your project."
    )

    return GeneratedContent(
        platform=Platform.FIVERR,
        content_text=gig_text,
        hashtags=[],
        metadata={"format": "gig_description", "cta": "message_first"},
    )


def generate_x_content(
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Generate a punchy X/Twitter thread with strong first tweet and engagement question."""
    topic = _extract_topic(upload)
    raw = upload.raw_content

    archetype_thread_opener = {
        Archetype.EDUCATOR: f"A thread on {topic} that will change how you work: 🧵",
        Archetype.ENTERTAINER: f"{topic} just broke everything. Thread: 🧵",
        Archetype.DISRUPTOR: f"The {topic} consensus is wrong. Here's the real story: 🧵",
        Archetype.BUILDER: f"How I built {topic}. Full breakdown, nothing held back: 🧵",
        Archetype.SAGE: f"What {topic} actually teaches you. Wisdom thread: 🧵",
        Archetype.CREATOR: f"Creative process thread: how {topic} gets made: 🧵",
        Archetype.CONNECTOR: f"People worth following in {topic}. A connector thread: 🧵",
        Archetype.PROVOCATEUR: f"Hot take on {topic}. I said what I said: 🧵",
        Archetype.MENTOR: f"For everyone figuring out {topic}. Read this thread: 🧵",
        Archetype.VISIONARY: f"The future of {topic} is already here. Thread: 🧵",
    }
    opener = archetype_thread_opener.get(profile.archetype, f"{topic} — a thread: 🧵")

    sentences = [s.strip() for s in raw.replace("\n", " ").split(".") if s.strip()]
    tweet_bodies = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) < 240:
            current = (current + ". " + sentence).strip()
        else:
            if current:
                tweet_bodies.append(current + ".")
            current = sentence
    if current:
        tweet_bodies.append(current + ".")

    tweet_bodies = tweet_bodies[:5]

    archetype_closing_question = {
        Archetype.EDUCATOR: f"What's your biggest misconception about {topic} that you had to unlearn?",
        Archetype.ENTERTAINER: "Which tweet hit hardest? RT the one that got you.",
        Archetype.DISRUPTOR: "Disagree with any of this? Good. Tell me where I'm wrong.",
        Archetype.BUILDER: "What are you building right now? Drop it below.",
        Archetype.SAGE: "What's the most important thing you know about this that I didn't mention?",
        Archetype.CREATOR: "What are you creating this week? Let's talk about it.",
        Archetype.CONNECTOR: "Who else should be in this conversation? Tag them.",
        Archetype.PROVOCATEUR: "Agree or disagree — and why. No wishy-washy takes.",
        Archetype.MENTOR: "What's one thing you'd add for someone just starting out?",
        Archetype.VISIONARY: "Where do you see this going? I want to hear your prediction.",
    }
    closing_q = archetype_closing_question.get(profile.archetype, "What did you take from this?")

    thread_parts = [f"1/ {opener}"]
    for i, body in enumerate(tweet_bodies, 2):
        thread_parts.append(f"{i}/ {body}")
    thread_parts.append(f"{len(thread_parts) + 1}/ {closing_q}")

    full_thread = "\n\n".join(thread_parts)

    return GeneratedContent(
        platform=Platform.X,
        content_text=full_thread,
        hashtags=[f"#{profile.archetype.value}", "#thread"],
        metadata={"format": "thread", "tweet_count": len(thread_parts)},
    )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_GENERATORS = {
    Platform.TIKTOK: generate_tiktok_content,
    Platform.INSTAGRAM: generate_instagram_content,
    Platform.FACEBOOK: generate_facebook_content,
    Platform.LINKEDIN: generate_linkedin_content,
    Platform.YOUTUBE: generate_youtube_content,
    Platform.FIVERR: generate_fiverr_content,
    Platform.X: generate_x_content,
}


def generate_for_platform(
    platform: Platform,
    profile: PersonalityProfile,
    upload: ContentUpload,
    story_context: str,
) -> GeneratedContent:
    """Dispatch content generation to the correct platform generator."""
    generator = _GENERATORS.get(platform)
    if generator is None:
        raise ValueError(f"No generator registered for platform: {platform}")
    return generator(profile, upload, story_context)
