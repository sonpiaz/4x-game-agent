# Game Name — 4x-game-agent Implementation

## Quick Start

1. Copy this template:
   ```bash
   cp -r games/_template games/your_game
   ```

2. Edit `config.yaml` with your game's settings

3. Map your game's UI coordinates in `coordinate_map.py`

4. Define game knowledge in `knowledge.py`

5. Write screen detection rules in `screen_analyzer.py`

6. Implement workflows in `workflow_engine.py`

7. Test:
   ```bash
   cd games/your_game
   python main.py --test
   ```

## Files to Customize

| File | Purpose | Priority |
|------|---------|----------|
| `config.yaml` | Game settings, API models, timing | Must |
| `coordinate_map.py` | UI button/building positions | Must |
| `knowledge.py` | Game data (prerequisites, strategies) | Must |
| `screen_analyzer.py` | Detect which screen the bot is on | Must |
| `state_machine.py` | Define game states and popup handling | Must |
| `workflow_engine.py` | Tap sequences for each task | Must |
| `world_model.py` | Track persistent game state | Should |
| `prompts.py` | LLM prompts for strategic/tactical AI | Optional |
| `building_finder.py` | Auto-discover building positions | Optional |

## Architecture Pattern

```
Your game folder is self-contained. It imports only from agent/:

    from agent.adb import GameScreen, GameActions
    from agent.ocr import OCREngine
    from agent.template_match import TemplateMatcher
    from agent.reflection import ReflectionLog
    from agent.llm import LLMVision
    from agent.dashboard import BotLogger, start_dashboard
```

All game logic (FSM, world model, workflows, screen detection) lives here.
If something is wrong, delete this folder and start fresh.
