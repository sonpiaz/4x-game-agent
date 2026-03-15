# HackerNews — Show HN

## Title (max 80 chars):
Show HN: 4x-game-agent – LLM game bot framework, 99% cheaper than pure LLM

## URL:
https://github.com/sonpiaz/4x-game-agent

## Text (if self-post, optional — URL post is usually better for Show HN):

Open-source framework for building AI bots that play 4X mobile strategy games (Rise of Kingdoms, Evony, etc.).

The key insight: you don't need AI for 98% of game decisions. Pixel analysis classifies screens in <50ms. PaddleOCR reads game state locally. Scripted workflows handle known tasks. A world model predicts timer completions.

LLM vision (Claude) only steps in for strategic reviews every 30 min and rare workflow failures. Result: ~$0.01/hr vs $1+/hr for pure LLM.

Framework design: thin core (ADB, OCR, template matching, LLM wrapper) + game-specific folders that are fully self-contained and disposable. Copy a template to add a new game.

Python, MIT license. Looking for contributors.
