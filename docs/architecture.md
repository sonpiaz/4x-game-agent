# Architecture

## Overview

4x-game-agent uses a layered architecture that minimizes expensive LLM API calls
by handling most decisions locally with free, fast methods.

```
┌─────────────────────────────────────────────────┐
│  LAYER 5: STRATEGIC AI (LLM, every 30 min)      │  ~$0.004/call
│  Big-picture review, goal adjustment             │
├─────────────────────────────────────────────────┤
│  LAYER 4: WORKFLOW ENGINE (Scripted, FREE)       │
│  Deterministic tap sequences with verification   │
├─────────────────────────────────────────────────┤
│  LAYER 3: WORLD MODEL (Persistent, FREE)         │
│  Timer tracking, building state, predictions     │
├─────────────────────────────────────────────────┤
│  LAYER 2: STATE MACHINE (FSM, FREE)              │
│  Screen detection, popup handling, navigation    │
├─────────────────────────────────────────────────┤
│  LAYER 1: LOCAL PERCEPTION (OCR + Pixels, FREE)  │
│  PaddleOCR text reading, pixel-based classify    │
└─────────────────────────────────────────────────┘
```

## Cost Model

| Approach | Cost/Hour | Cost/Month |
|----------|-----------|------------|
| Pure LLM (every 3s) | ~$1.00 | ~$720 |
| Hybrid (LLM as fallback) | ~$0.07 | ~$50 |
| Full local + rare LLM | ~$0.01 | ~$7 |

This framework targets the **$0.01/hr** range by using LLM only for:
- Strategic reviews (every 30 min)
- Fallback when scripted workflows fail

## Core Utilities (`agent/`)

Game-agnostic tools shared by all game implementations:

| Module | Purpose |
|--------|---------|
| `adb.py` | ADB screenshot + tap/swipe interface |
| `ocr.py` | PaddleOCR text reading wrapper |
| `template_match.py` | OpenCV visual element matching |
| `reflection.py` | Success/failure learning log |
| `llm.py` | LLM vision API wrapper (Claude) |
| `dashboard.py` | Real-time web monitoring UI |

## Game Implementations (`games/`)

Each game is a self-contained folder with ALL game-specific logic:

```
games/your_game/
├── main.py              # Entry point
├── config.yaml          # Settings
├── engine.py            # Main bot loop
├── state_machine.py     # Screen states + popup handling
├── world_model.py       # Persistent game state + timers
├── workflow_engine.py   # Tap sequences for each task
├── screen_analyzer.py   # Screen detection rules
├── coordinate_map.py    # UI element positions
├── knowledge.py         # Game data (prerequisites, strategies)
├── prompts.py           # LLM prompts (strategic + tactical)
└── building_finder.py   # Auto-discover building positions
```

## Design Principles

1. **Core is thin** — Only game-agnostic utilities in `agent/`. No game logic.
2. **Games are disposable** — Delete a game folder and start fresh. No side effects.
3. **Local first** — Use free local methods (OCR, pixels, templates) before paid APIs.
4. **Config-driven** — Game settings in YAML, not hardcoded in Python.
5. **Self-improving** — Reflection log + template capture = bot gets better over time.
