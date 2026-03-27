# Creator AI — Social Media Content Engine

A multi-layer FastAPI application that builds your personality archetype, ingests raw content, generates platform-native posts, schedules intelligently, responds in your voice, and alerts you to high-intent audience members.

---

## Architecture

The system is built as a stack of specialised layers, each unlocked by subscription tier:

| Layer | Name | Description |
|---|---|---|
| **1** | Personality Archive | 10-question archetype quiz, language style, tone, mood profile |
| **2** | The Brain (Input Engine) | Content ingestion, adaptive intake questions, story context |
| **2.5** | Personal Creative Analytics | Productivity peaks, mood-quality correlation, content patterns |
| **3** | Platform Mini Apps | Archetype-voiced generators for TikTok, Instagram, Facebook, LinkedIn, YouTube, Fiverr, X |
| **4** | Intelligent Sequencer | Narrative-synced scheduling across platforms |
| **5** | Live Response Engine | 3-step archetype responses to comments and DMs |
| **6** | Interest Alert System | Weighted interaction scoring, creator alerts at threshold |
| **6.5** | Audience Engagement Intelligence | Platform performance analysis, high-intent segmentation, strategy recommendations |

---

## 10 Archetypes

| Archetype | Tagline |
|---|---|
| Educator | teaches, illuminates, transforms understanding |
| Entertainer | captivates, energises, makes the world more alive |
| Disruptor | challenges, exposes, rebuilds from the ground up |
| Builder | creates systems, executes relentlessly, documents the journey |
| Sage | distils wisdom, sees patterns, speaks timeless truth |
| Creator | crafts beauty, channels expression, makes the unseen visible |
| Connector | bridges worlds, builds community, makes everyone belong |
| Provocateur | challenges comfort, sparks debate, refuses the safe take |
| Mentor | guides, transforms, sees potential others miss |
| Visionary | sees the future, maps the shift, pulls people forward |

---

## Pricing Tiers

| Tier | Price | Layers |
|---|---|---|
| **Foundation** | $9.99/mo | Layer 1, 2 |
| **Creator** | $24.99/mo | Layers 1, 2, 2.5 |
| **Professional** | $49.99/mo | Layers 1, 2, 2.5, 3 |
| **Enterprise** | $99.99/mo | All layers |

---

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the API server
uvicorn src.creator_ai.main:app --reload

# Run tests
pytest
```

The API docs are available at `http://localhost:8000/docs` once the server is running.

---

## Project Structure

```
src/creator_ai/
├── main.py                    # FastAPI app entrypoint
├── pricing.py                 # Tier definitions and access control
├── models/
│   ├── archetypes.py          # 10 archetypes + metadata
│   ├── personality.py         # Quiz, language style, tone, mood, profile
│   ├── content.py             # Content upload, Brain session, generated content
│   └── engagement.py         # Interaction scoring models
├── layers/
│   ├── layer1_personality.py  # Personality Archive
│   ├── layer2_brain.py        # Input Engine / The Brain
│   ├── layer2_5_analytics.py  # Personal Creative Analytics
│   ├── layer3_mini_apps.py    # Platform Mini Apps
│   ├── layer4_sequencer.py    # Intelligent Sequencing
│   ├── layer5_response.py     # Live Response Engine
│   ├── layer6_alerts.py       # Interest Alert System
│   └── layer6_5_intelligence.py # Audience Engagement Intelligence
└── routers/
    ├── personality.py          # GET/POST /personality/*
    ├── brain.py                # POST /brain/*
    ├── content.py              # POST /content/generate
    ├── sequencer.py            # POST /schedule
    ├── response.py             # POST /response/generate
    └── alerts.py               # GET/POST /alerts/* and /analytics/*
tests/
├── test_layer1_personality.py
├── test_layer2_brain.py
├── test_layer3_mini_apps.py
├── test_layer6_alerts.py
└── test_pricing.py
```

---

## API Endpoints

### Personality (Layer 1)
- `GET /personality/quiz` — Return 10 archetype quiz questions
- `POST /personality/quiz/submit` — Submit answers, get archetype + scores
- `POST /personality/profile` — Create full personality profile
- `GET /personality/archetypes` — List all 10 archetypes with metadata
- `PUT /personality/profile/mood` — Update mood for the day

### Brain (Layer 2)
- `POST /brain/session` — Create a new Brain session
- `POST /brain/upload` — Upload content to a Brain session
- `GET /brain/session/{id}/questions` — Get adaptive intake questions
- `POST /brain/session/{id}/answers` — Submit intake answers
- `GET /brain/session/{id}/context` — Get current story context

### Content (Layer 3)
- `POST /content/generate` — Generate content for specified platforms
- `GET /content/{id}` — Get generated content by ID
- `GET /content/platforms/list` — List available platforms

### Sequencer (Layer 4)
- `POST /schedule` — Schedule content for deployment
- `GET /schedule/optimal` — Get optimal posting times

### Response (Layer 5)
- `POST /response/generate` — Generate response to a comment/DM
- `POST /response/intent` — Parse intent of incoming interaction

### Alerts & Analytics (Layers 6 & 6.5)
- `POST /alerts/score` — Score a new interaction
- `GET /alerts/engagement/{user_id}` — Get engagement score
- `GET /alerts/high-intent` — Get high-intent engager list
- `GET /analytics/platform-performance` — Platform performance analysis
- `GET /analytics/recommendations` — Strategy recommendations