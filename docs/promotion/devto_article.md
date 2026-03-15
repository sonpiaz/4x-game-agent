---
title: "How I Built a Game Bot That Uses LLM Vision for $0.01/Hour (Not $1/Hour)"
published: false
tags: ai, gamedev, python, opensource
---

Most tutorials about using LLMs for game automation show you how to send screenshots to GPT-4 or Claude every few seconds. It works — but at $1+/hour, you'll burn through hundreds of dollars a month.

I built a framework that gets the same results for **$0.01/hour**. Here's how.

## The Expensive Way

```
Every 3 seconds:
  1. Take screenshot
  2. Send to Claude: "What should I do?"
  3. Parse response
  4. Execute action
  5. Repeat

Cost: ~1,200 API calls/hour × $0.001 = $1.20/hour
```

This is how most LLM game agents work. It's simple, but the cost adds up fast — especially if you want to run 24/7.

## The Cheap Way: 5-Layer Hybrid Architecture

The insight is that **98% of game decisions don't need AI**. You can handle them locally, for free:

```
Layer 5: STRATEGIC AI ──── LLM reviews strategy every 30 min ($0.004)
Layer 4: WORKFLOWS ─────── Scripted tap sequences (FREE)
Layer 3: WORLD MODEL ───── Tracks timers and predicts events (FREE)
Layer 2: STATE MACHINE ─── Detects screens and handles popups (FREE)
Layer 1: PERCEPTION ────── Pixel analysis + OCR (FREE)
```

### Layer 1: Perception (FREE, <100ms)

Instead of asking an AI "what screen is this?", I check pixel colors at known positions:

- Bottom navigation bar is dark with colored icons? → Home screen
- Dark overlay with bright center? → Popup
- Bright panel in lower half? → Building menu

This takes **30-50ms** vs 15-20 seconds for full OCR.

For the 20% of cases where pixels aren't enough, PaddleOCR runs locally to read text. Still free — no API calls.

### Layer 2: State Machine (FREE)

A simple FSM tracks which screen the bot is on. Popups are managed with a stack — when one appears, the previous state is pushed. When dismissed, it pops back.

This handles the #1 frustration with game bots: random purchase popups interrupting your workflow.

### Layer 3: World Model (FREE)

Instead of re-discovering game state every cycle, the bot **remembers**:
- Which buildings are upgrading and when they finish
- Whether research is active
- Which troop training queues are idle

It predicts timer completions and acts at exactly the right moment — no polling.

### Layer 4: Workflows (FREE)

Known tasks are scripted as deterministic tap sequences:

```python
def upgrade_building(self, name):
    self.ensure_home()           # Navigate to home screen
    self.find_and_tap(name)      # Template match → cached pos → spiral search
    self.tap(720, 2100)          # Tap upgrade button
    self.tap(720, 1500)          # Confirm
    self.world.observe_upgrade_started(name)
    self.ensure_home()
```

Each step verifies the screen state before proceeding. If something unexpected happens, it falls back to Layer 5.

### Layer 5: Strategic AI ($0.004 every 30 min)

Claude Sonnet reviews a screenshot and answers: "What's the most important thing to do right now?"

This catches things the scripted workflows can't:
- Builders are idle but the bot didn't notice
- A new event started that changes priorities
- The current strategy needs adjustment

Cost: ~48 calls/day × $0.004 = **$0.19/day**.

## Self-Improving: The Bot Gets Better Over Time

Two patterns borrowed from AI research:

**Template Capture (Voyager-inspired):** When the bot finds a building, it captures a screenshot snippet as a template. Next time, OpenCV template matching finds it instantly instead of searching.

**Self-Reflection (CRADLE/Reflexion-inspired):** Every success and failure is logged. Before retrying a task, the bot checks past failures to avoid repeating mistakes.

## The Framework

I packaged this as an open-source framework where each game is a self-contained folder:

```
4x-game-agent/
├── agent/              # Core utilities (ADB, OCR, template matching, LLM)
├── games/
│   ├── kingshot/       # Reference implementation (fully working)
│   └── _template/      # Copy to add your game
└── docs/
```

The core is intentionally thin — just utilities. All game logic (screen states, workflows, coordinates, strategies) lives in the game folder. Wrong approach? Delete the folder and start over.

## Getting Started

```bash
git clone https://github.com/sonpiaz/4x-game-agent.git
cd 4x-game-agent
pip install -e ".[all]"

# Test with Kingshot (or copy _template for your game)
cd games/kingshot
python main.py --test
```

## Contributing

The most valuable contribution is adding a new game. The framework handles the hard parts (ADB, OCR, template matching, LLM integration). You just need to:

1. Map UI coordinates for your game
2. Write screen detection rules
3. Script the tap workflows
4. Define game knowledge (upgrade prerequisites, etc.)

**GitHub**: [github.com/sonpiaz/4x-game-agent](https://github.com/sonpiaz/4x-game-agent)

Games we're looking for: Rise of Kingdoms, Evony, Lords Mobile, Call of Dragons, Whiteout Survival.

---

*Have questions? Open an issue on GitHub or drop a comment below.*
