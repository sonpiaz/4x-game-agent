"""
V8 Engine — "Architect"
World Model-driven, workflow-based game automation.

Architecture:
  SENTINEL (every 5s, FREE) → popup check, timer monitor
  EXECUTOR (triggered, FREE) → run verified workflows
  STRATEGIST (every 30min, $0.004) → Claude Sonnet big-picture review

Key difference from v7:
  - World Model knows game state persistently (doesn't re-discover each cycle)
  - Workflows execute fast deterministic tap sequences (not step-by-step AI)
  - Timer-based scheduling (acts at the right moment, not polling)
  - AI is last resort fallback, not the primary decision maker
"""
import time
import config
from game.screen import GameScreen
from game.actions import GameActions
from perception.ocr import GameOCR
from perception.screen_analyzer import FastScreenAnalyzer
from core.state_machine import GameFSM, GameState
from core.world_model import WorldModel
from core.workflow_engine import WorkflowEngine
from brain.claude_vision import ClaudeVision


# Building name mapping: game knowledge → coordinate_map
KNOWLEDGE_TO_COORDS = {
    "Wall": "wall",
    "Academy": "academy",
    "Hospital": "hospital",
    "Infirmary": "hospital",
    "Barracks": "barracks",
    "Range": "archery_range",
    "Archery Range": "archery_range",
    "Stable": "stables",
    "Stables": "stables",
    "Embassy": "embassy",
    "Town Center": "town_center",
    "Hero Hall": None,
    "House 1": None,
    "House 3": None,
    "Sawmill": None,
    "Quarry": None,
    "Iron Mine": None,
    "Mill": None,
    "Command Center": None,
}


