# I built an AI that plays mobile strategy games for $0.01/hour (open source)

I've been working on an AI bot that plays 4X mobile strategy games (think Rise of Kingdoms, Evony, Lords Mobile) — and I open-sourced it as a framework so anyone can add their own game.

## What it does

The bot automates the repetitive parts of 4X games:
- Keeps builders, research, and troop training queues active 24/7
- Collects resources automatically
- Handles alliance help and donations
- Pushes conquest stages
- Dismisses popups (those annoying purchase offers)
- Reviews strategy with AI every 30 minutes

## The interesting part: it barely uses AI

Most game bots either use hardcoded pixel matching (fragile) or send every screenshot to an AI (expensive). Mine does both:

- **98% of decisions** are local: pixel-based screen detection (<100ms), PaddleOCR for reading numbers, scripted tap sequences for known workflows
- **2% of decisions** use Claude AI: strategic reviews every 30 min, and step-by-step guidance when scripted workflows fail

This keeps the cost at **~$0.01/hour** instead of $1+/hour for pure AI.

## Cool technical bits

- **Pixel screen classifier**: Checks colors at fixed positions to identify screens in <50ms. No OCR needed to know if you're on the home screen vs a popup.
- **Self-improving building finder**: Uses OpenCV template matching + position caching. First time finding a building is slow. Every time after is instant.
- **Self-reflection**: Logs what works and what fails. Before retrying a task, checks past failures to avoid repeating mistakes.
- **World model with timer predictions**: Tracks when builders/research will finish, so the bot acts at exactly the right moment instead of polling.

## Want to try it?

It's designed as a framework — each game is a separate folder. The reference implementation is for Kingshot, but the template makes it easy to add any similar game.

**GitHub**: https://github.com/sonpiaz/4x-game-agent (MIT license)

Looking for people who play RoK, Evony, or Lords Mobile to add those games. The hardest part is mapping the UI coordinates — the framework handles everything else.
