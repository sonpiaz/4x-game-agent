# 4x-game-agent

## What This Is

LLM-powered AI agent framework for 4X mobile strategy games (Rise of Kingdoms, Evony,
Lords Mobile, Kingshot, etc.). Uses a layered architecture where local perception (OCR,
pixel analysis, template matching) handles 98% of decisions for free, with LLM vision
as a rare fallback.

## Project Structure

- `agent/` — Core utilities (game-agnostic). ADB, OCR, template matching, reflection, LLM wrapper, dashboard.
- `games/kingshot/` — Reference implementation (Kingshot game). All game-specific logic lives here.
- `games/_template/` — Copy this to add a new game.
- `docs/` — Architecture, adding-a-game guide, cost analysis.

## Key Rules

- **Core is thin** — `agent/` has NO game logic, only utilities. Game-specific code goes in `games/`.
- **Games are disposable** — Can delete any game folder and rebuild from scratch.
- **Local first** — Use free methods (pixels, OCR, templates) before paid LLM APIs.
- **Each game is self-contained** — Its own config, FSM, world model, workflows, coordinates.

## Running

```bash
pip install -e ".[all]"           # Install framework
cd games/kingshot && python main.py --test  # Test Kingshot
cd games/kingshot && python main.py         # Run Kingshot bot
```

## Adding a New Game

```bash
cp -r games/_template games/new_game
# Edit config.yaml, coordinate_map.py, knowledge.py, screen_analyzer.py, etc.
```

See `docs/adding-a-game.md` for full guide.

## Architecture Layers

1. **Perception** — Pixel classify (<100ms) + PaddleOCR (every 60s)
2. **State Machine** — Screen detection + popup handling (FREE)
3. **World Model** — Timer tracking + predictions (FREE)
4. **Workflows** — Scripted tap sequences (FREE)
5. **Strategic AI** — LLM review every 30 min (~$0.004/call)