class V8Engine:
    """The Architect — World Model-driven game automation."""

    # Intervals
    CYCLE_INTERVAL = 5          # Main loop tick (seconds)
    PATROL_INTERVAL = 300       # Resource collection sweep
    ALLIANCE_HELP_INTERVAL = 600  # Alliance help
    ALLIANCE_DONATE_INTERVAL = 86400  # Daily
    RED_DOT_INTERVAL = 1800     # Check notifications
    CONQUEST_INTERVAL = 900     # Push conquest
    STRATEGIC_INTERVAL = 1800   # Sonnet review

    # OCR frequency: full OCR for game state every N seconds (not every cycle)
    OCR_INTERVAL = 60  # Full OCR every 60s (was every 5s)

    def __init__(self, screen: GameScreen, actions: GameActions,
                 vision: ClaudeVision, logger):
        self.screen = screen
        self.actions = actions
        self.vision = vision
        self.log = logger.log

        # Core systems
        self.ocr = GameOCR()
        self.analyzer = FastScreenAnalyzer(ocr=self.ocr)  # Fast pixel classifier
        self.fsm = GameFSM(actions, self.ocr, self.log)
        self.world = WorldModel(self.log)
        self.wf = WorkflowEngine(screen, actions, self.ocr, self.fsm,
                                  self.world, self.log,
                                  analyzer=self.analyzer)

        # Timing
        self.cycle_count = 0
        self._last_patrol = 0
        self._last_alliance_help = 0
        self._last_alliance_donate = 0
        self._last_red_dots = 0
        self._last_conquest = 0
        self._last_strategic = 0
        self._last_full_ocr = 0  # Track when last full OCR ran

        # Stats
        self.stats = {
            "cycles": 0,
            "mode": "sentinel",
            "popups_dismissed": 0,
            "api_calls_strategic": 0,
            "api_calls_tactical": 0,
            "idle_fixes": 0,
            "patrol_runs": 0,
        }

        # Idle queue failure tracking: {queue_key: (consecutive_fails, skip_until_time)}
        self._idle_failures = {}

    def run_cycle(self):
        """Main loop entry. Called every CYCLE_INTERVAL seconds."""
        self.cycle_count += 1
        self.stats["cycles"] += 1
        now = time.time()

        # Log every 10th cycle to reduce noise
        if self.cycle_count % 10 == 1:
            self.log(f"\n{'='*50}")
            self.log(f"CYCLE #{self.cycle_count} | {self.world.get_summary()}")
            self.log(f"Power/hr: {self.world.power_per_hour():,} | "
                     f"Idle fixes: {self.stats['idle_fixes']} | "
                     f"API: {self.stats['api_calls_strategic']}S+"
                     f"{self.stats['api_calls_tactical']}H")

        # === ALWAYS: Screenshot + FAST classify (~50ms vs 15-20s) ===
        b64, sx, sy = self.screen.screenshot()
        if not b64:
            self.log("ERROR: Screenshot failed")
            return

        # Fast pixel-based classification (falls back to OCR if ambiguous)
        screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
        # Update FSM with pre-classified result (no OCR needed)
        self.fsm.update(screen_type)

        # === POPUP: Dismiss immediately (FREE) ===
        if self.fsm.is_popup():
            self.log(f"POPUP: {screen_type}")
            self.fsm.handle_popup()
            self.stats["popups_dismissed"] += 1
            return

        # === OBSERVE: Update world model if on home_city ===
        # Full OCR only runs periodically (every OCR_INTERVAL seconds)
        if screen_type == "home_city":
            if now - self._last_full_ocr > self.OCR_INTERVAL:
                ocr_data = self.ocr.read_game_state(config.SCREENSHOT_PATH)
                self.world.observe_screen(ocr_data, screen_type)
                # Sync timers from OCR data
                if ocr_data.get("active_timers"):
                    self.world.sync_timers_from_screen(ocr_data["active_timers"])
                self._last_full_ocr = now

        # === NAVIGATE HOME: If on useless screen ===
        useful = {"home_city", "building_menu", "research_tree",
                  "training_menu", "alliance_screen", "conquest_screen",
                  "hero_screen", "battle_prep"}
        if screen_type not in useful:
            self.log(f"SENTINEL: On '{screen_type}', navigating home")
            self.wf.ensure_home()
            return

        # === P0: FIX IDLE QUEUES (highest priority, FREE) ===
        # Try each idle queue; skip queues that have failed 3+ times recently
        idle_queues = self.world.get_idle_queues()
        if idle_queues:
            self.stats["mode"] = "executor"
            for queue_type, queue_name, _ in idle_queues:
                queue_key = f"{queue_type}:{queue_name}"

                # Check if this queue is in skip cooldown
                fails, skip_until = self._idle_failures.get(queue_key, (0, 0))
                if fails >= 3 and now < skip_until:
                    self.log(f"EXECUTOR: Skipping {queue_key} "
                             f"(failed {fails}x, cooling {skip_until - now:.0f}s)")
                    continue

                self.log(f"EXECUTOR: Idle {queue_key}")
                success = self._fix_idle(queue_type, queue_name)
                self.stats["idle_fixes"] += 1

                if success:
                    # Reset failure counter on success
                    self._idle_failures.pop(queue_key, None)
                else:
                    # Increment failure counter; skip for 10 min after 3 fails
                    new_fails = fails + 1
                    skip_time = now + 600 if new_fails >= 3 else 0
                    self._idle_failures[queue_key] = (new_fails, skip_time)
                    if new_fails >= 3:
                        self.log(f"EXECUTOR: {queue_key} failed {new_fails}x, "
                                 f"skipping for 10 min")
                    continue  # Try next idle queue

                return  # Successfully fixed one queue, exit cycle

        # === P1: PERIODIC TASKS ===

        # Resource collection (every 5 min)
        if now - self._last_patrol > self.PATROL_INTERVAL:
            self.stats["mode"] = "patrol"
            self.wf.collect_resources()
            self._last_patrol = now
            self.stats["patrol_runs"] += 1
            return

        # Alliance help (every 10 min)
        if now - self._last_alliance_help > self.ALLIANCE_HELP_INTERVAL:
            self.wf.alliance_help()
            self._last_alliance_help = now
            return

        # Alliance donate (daily)
        if not self.world.is_daily_done("alliance_donate"):
            if now - self._last_alliance_donate > 60:  # Don't retry too fast
                if self.wf.alliance_donate():
                    self.world.mark_daily_done("alliance_donate")
                self._last_alliance_donate = now
                return

        # Red dots / notifications (every 30 min)
        if now - self._last_red_dots > self.RED_DOT_INTERVAL:
            self.wf.collect_red_dots()
            self._last_red_dots = now
            return

        # Conquest push (every 15 min)
        if now - self._last_conquest > self.CONQUEST_INTERVAL:
            self.wf.conquest_battle()
            self._last_conquest = now
            return

        # === P2: STRATEGIC REVIEW (every 30 min, PAID) ===
        if now - self._last_strategic > self.STRATEGIC_INTERVAL:
            self.stats["mode"] = "strategist"
            self._strategic_review(b64)
            self._last_strategic = now
            return

        # === IDLE: Nothing to do ===
        self.stats["mode"] = "sentinel"
        next_secs = self.world.seconds_until_next_event()
        if next_secs < 120:
            nxt = self.world.next_timer_completion()
            if self.cycle_count % 10 == 0:
                self.log(f"SENTINEL: {nxt[1]} completes in {next_secs:.0f}s")

    # =========================================================
    # IDLE QUEUE FIXING
    # =========================================================

    def _fix_idle(self, queue_type: str, queue_name: str) -> bool:
        """Fix an idle queue by running the appropriate workflow.
        Returns True if the fix succeeded, False otherwise."""
        if queue_type == "builder":
            building = self._pick_next_upgrade()
            if building:
                self.log(f"EXECUTOR: Upgrade {building}")
                success = self.wf.upgrade_building(building)
                if not success:
                    self._ai_fallback(
                        "upgrade_building",
                        f"Upgrade {building} — tap on it, then tap upgrade button, confirm",
                    )
                    return False
                return True
            else:
                self.log("EXECUTOR: No building to upgrade (all prereqs unknown)")
                self.world.add_lesson("No obvious next upgrade — need strategic review")
                return False

        elif queue_type == "research":
            success = self.wf.start_research()
            if not success:
                self._ai_fallback(
                    "start_research",
                    "Open Academy, navigate to research tree, start Construction Speed or next available economy research",
                    max_steps=12,
                )
                return False
            return True

        elif queue_type == "training":
            success = self.wf.train_troops(queue_name)
            if not success:
                self._ai_fallback(
                    "train_troops",
                    f"Tap {queue_name} building, tap Train, set max troops, confirm",
                )
                return False
            return True

        return False

    def _ai_fallback(self, goal: str, goal_desc: str, max_steps: int = 10):
        """Try AI-guided task with error handling for missing/invalid API key."""
        self.log(f"EXECUTOR: Workflow failed, trying AI fallback")
        try:
            self.stats["api_calls_tactical"] += 1
            self.wf.ai_guided_task(self.vision, goal, goal_desc, max_steps=max_steps)
        except Exception as e:
            err = str(e)
            if "401" in err or "authentication" in err.lower() or "api" in err.lower():
                self.log("EXECUTOR: AI fallback skipped (no valid API key)")
            else:
                self.log(f"EXECUTOR: AI fallback error: {e}")

    def _pick_next_upgrade(self) -> str:
        """Use TC prerequisites to pick the most important upgrade."""
        try:
            from game.knowledge import TC_PREREQUISITES
        except ImportError:
            return "town_center"

        tc = self.world.get_tc_level()
        next_tc = tc + 1

        if next_tc not in TC_PREREQUISITES:
            return "town_center"

        prereqs = TC_PREREQUISITES[next_tc].get("prereqs", {})

        # Find first prerequisite we haven't met
        for knowledge_name, required_level in prereqs.items():
            coord_name = KNOWLEDGE_TO_COORDS.get(knowledge_name)
            if not coord_name:
                continue  # Building not in our coordinate map
            current = self.world.get_building_level(coord_name)
            if current < required_level:
                return coord_name

        # All prereqs met — upgrade TC
        return "town_center"

    # =========================================================
    # STRATEGIC REVIEW
    # =========================================================

    def _strategic_review(self, screenshot_b64: str):
        """Call Claude Sonnet for big-picture strategic review."""
        self.log("STRATEGIST: Reviewing game state with Claude Sonnet...")
        self.stats["api_calls_strategic"] += 1

        start = time.time()
        plan = self.vision.strategic_plan(screenshot_b64)
        elapsed = time.time() - start
        self.log(f"STRATEGIST: Review done in {elapsed:.1f}s")

        goal = plan.get("goal", "maintenance")
        goal_desc = plan.get("goal_description", "")
        self.log(f"STRATEGIST: Goal → {goal}: {goal_desc}")

        # If Sonnet detects something urgent, act on it
        if plan.get("builders_idle"):
            self.log("STRATEGIST: Sonnet says builders idle!")
            # Force world model to re-check
            for name, b in self.world.state["buildings"].items():
                if b["upgrading"] and b.get("timer_end") and b["timer_end"] < time.time():
                    self.world.observe_upgrade_complete(name)

        if plan.get("research_idle"):
            self.log("STRATEGIST: Sonnet says research idle!")
            self.world.state["research"]["active"] = False
            self.world.save()

        if plan.get("training_idle"):
            self.log("STRATEGIST: Sonnet says training idle!")
            for name in self.world.state["training"]:
                t = self.world.state["training"][name]
                if t["active"] and t.get("timer_end") and t["timer_end"] < time.time():
                    t["active"] = False
            self.world.save()

    # =========================================================
    # STATS
    # =========================================================

    def get_stats(self):
        self.stats["world_summary"] = self.world.get_summary()
        self.stats["power_per_hour"] = self.world.power_per_hour()
        self.stats["workflow_stats"] = self.wf.stats
        self.stats["reflection_stats"] = self.wf.reflection.get_stats()
        self.stats["analyzer_stats"] = self.analyzer.get_stats()
        nxt = self.world.next_timer_completion()
        if nxt:
            secs = max(0, nxt[0] - time.time())
            self.stats["next_event"] = f"{nxt[1]} in {secs/60:.0f}min"
        else:
            self.stats["next_event"] = "none"
        return self.stats

    def get_sleep_interval(self) -> float:
        """Smart sleep: shorter when action needed soon, longer when idle."""
        next_secs = self.world.seconds_until_next_event()

        if next_secs < 30:
            return 2  # Timer about to complete — stay alert
        elif next_secs < 120:
            return 5  # Event coming soon
        elif next_secs < 600:
            return 10  # Nothing urgent
        else:
            return 15  # All queues busy, long timers
