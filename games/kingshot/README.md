# Kingshot — Reference Implementation

The first and fully working game implementation for 4x-game-agent.

## Game Info

- **Game**: Kingshot (4X mobile strategy)
- **Platform**: Android (BlueStacks emulator)
- **Resolution**: 1440x2560 (portrait)
- **Account**: TC9, F2P, Kingdom #892

## Features

- Auto-upgrade buildings (TC rush path TC9 → TC13)
- Auto-research (economy tree priority)
- Auto-train troops (all 3 military buildings)
- Auto-collect resources (sweep-tap base)
- Auto-alliance help + donate
- Auto-conquest push
- Popup auto-dismiss (quit dialog, top-up offers)
- Building auto-discovery (template matching + city exploration)
- Self-reflection (learn from failures)
- Web dashboard at `localhost:8080`

## Architecture

```
STRATEGIST (Claude Sonnet, every 30 min) — big-picture review
EXECUTOR (Verified Workflows, FREE) — deterministic tap sequences
BUILDING FINDER (OpenCV + Exploration, FREE) — template + cached + spiral + explore
SENTINEL (Every 5s, FREE) — pixel-based screen classify (<100ms)
WORLD MODEL (Persistent, FREE) — buildings, timers, resources, cached positions
```

## Running

```bash
export ANTHROPIC_API_KEY='sk-ant-...'  # Optional
cd games/kingshot
python main.py --test       # Test ADB + OCR
python main.py --calibrate  # One-time building discovery
python main.py              # Run bot
```

## Cost

~$0.01/hour ($7/month) running 24/7.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `config.yaml` | All settings |
| `engine.py` | V8 engine (main loop) |
| `state_machine.py` | FSM (screen states, popup handling) |
| `world_model.py` | Persistent game state + timer sync |
| `workflow_engine.py` | Tap sequences for each task |
| `screen_analyzer.py` | Pixel-based screen classifier |
| `ocr.py` | Game-specific OCR parsing |
| `coordinate_map.py` | UI element positions |
| `building_finder.py` | 4-strategy building discovery |
| `knowledge.py` | TC prerequisites, strategies, hero data |
| `prompts.py` | Claude API prompts (strategic + tactical) |
| `strategy.py` | Game strategy knowledge + memory |

## Critical Rules

- **NEVER** use `actions.back()` — triggers "Quit Game?" dialog in Kingshot
- **NEVER** trust OCR values from non-home screens
- Workflows must verify screen type at checkpoints
- Fast pixel classify is primary — OCR fallback only for ambiguous screens
