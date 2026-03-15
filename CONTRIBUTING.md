# Contributing to 4x-game-agent

Thank you for your interest in contributing! This project welcomes contributions
of all kinds — new game implementations, core improvements, bug fixes, and documentation.

## Ways to Contribute

### 1. Add a New Game (Most Valuable!)

The easiest and most impactful contribution is adding support for a new 4X strategy game.

```bash
# 1. Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/4x-game-agent.git
cd 4x-game-agent

# 2. Copy the template
cp -r games/_template games/your_game

# 3. Customize for your game (see games/_template/README.md)

# 4. Test it
cd games/your_game
python main.py --test
```

What you need:
- The game running on an Android emulator (BlueStacks, LDPlayer, etc.)
- ADB connected to the emulator
- Screenshots of key game screens for coordinate mapping

### 2. Add a New LLM Backend

Currently we support Claude (Anthropic). Want to add OpenAI GPT-4V, Gemini, or local models?
Edit `agent/llm.py` and add a new provider.

### 3. Add a New Device Interface

Currently we support ADB (Android). Want to add iOS (Appium) or desktop screenshot support?
Add a new file in `agent/` following the same interface as `agent/adb.py`.

### 4. Improve Core Utilities

The `agent/` package contains game-agnostic tools. Improvements here benefit all games:
- Better OCR accuracy
- Faster template matching
- Dashboard enhancements
- New utility functions

## Development Setup

```bash
# Install in development mode
pip install -e ".[all,dev]"

# Run tests
pytest agent/tests/

# Run linter
ruff check .
```

## Pull Request Process

1. Fork the repo and create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Test your changes: `pytest` and manual testing with your game
4. Commit with a clear message: `feat: add Evony game support`
5. Push and open a PR

## Commit Messages

Use conventional commits:
- `feat:` — new feature or game
- `fix:` — bug fix
- `docs:` — documentation only
- `chore:` — maintenance, CI, tooling

## Code Style

- Python 3.9+ compatible
- Use type hints for function signatures
- Keep game-specific code in `games/your_game/`, NOT in `agent/`
- No game logic in `agent/` — it should stay game-agnostic

## Questions?

Open an issue with the `question` label. We're happy to help!
