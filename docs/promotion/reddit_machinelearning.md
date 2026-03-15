# [P] 4x-game-agent: LLM-powered bot framework for mobile strategy games — 99% cheaper than pure LLM approach

I built an open-source framework for creating AI bots that play 4X mobile strategy games (Rise of Kingdoms, Evony, Lords Mobile, etc.) using a hybrid architecture that combines local perception with LLM vision.

## The Problem

Using LLM vision APIs for every game decision is absurdly expensive:
- Screenshot every 3s → 1,200 API calls/hour
- Claude Haiku at ~$0.001/call = **$1.20/hour = $864/month**
- Claude Sonnet at ~$0.004/call = **$4.80/hour = $3,456/month**

## The Solution: 5-Layer Hybrid Architecture

```
Layer 5: STRATEGIC AI ──── LLM vision (every 30 min, ~$0.004)
Layer 4: WORKFLOWS ─────── Scripted tap sequences (FREE)
Layer 3: WORLD MODEL ───── Timer predictions (FREE)
Layer 2: STATE MACHINE ─── Screen detection + popups (FREE)
Layer 1: PERCEPTION ────── Pixel classify <100ms + PaddleOCR (FREE)
```

98% of decisions are handled locally for free. LLM only steps in for strategic reviews (every 30 min) and rare fallbacks when scripted workflows fail.

**Result: ~$0.01/hour ($7/month) vs $1+/hour for pure LLM.**

## How It Works

1. **Pixel-based screen classification** (<100ms) — no OCR needed to know what screen you're on
2. **PaddleOCR** reads game state (power, gems, timers) every 60s — all local, no API
3. **World model** tracks building timers, research queues, training — predicts when to act
4. **Scripted workflows** execute deterministic tap sequences with screen verification
5. **OpenCV template matching** auto-discovers building positions (Voyager-inspired skill library)
6. **Claude Sonnet** reviews strategy every 30 min — big-picture corrections only
7. **Claude Haiku** guides step-by-step taps only when workflows fail

## Framework Design

The core is intentionally thin — just 6 game-agnostic utilities (ADB, OCR, template matching, reflection log, LLM wrapper, dashboard). Each game is a self-contained folder with its own FSM, world model, workflows, and coordinates. Want to add a new game? Copy the template folder and customize.

## Results (Kingshot — reference implementation)

- Screen classification: 30-50ms (was 15-20s with OCR)
- Cycles per minute: ~12 (was ~3)
- Cost: ~$0.01/hr running 24/7
- Auto-discovers and caches building positions over time
- Self-reflection: logs failures and avoids repeating mistakes

## Links

- **GitHub**: https://github.com/sonpiaz/4x-game-agent
- **License**: MIT

Looking for contributors, especially anyone who plays Rise of Kingdoms, Evony, or Lords Mobile and wants to add their game!

## Technical Details

- Python 3.9+
- PaddleOCR for local text reading
- OpenCV for template matching and pixel analysis
- Claude API (Anthropic) for vision — planning to add OpenAI GPT-4V support
- ADB for Android emulator control (BlueStacks, LDPlayer, etc.)
