"""
Workflow Engine — Execute verified action sequences.
Each workflow is a method that: ensure screen → tap sequence → verify → update model.

v9 improvements (CRADLE/Voyager patterns):
  - Adaptive coordinates: try cached position → default → spiral search
  - Self-reflection: log failures, learn from mistakes
  - Smart retry: offset grid pattern when building tap misses

v10 improvements (ROK bot + BuildingFinder):
  - BuildingFinder: template match → cached → default → city exploration
  - Auto-captures templates when buildings found
  - Builds complete building map over time (one-time calibration)
"""
import time
import config
from perception.coordinate_map import (
    TABS, POPUP, BUILDINGS, BUILDING_MENU, TRAINING,
    ALLIANCE, CONQUEST, HERO, CLAIM, RESOURCE_SWEEP,
)
from core.reflection import ReflectionLog
from perception.template_match import TemplateMatcher
from perception.building_finder import BuildingFinder


class WorkflowEngine:
    """Deterministic workflow executor with screen verification and adaptive learning."""

    def __init__(self, screen, actions, ocr, fsm, world_model, log_fn,
                 analyzer=None):
        self.screen = screen
        self.actions = actions
        self.ocr = ocr
        self.fsm = fsm
        self.world = world_model
        self.log = log_fn
        self.analyzer = analyzer  # FastScreenAnalyzer for fast classification
        self.reflection = ReflectionLog(log_fn)

        # Building detection: template matching + exploration
        self.template_matcher = TemplateMatcher(log_fn)
        self.building_finder = BuildingFinder(
            screen, actions, ocr, self.template_matcher,
            world_model, log_fn,
            analyzer=analyzer,
        )

        self.stats = {
            "executed": 0,
            "succeeded": 0,
            "failed": 0,
        }

    # =========================================================
    # VERIFICATION HELPERS
    # =========================================================

    def _check_screen(self) -> str:
        """Take screenshot and classify screen using fast analyzer."""
        self.screen.screenshot()
        if self.analyzer:
            screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
        else:
            screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)
        self.fsm.update(screen_type)
        return screen_type

    def _wait_for_screen(self, expected: str, timeout: float = 5.0) -> bool:
        """Wait for screen to match expected type."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            screen = self._check_screen()
            if screen == expected:
                return True
            if self.fsm.is_popup():
                self.fsm.handle_popup()
                time.sleep(0.5)
                continue
            time.sleep(0.5)
        return False

    def _wait_for_any_screen(self, expected: set, timeout: float = 5.0) -> str:
        """Wait for screen to be any of expected types. Returns matched type or ''."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            screen = self._check_screen()
            if screen in expected:
                return screen
            if self.fsm.is_popup():
                self.fsm.handle_popup()
                time.sleep(0.5)
                continue
            time.sleep(0.5)
        return ""

    def _run(self, name: str, fn, *args) -> bool:
        """Execute a workflow with stats tracking and reflection."""
        self.stats["executed"] += 1

        # Check past reflections for warnings
        past_failures = self.reflection.get_reflections_for(name, limit=3)
        if past_failures:
            recent = past_failures[0]
            self.log(f"WORKFLOW: {name} (note: last failure was '{recent['error']}')")
        else:
            self.log(f"WORKFLOW: {name}")

        try:
            result = fn(*args)
            if result:
                self.stats["succeeded"] += 1
                self.reflection.record_success(name)
                self.log(f"WORKFLOW: {name} — OK")
            else:
                self.stats["failed"] += 1
                self.log(f"WORKFLOW: {name} — FAILED")
            return result
        except Exception as e:
            self.stats["failed"] += 1
            self.reflection.record_failure(
                name, str(e), f"Exception during workflow: {type(e).__name__}")
            self.log(f"WORKFLOW: {name} — ERROR: {e}")
            return False

    # =========================================================
    # NAVIGATION
    # =========================================================

    def ensure_home(self) -> bool:
        """Navigate to home city screen. NEVER uses actions.back().
        Strategy: close/exit current screen until home_city detected.

        Screen-specific navigation:
        - battle_prep / battle_active: green back arrow top-left (~120, 120)
        - conquest_screen: X button top-right or back arrow top-left
        - building_menu / training_menu: X or tap outside
        - popup: auto-dismiss via FSM
        - unknown: try close buttons then bottom nav
        """
        for attempt in range(6):
            screen = self._check_screen()

            if screen == "home_city":
                return True

            # Handle popups via FSM
            if self.fsm.is_popup():
                self.fsm.handle_popup()
                time.sleep(1.0)
                continue

            self.log(f"  ensure_home attempt {attempt+1}: on '{screen}'")

            # Screen-specific exit strategies
            if screen in ("battle_prep", "battle_active", "battle_result"):
                # Green back arrow at top-left (device coords ~120, 120)
                self.actions.tap(120, 120, "back_arrow_topleft")
                time.sleep(2.0)

            elif screen == "conquest_screen":
                # Green back arrow at top-left exits conquest
                self.actions.tap(120, 120, "back_arrow_conquest")
                time.sleep(2.0)

            elif screen in ("building_menu", "training_menu", "research_tree"):
                # Close building menu — X at top-right of dialog
                self.actions.tap(1300, 400, "close_building_x")
                time.sleep(1.0)
                # Or tap outside the menu
                self.actions.tap(100, 400, "tap_outside_menu")
                time.sleep(1.0)

            elif screen in ("hero_screen", "alliance_screen"):
                # These screens have X or back at top
                self.actions.tap(120, 120, "back_arrow")
                time.sleep(1.5)

            else:
                # Unknown screen — try multiple exit strategies
                if attempt % 2 == 0:
                    # Try close buttons at common positions
                    self.actions.tap(1380, 100, "close_x_topright")
                    time.sleep(0.5)
                    self.actions.tap(1300, 300, "close_x_mid")
                    time.sleep(0.5)
                    self.actions.tap(120, 120, "back_arrow_generic")
                    time.sleep(1.5)
                else:
                    # Try tapping center to dismiss, then outside
                    self.actions.tap(720, 1200, "dismiss_center")
                    time.sleep(1.0)
                    self.actions.tap(100, 1200, "dismiss_side")
                    time.sleep(1.0)

        return self._wait_for_screen("home_city", timeout=3.0)

    # =========================================================
    # BUILDING WORKFLOWS
    # =========================================================

    def upgrade_building(self, building_name: str) -> bool:
        """Full workflow: home → tap building → upgrade → confirm → home."""
        return self._run(f"upgrade:{building_name}", self._upgrade_building, building_name)

    def _smart_tap_building(self, building_name: str) -> bool:
        """Find and tap a building using BuildingFinder.

        Uses 4 strategies in priority order:
        1. Template matching (fast, ~100ms)
        2. Cached position from world model
        3. Default coordinates + spiral retry
        4. City exploration with scroll + tap-identify grid

        Any building found is auto-cached and templated for future use.
        """
        success = self.building_finder.find_and_tap(building_name)
        if not success:
            self.reflection.record_failure(
                f"tap:{building_name}",
                "Building not found by any strategy",
                "Template match, cached, default coords, and city exploration all failed. "
                "Building may be in an unexplored area of the city map.",
            )
        return success

    def _upgrade_building(self, building_name: str) -> bool:
        # Step 1: Ensure home
        if not self.ensure_home():
            self.log("  Can't reach home screen")
            self.reflection.record_failure(
                f"upgrade:{building_name}", "Can't reach home",
                "ensure_home failed before upgrade attempt")
            return False

        # Step 2: Smart tap building (adaptive + spiral retry)
        if not self._smart_tap_building(building_name):
            self.log(f"  Can't open {building_name} menu after spiral search")
            self.ensure_home()
            return False

        # Step 3: Tap upgrade button
        ux, uy = BUILDING_MENU["upgrade_button"]
        self.actions.tap(ux, uy, "upgrade_btn")
        time.sleep(1.5)

        # Step 4: Handle confirm dialog
        screen = self._check_screen()
        if screen in ("popup_generic", "popup_purchase", "building_menu"):
            cx, cy = BUILDING_MENU["confirm_upgrade"]
            self.actions.tap(cx, cy, "confirm_upgrade")
            time.sleep(1.0)

        # Step 5: Check if upgrade button needs a second tap (alliance help prompt)
        screen = self._check_screen()
        if screen == "building_menu":
            cx, cy = BUILDING_MENU["confirm_upgrade"]
            self.actions.tap(cx, cy, "confirm_upgrade_2")
            time.sleep(1.0)

        # Step 6: Update world model
        self.world.observe_upgrade_started(building_name)

        # Step 7: Go home
        self.ensure_home()
        return True

    # =========================================================
    # TRAINING WORKFLOWS
    # =========================================================

    def train_troops(self, building_name: str) -> bool:
        """Full workflow: home → tap military building → train max → confirm → home."""
        return self._run(f"train:{building_name}", self._train_troops, building_name)

    def _train_troops(self, building_name: str) -> bool:
        if not self.ensure_home():
            return False

        # Smart tap building (adaptive + spiral retry)
        if not self._smart_tap_building(building_name):
            self.log(f"  Can't open {building_name} menu")
            self.ensure_home()
            return False

        screen = self._check_screen()

        # If on building menu, tap train button to open training screen
        if screen == "building_menu":
            tx, ty = TRAINING["train_button"]
            self.actions.tap(tx, ty, "train_btn")
            time.sleep(1.5)

        # Tap max
        mx, my = TRAINING["max_button"]
        self.actions.tap(mx, my, "max_troops")
        time.sleep(0.5)

        # Confirm
        cx, cy = TRAINING["confirm_train"]
        self.actions.tap(cx, cy, "confirm_train")
        time.sleep(1.0)

        # Update world model
        self.world.observe_training_started(building_name)

        self.ensure_home()
        return True

    # =========================================================
    # RESEARCH WORKFLOW
    # =========================================================

    def start_research(self) -> bool:
        """Navigate to academy, attempt to start research.
        Returns False if research tree navigation needs AI help."""
        return self._run("start_research", self._start_research)

    def _start_research(self) -> bool:
        if not self.ensure_home():
            return False

        # Smart tap academy
        if not self._smart_tap_building("academy"):
            self.log("  Can't open academy menu")
            self.ensure_home()
            return False

        screen = self._check_screen()

        # If on building menu, look for a "Research" button
        if screen == "building_menu":
            # Tap info/research area
            self.actions.tap(720, 2100, "research_btn")
            time.sleep(1.5)

            # Check if we reached the research tree
            screen = self._check_screen()
            if screen == "research_tree":
                self.log("  Reached research tree — returning True for AI to pick research")
                return True

        # Not on research tree — couldn't navigate there
        self.ensure_home()
        return False

    # =========================================================
    # COLLECTION WORKFLOWS
    # =========================================================

    def collect_resources(self) -> bool:
        """Sweep-tap base for floating resource icons."""
        return self._run("collect_resources", self._collect_resources)

    def _collect_resources(self) -> bool:
        if not self.ensure_home():
            return False

        for x, y in RESOURCE_SWEEP:
            self.actions.fast_tap(x, y)
        return True

    def collect_red_dots(self) -> bool:
        """Tap common notification areas to collect rewards."""
        return self._run("collect_red_dots", self._collect_red_dots)

    def _collect_red_dots(self) -> bool:
        if not self.ensure_home():
            return False

        # Tap right-panel notification areas
        from perception.coordinate_map import RIGHT_PANEL
        for name, (rx, ry) in RIGHT_PANEL.items():
            self.actions.tap(rx, ry, f"red_dot:{name}")
            time.sleep(0.5)
            # Quick dismiss any popup that opens
            screen = self._check_screen()
            if self.fsm.is_popup():
                self.fsm.handle_popup()
                time.sleep(0.5)

        # Claim buttons in common positions
        for name, (cx, cy) in CLAIM.items():
            self.actions.tap(cx, cy, f"claim:{name}")
            time.sleep(0.3)

        self.ensure_home()
        return True

    # =========================================================
    # ALLIANCE WORKFLOWS
    # =========================================================

    def alliance_help(self) -> bool:
        """Open alliance tab, help all members."""
        return self._run("alliance_help", self._alliance_help)

    def _alliance_help(self) -> bool:
        ax, ay = TABS["alliance"]
        self.actions.tap(ax, ay, "tab:alliance")
        time.sleep(2.0)

        # Help all button
        self.actions.tap(720, 400, "help_all")
        time.sleep(0.5)
        self.actions.multi_tap(1100, 600, 10, "help_members")
        time.sleep(0.5)

        self.ensure_home()
        return True

    def alliance_donate(self) -> bool:
        """Donate to alliance tech."""
        return self._run("alliance_donate", self._alliance_donate)

    def _alliance_donate(self) -> bool:
        ax, ay = TABS["alliance"]
        self.actions.tap(ax, ay, "tab:alliance")
        time.sleep(2.0)

        self.actions.tap(400, 300, "tech_tab")
        time.sleep(2.0)

        self.actions.multi_tap(720, 1800, 5, "donate")
        time.sleep(0.5)

        self.ensure_home()
        return True

    # =========================================================
    # CONQUEST WORKFLOW
    # =========================================================

    def conquest_battle(self) -> bool:
        """Navigate to conquest, attempt to push stages."""
        return self._run("conquest_battle", self._conquest_battle)

    def _conquest_battle(self) -> bool:
        cx, cy = TABS["conquest"]
        self.actions.tap(cx, cy, "tab:conquest")
        time.sleep(2.0)

        screen = self._wait_for_any_screen(
            {"conquest_screen", "battle_prep"}, timeout=4.0
        )
        if not screen:
            self.ensure_home()
            return False

        # Tap battle/challenge button
        bx, by = CONQUEST["battle_button"]
        self.actions.tap(bx, by, "battle")
        time.sleep(2.0)

        # If battle prep screen, deploy and fight
        screen = self._check_screen()
        if screen == "battle_prep":
            # Quick deploy (if available)
            self.actions.tap(720, 1200, "quick_deploy")
            time.sleep(1.0)
            # Fight button
            self.actions.tap(720, 2000, "fight")
            time.sleep(3.0)

        # Wait for battle result
        screen = self._wait_for_any_screen(
            {"battle_result", "conquest_screen", "home_city"}, timeout=15.0
        )

        if screen == "battle_result":
            # Collect reward if available
            rx, ry = CONQUEST["collect_reward"]
            self.actions.tap(rx, ry, "collect_reward")
            time.sleep(1.0)

        self.ensure_home()
        return True

    # =========================================================
    # AI-ASSISTED WORKFLOW (Fallback)
    # =========================================================

    def ai_guided_task(self, vision, goal: str, goal_desc: str,
                       max_steps: int = 15) -> bool:
        """Fallback: Use Claude Haiku for step-by-step navigation.
        Called when no scripted workflow exists for a task."""
        self.log(f"AI FALLBACK: {goal}")
        self.stats["executed"] += 1

        last_action = "none"
        last_result = f"Starting goal: {goal_desc}"
        consecutive_waits = 0

        for step in range(1, max_steps + 1):
            b64, sx, sy = self.screen.screenshot()
            if not b64:
                time.sleep(2)
                continue

            # Popup check
            screen = self.fsm.update(config.SCREENSHOT_PATH)
            if self.fsm.is_popup():
                self.fsm.handle_popup()
                time.sleep(1.0)
                continue

            # Get compressed dims for Claude
            img_w, img_h = self._compressed_dims()

            result = vision.tactical_step(
                b64, img_w, img_h,
                goal, goal_desc, step,
                last_action, last_result,
            )

            action = result.get("action", "wait")
            target = result.get("target", "?")
            reason = result.get("reason", "")

            if action == "tap":
                raw_x, raw_y = result.get("x", 0), result.get("y", 0)
                dev_x, dev_y = int(raw_x * sx), int(raw_y * sy)
                self.log(f"  AI Step {step}: TAP ({raw_x},{raw_y})→({dev_x},{dev_y}) {target}")
                self.actions.tap(dev_x, dev_y, target)
                last_action = f"tap {target} at ({dev_x},{dev_y})"
                last_result = "tapped, waiting"
                consecutive_waits = 0
                time.sleep(config.STEP_DELAY)

            elif action == "wait":
                secs = min(result.get("seconds", 2), 5)
                self.log(f"  AI Step {step}: WAIT {secs}s — {reason}")
                time.sleep(secs)
                last_action = f"waited {secs}s"
                last_result = "waited"
                consecutive_waits += 1
                if consecutive_waits >= 3:
                    break

            elif action == "done":
                self.log(f"  AI Step {step}: DONE — {reason}")
                self.stats["succeeded"] += 1
                return True

            else:
                break

        self.stats["failed"] += 1
        return False

    def _compressed_dims(self):
        try:
            from PIL import Image
            img = Image.open(config.SCREENSHOT_PATH)
            w, h = img.size
            if max(w, h) > 1280:
                ratio = 1280 / max(w, h)
                return int(w * ratio), int(h * ratio)
            return w, h
        except Exception:
            return 1280, 720
