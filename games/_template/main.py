#!/usr/bin/env python3
"""
Game Bot — Template for 4x-game-agent.

Customize this file for your game.

Usage:
  python main.py --test   # Test connection + OCR
  python main.py          # Run bot
"""
import sys
import os
import time
import yaml

# Setup paths
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAME_DIR)

# Load config
with open(os.path.join(GAME_DIR, "config.yaml")) as f:
    CONFIG = yaml.safe_load(f)


def test_mode():
    """Test ADB connection and OCR."""
    print("TEST MODE")
    print("=" * 50)

    from agent.adb import GameScreen
    screen = GameScreen(
        device=CONFIG["adb_device"],
        screenshot_path=CONFIG["screenshot_path"],
    )

    print("1. Connecting ADB...")
    if not screen.connect():
        print("   FAILED — check emulator")
        return
    print(f"   OK — {screen.device_w}x{screen.device_h}")

    print("2. Screenshot...")
    b64, sx, sy = screen.screenshot()
    if not b64:
        print("   FAILED")
        return
    print(f"   OK (scale: {sx:.2f}x, {sy:.2f}y)")

    print("3. OCR...")
    from agent.ocr import OCREngine
    ocr = OCREngine()
    t0 = time.time()
    texts = ocr.read_all(CONFIG["screenshot_path"])
    ms = (time.time() - t0) * 1000
    print(f"   Found {len(texts)} text regions in {ms:.0f}ms")
    for t in texts[:10]:
        print(f"   [{t['x']:4d},{t['y']:4d}] {t['text']}")

    print("\nReady! Customize this game's modules and run `python main.py`.")


def main():
    """Main bot loop — customize for your game."""
    print("TODO: Implement your game's main loop.")
    print("See games/kingshot/ for a reference implementation.")


if __name__ == "__main__":
    os.chdir(GAME_DIR)
    if "--test" in sys.argv:
        test_mode()
    else:
        main()
