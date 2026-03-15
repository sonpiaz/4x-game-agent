# 4x-game-agent

**LLM-powered AI agent framework for 4X mobile strategy games.**

Build AI bots that play Rise of Kingdoms, Evony, Lords Mobile, Kingshot,
and other city-building strategy games — using vision + reasoning at **99% lower cost**
than pure LLM approaches.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why This Project?

Existing game bots are either:
- **Rule-based** (pixel matching, hardcoded coordinates) — fragile, no reasoning
- **Pure LLM** (send every screenshot to GPT-4/Claude) — smart but costs **$1+/hour**

This framework combines both: **local perception handles 98% of decisions for free**,
LLM vision steps in only when the bot is stuck or needs strategic planning.

| Approach | Cost/Hour | Cost/Month (24/7) |
|----------|-----------|-------------------|
| Pure LLM (every 3s) | ~$1.00 | ~$720 |
| **4x-game-agent** | **~$0.01** | **~$7** |

## Architecture

```
LAYER 5: STRATEGIC AI ──── LLM vision review (every 30 min, ~$0.004)
LAYER 4: WORKFLOWS ─────── Scripted tap sequences with verification (FREE)
LAYER 3: WORLD MODEL ───── Persistent state + timer predictions (FREE)
LAYER 2: STATE MACHINE ─── Screen detection + popup handling (FREE)
LAYER 1: PERCEPTION ────── Pixel classify (<100ms) + OCR text reading (FREE)
```

## Supported Games

| Game | Status | Contributor |
|------|--------|-------------|
| [Kingshot](games/kingshot/) | Reference implementation | [@sonpiaz](https://github.com/sonpiaz) |
| Rise of Kingdoms | Planned | [Help wanted!](../../issues/new?template=new_game.md) |
| Evony: The King's Return | Planned | [Help wanted!](../../issues/new?template=new_game.md) |
| Lords Mobile | Planned | [Help wanted!](../../issues/new?template=new_game.md) |
| Call of Dragons | Planned | [Help wanted!](../../issues/new?template=new_game.md) |

**Want to add your game?** See [Adding a New Game](docs/adding-a-game.md).

## Quick Start

### 1. Install

```bash
git clone https://github.com/sonpiaz/4x-game-agent.git
cd 4x-game-agent
pip install -e ".[all]"
```

### 2. Connect your emulator

```bash
# Start BlueStacks/LDPlayer with your game
adb devices  # Should show your emulator
```

### 3. Run the Kingshot bot (reference implementation)

```bash
export ANTHROPIC_API_KEY='sk-ant-...'  # Optional: for AI fallback
cd games/kingshot
python main.py --test   # Test connection + OCR
python main.py          # Run the bot
```

### 4. Add your own game

```bash
cp -r games/_template games/my_game
# Edit config.yaml, coordinate_map.py, knowledge.py, etc.
# See docs/adding-a-game.md for the full guide
```

## Project Structure

```
4x-game-agent/
├── agent/                  # Core utilities (game-agnostic)
│   ├── adb.py              #   ADB screenshot + tap/swipe
│   ├── ocr.py              #   PaddleOCR text reading
│   ├── template_match.py   #   OpenCV visual matching
│   ├── reflection.py       #   Success/failure learning
│   ├── llm.py              #   LLM vision API wrapper
│   └── dashboard.py        #   Web monitoring UI
│
├── games/
│   ├── kingshot/            # Reference implementation (fully working)
│   │   ├── main.py          #   Entry point
│   │   ├── config.yaml      #   Game settings
│   │   ├── engine.py        #   Bot engine
│   │   ├── coordinate_map.py #  UI positions
│   │   ├── knowledge.py     #   Game data (TC1-30 prerequisites)
│   │   └── ...              #   FSM, workflows, world model, etc.
│   │
│   └── _template/           # Copy this to start a new game
│
└── docs/
    ├── architecture.md      # How it works
    ├── adding-a-game.md     # Step-by-step guide
    └── cost-analysis.md     # Cost breakdown
```

## How It Works

1. **Take screenshot** via ADB (works with any Android emulator)
2. **Classify screen** using pixel analysis (<100ms, no API)
3. **Handle popups** automatically via FSM (tap close/cancel)
4. **Check timers** in world model (predict when builders/research finish)
5. **Execute workflows** — scripted tap sequences for upgrades, training, etc.
6. **OCR read** game state every 60s (power, gems, resources)
7. **AI review** every 30 min — Claude Sonnet checks if strategy is on track
8. **AI fallback** — if a workflow fails, Claude Haiku guides step-by-step

## Key Features

- **Multi-game framework** — plug any 4X strategy game
- **Self-improving** — learns building positions via template capture
- **Self-reflecting** — logs failures and avoids repeating mistakes
- **Config-driven** — YAML config, no code changes for tuning
- **Web dashboard** — real-time monitoring at `localhost:8080`
- **Cost-efficient** — 99% cheaper than pure LLM approaches

## Target Games

This framework works best with 4X mobile strategy games that share this gameplay loop:

> Build city → Research → Train troops → Collect resources →
> Alliance help → Hero upgrades → Events → Repeat

Examples: Rise of Kingdoms, Evony, Lords Mobile, Call of Dragons,
King of Avalon, Whiteout Survival, State of Survival, Viking Rise,
Age of Empires Mobile, Last War, Kingshot.

## Contributing

We welcome contributions! The most valuable contribution is **adding a new game**.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).
