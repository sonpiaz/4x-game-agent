#!/usr/bin/env python3
"""
Kingshot Bot — Reference implementation for 4x-game-agent.

Usage:
  python main.py              # Run bot (v10 Explorer engine)
  python main.py --test       # Test all layers
  python main.py --calibrate  # One-time building discovery
"""
import sys
import os
import time
import yaml

# Add repo root to path so we can import agent package
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

# Also add this game dir to path for local imports
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAME_DIR)

# Load config
with open(os.path.join(GAME_DIR, "config.yaml")) as f:
    CONFIG = yaml.safe_load(f)

# Make config accessible as module-level attributes (backwards compat)
import types
config = types.SimpleNamespace(**{
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    "STRATEGIC_MODEL": CONFIG["strategic_model"],
    "TACTICAL_MODEL": CONFIG["tactical_model"],
    "STRATEGIC_MAX_TOKENS": CONFIG["strategic_max_tokens"],
    "TACTICAL_MAX_TOKENS": CONFIG["tactical_max_tokens"],
    "ADB_DEVICE": CONFIG["adb_device"],
    "TAP_DELAY": CONFIG["tap_delay"],
    "ACTION_DELAY": CONFIG["action_delay"],
    "MENU_LOAD_WAIT": CONFIG["menu_load_wait"],
    "STRATEGIC_INTERVAL": CONFIG["strategic_interval"],
    "STEP_DELAY": CONFIG["step_delay"],
    "MAX_STEPS_PER_GOAL": CONFIG["max_steps_per_goal"],
    "SCREENSHOT_PATH": CONFIG["screenshot_path"],
    "MIN_GEMS_TO_SPEND": CONFIG["min_gems_to_spend"],
    "NEVER_SPEND_GEMS_ON": CONFIG["never_spend_gems_on"],
    "DASHBOARD_PORT": CONFIG["dashboard_port"],
    "LOG_PATH": os.path.join(GAME_DIR, "logs", "bot.log"),
})

# Monkey-patch config module so existing code works without changes
sys.modules["config"] = config


def test_mode():
    """Test: 1 screenshot -> Fast Classify -> OCR -> World Model check."""
    print("TEST MODE - Kingshot Bot (4x-game-agent)")
    print("=" * 50)

    from agent.adb import GameScreen
    from agent.dashboard import BotLogger

    logger = BotLogger(log_dir=os.path.join(GAME_DIR, "logs"))
    screen = GameScreen(device=config.ADB_DEVICE,
                        screenshot_path=config.SCREENSHOT_PATH)

    print("1. Connecting ADB...")
    connected = screen.connect()
    print(f"   {'OK' if connected else 'FAILED'}")
    if not connected:
        return

    print(f"   Device: {screen.device_w}x{screen.device_h}")

    print("2. Screenshot...")
    b64, sx, sy = screen.screenshot()
    print(f"   {'OK' if b64 else 'FAILED'} (scale: {sx:.2f}x, {sy:.2f}y)")
    if not b64:
        return

    print("3. Fast screen classification (pixel-based)...")
    from screen_analyzer import FastScreenAnalyzer
    analyzer = FastScreenAnalyzer()
    t0 = time.time()
    fast_result = analyzer.classify_fast(config.SCREENSHOT_PATH)
    fast_ms = (time.time() - t0) * 1000
    print(f"   Fast result: {fast_result} ({fast_ms:.0f}ms)")

    print("4. Local OCR...")
    from agent.ocr import OCREngine
    ocr = OCREngine()
    t0 = time.time()
    texts = ocr.read_all(config.SCREENSHOT_PATH)
    ocr_ms = (time.time() - t0) * 1000
    print(f"   OCR time: {ocr_ms:.0f}ms, texts found: {len(texts)}")

    print(f"\nPERFORMANCE: Fast={fast_ms:.0f}ms, OCR={ocr_ms:.0f}ms, "
          f"Speedup={ocr_ms/max(fast_ms, 1):.0f}x")
    print("Kingshot bot ready. Run `python main.py` for full execution.")


def main():
    """Run the Kingshot bot."""
    print("""
 ╔══════════════════════════════════════╗
 ║   KINGSHOT BOT — 4x-game-agent      ║
 ║   Fast Screen Classify (<100ms)     ║
 ║   World Model + Timer Sync          ║
 ║   AI = last resort (~$0.01/hr)      ║
 ╚══════════════════════════════════════╝
""")

    from agent.adb import GameScreen, GameActions
    from agent.dashboard import BotLogger, start_dashboard, is_paused
    from prompts import ClaudeVision
    from engine import V8Engine

    logger = BotLogger(log_dir=os.path.join(GAME_DIR, "logs"))
    screen = GameScreen(device=config.ADB_DEVICE,
                        screenshot_path=config.SCREENSHOT_PATH)
    actions = GameActions(device=config.ADB_DEVICE,
                          tap_delay=config.TAP_DELAY,
                          action_delay=config.ACTION_DELAY)
    vision = ClaudeVision()

    engine = V8Engine(screen, actions, vision, logger)

    start_dashboard(port=config.DASHBOARD_PORT, title="Kingshot Bot")

    logger.log("Connecting to BlueStacks...")
    connected = screen.connect()
    if not connected:
        logger.log("ERROR: ADB failed! Check BlueStacks.")
        sys.exit(1)

    res = screen.get_resolution()
    logger.log(f"Connected! Device: {res[0]}x{res[1]}")
    logger.log(f"Dashboard: http://localhost:{config.DASHBOARD_PORT}")

    consecutive_errors = 0

    while True:
        try:
            if is_paused():
                time.sleep(2)
                continue

            engine.run_cycle()
            logger.update_stats(engine.get_stats())
            consecutive_errors = 0

            sleep_time = engine.get_sleep_interval()
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.log("Bot stopped")
            break

        except Exception as e:
            consecutive_errors += 1
            logger.log(f"ERROR (#{consecutive_errors}): {e}")
            import traceback
            logger.log(traceback.format_exc())
            if consecutive_errors >= 5:
                logger.log("5 errors - cooling down 5 min")
                time.sleep(300)
                consecutive_errors = 0
            else:
                time.sleep(10)


if __name__ == "__main__":
    # Change working directory to game folder for relative file paths
    os.chdir(GAME_DIR)

    if "--test" in sys.argv:
        test_mode()
    elif "--calibrate" in sys.argv:
        print("Run: python -c 'from building_finder import ...; ...'")
        print("(Calibration code preserved in building_finder.py)")
    else:
        main()
