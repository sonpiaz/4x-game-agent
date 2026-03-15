"""
Building Finder — Locate buildings on the scrollable city map.

The Kingshot city view is pannable/scrollable, so fixed coordinate approaches
fail. This module uses multiple strategies in priority order:

1. Template matching on current view (fast, ~100ms)
2. Cached position from world model (instant, proven-to-work coords)
3. Default coordinates with spiral retry (from coordinate_map)
4. City exploration: scroll + tap-identify grid (slow, one-time calibration)

Any building found by ANY method is auto-cached and its template captured
for faster future detection. Over time, the bot builds a complete building
map without needing VLM or manual coordinate entry.

Pattern: ROK bot OpenCV approach + CRADLE self-discovery.
"""
import os
import time
import shutil
import cv2
import numpy as np
import config

# Known building names that appear in building menus → coordinate_map key
KNOWN_BUILDING_NAMES = {
    "Town Center": "town_center",
    "Town Hall": "town_center",
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
    "Sawmill": "sawmill",
    "House": "house",
    "Quarry": "quarry",
    "Iron Mine": "iron_mine",
    "Mill": "mill",
    "Hero Hall": "hero_hall",
    "Command Center": "command_center",
    "Watchtower": "watchtower",
    "Kitchen": "kitchen",
    "Guard Station": "guard_station",
}

# Reverse lookup: coord_key → display names
COORD_TO_DISPLAY = {}
for _display, _coord in KNOWN_BUILDING_NAMES.items():
    COORD_TO_DISPLAY.setdefault(_coord, []).append(_display)

# Spiral offsets for probing around a base position
SPIRAL_OFFSETS = [
    (0, 0), (0, -100), (0, 100), (-100, 0), (100, 0),
    (-100, -100), (100, -100), (-100, 100), (100, 100),
    (0, -200), (0, 200), (-200, 0), (200, 0),
]

# Exploration grid positions in city area (avoids UI bars and right panel)
# x: 100-1050 (right panel starts ~1100), y: 300-1800 (top bar ~150, bottom ~2400)
EXPLORE_GRID_X = [250, 500, 750, 1000]
EXPLORE_GRID_Y = [400, 700, 1000, 1350, 1700]

# Scroll directions for exploring beyond the initial view
# Format: (name, swipe_x1, swipe_y1, swipe_x2, swipe_y2, duration_ms)
# To see the RIGHT side of city: drag finger LEFT (high x → low x)
SCROLL_DIRECTIONS = [
    ("right", 1000, 1000, 300, 1000, 500),
    ("left",  300, 1000, 1000, 1000, 500),
    ("up",    700, 500, 700, 1200, 500),
    ("down",  700, 1500, 700, 700, 500),
]


class BuildingFinder:
    """Find buildings on the scrollable city map using multiple strategies."""

    def __init__(self, screen, actions, ocr, template_matcher, world, log_fn,
                 analyzer=None):
        self.screen = screen
        self.actions = actions
        self.ocr = ocr
        self.templates = template_matcher
        self.world = world
        self.log = log_fn or print
        self.analyzer = analyzer  # FastScreenAnalyzer for fast classification

        # If we already have 5+ cached building positions, skip expensive exploration
        cached = self.world.state.get("cached_positions", {})
        if len(cached) >= 5:
            self._exploration_done = True
            (self.log or print)(
                f"FINDER: {len(cached)} cached positions found, skipping exploration"
            )
        else:
            self._exploration_done = False

    def find_and_tap(self, building_name: str) -> bool:
        """Find a building and tap on it. Returns True if building menu opened.

        After this returns True, the screen is on building_menu for the
        requested building — ready for upgrade/train/info actions.
        """
        self.log(f"FINDER: Looking for {building_name}")

        # Strategy 1: Template match on current screenshot
        self.screen.screenshot()
        pos = self._try_template(building_name)
        if pos:
            self.log(f"FINDER: Template match at ({pos[0]}, {pos[1]})")
            if self._tap_and_verify(pos[0], pos[1], building_name):
                return True

        # Strategy 2: Cached position from world model
        cached = self.world.get_cached_position(building_name)
        if cached:
            self.log(f"FINDER: Cached at ({cached[0]}, {cached[1]})")
            if self._tap_and_verify(cached[0], cached[1], building_name):
                return True
            self.world.invalidate_position(building_name)

        # Strategy 2.5: Reset camera to TC center, then try default coords
        # ROK bot pattern: navigate away and back resets camera position
        self._reset_camera()

        # Strategy 3: Default coordinates with spiral (after camera reset)
        from perception.coordinate_map import BUILDINGS as DEFAULT_COORDS
        if building_name in DEFAULT_COORDS:
            base_x, base_y = DEFAULT_COORDS[building_name]
            self.log(f"FINDER: Defaults ({base_x}, {base_y}) + spiral")
            for dx, dy in SPIRAL_OFFSETS:
                x, y = base_x + dx, base_y + dy
                if x < 50 or x > 1400 or y < 100 or y > 2400:
                    continue
                if self._tap_and_verify(x, y, building_name):
                    return True

        # Strategy 4: Full city exploration (slow, one-time)
        if not self._exploration_done:
            self.log(f"FINDER: Starting city exploration for {building_name}")
            return self._explore_city(building_name)

        self.log(f"FINDER: Could not find {building_name}")
        return False

    # =========================================================
    # CAMERA RESET (ROK bot pattern)
    # =========================================================

    def _reset_camera(self):
        """Reset city camera to center on Town Center.

        Pattern from ROK bots: navigate to a different screen (world map)
        and back to city view. This resets the camera to the default
        position centered on TC, making building coordinates predictable.
        """
        from perception.coordinate_map import TABS
        self.log("FINDER: Resetting camera (world→city)")

        # Tap "World" tab to leave city view
        wx, wy = TABS["world"]
        self.actions.tap(wx, wy, "tab_world")
        time.sleep(2.0)

        # Tap city area or a bottom tab to return to city view
        # Tapping the empty area at top-left should navigate back
        # Or we can tap a known bottom tab that returns to city
        # In Kingshot, tapping "world" again or tapping the city icon returns
        self.actions.tap(wx, wy, "tab_world_again")
        time.sleep(1.5)

        # If we're on world map, tap center to go back to city
        self.screen.screenshot()
        if self.analyzer:
            screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
        else:
            screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)
        if screen_type != "home_city":
            # Try tapping center of screen (often returns to city)
            self.actions.tap(720, 1280, "center_return")
            time.sleep(1.5)
            # Try close/back buttons
            self.actions.tap(120, 120, "back_to_city")
            time.sleep(1.5)

        self.screen.screenshot()

    # =========================================================
    # STRATEGY HELPERS
    # =========================================================

    def _try_template(self, building_name):
        """Try OpenCV template matching. Returns (x, y) or None."""
        if not self.templates:
            return None
        result = self.templates.find(config.SCREENSHOT_PATH, building_name)
        if result:
            return (result[0], result[1])
        return None

    def _tap_and_verify(self, x, y, expected_name) -> bool:
        """Tap a position and verify the correct building menu opened.

        Uses FastScreenAnalyzer for quick classification (~50ms) instead of
        full OCR (~15-20s). Only runs OCR when a menu IS detected (to read
        the building name).

        Side effect: any building found (even wrong one) gets cached for
        future use. This builds the building map passively.
        """
        # Save current screenshot for change detection + template capture
        before_path = "/tmp/kingshot_before_tap.png"
        try:
            shutil.copy2(config.SCREENSHOT_PATH, before_path)
        except Exception:
            pass

        self.actions.tap(x, y, f"find_{expected_name}")
        time.sleep(1.5)

        # Take new screenshot
        self.screen.screenshot()

        # Quick check: did the screen change? (~5ms)
        if not self._screen_changed(before_path, config.SCREENSHOT_PATH):
            return False  # Nothing happened — empty ground

        # Screen changed — fast classify what opened (~50ms vs 15-20s)
        if self.analyzer:
            screen_type = self.analyzer.classify_fast(config.SCREENSHOT_PATH)
            # "ambiguous" could be a building menu we can't pixel-detect
            if screen_type == "ambiguous":
                # Check if a dialog panel appeared
                if self.analyzer.menu_opened(before_path, config.SCREENSHOT_PATH):
                    screen_type = "building_menu"
                else:
                    screen_type = "home_city"  # Changed but no menu
        else:
            screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)

        if screen_type not in ("building_menu", "training_menu"):
            # Not a building — close whatever opened and get back
            if screen_type != "home_city":
                self._recover_to_home()
            return False

        # Building menu opened — identify which building via targeted OCR
        found = self._identify_building_from_menu()
        if not found:
            # Couldn't identify — might still be the right building
            # Cache as unknown and close
            self._close_building_menu()
            return False

        found_display, found_coord = found

        # Cache this building's position (useful regardless of whether it's target)
        self.world.cache_position(found_coord, x, y)
        self._auto_capture_template(found_coord, before_path, x, y)

        if found_coord == expected_name:
            self.log(f"FINDER: ✓ Found {found_display} at ({x}, {y})")
            return True

        # Wrong building — still valuable for our map
        self.log(f"FINDER: Found {found_display} (wanted {expected_name}) at ({x}, {y})")
        self._close_building_menu()
        return False

    def _screen_changed(self, before_path, after_path, threshold=0.92):
        """Fast pixel comparison to detect if screen changed after a tap."""
        try:
            before = cv2.imread(before_path, cv2.IMREAD_GRAYSCALE)
            after = cv2.imread(after_path, cv2.IMREAD_GRAYSCALE)
            if before is None or after is None:
                return True

            # Resize to small size for speed (~5ms)
            size = (180, 320)
            before_small = cv2.resize(before, size)
            after_small = cv2.resize(after, size)

            # Normalized cross-correlation
            result = cv2.matchTemplate(
                before_small, after_small, cv2.TM_CCOEFF_NORMED)
            similarity = result[0][0]
            return similarity < threshold
        except Exception:
            return True  # Assume changed on error

    def _identify_building_from_menu(self):
        """Read building name from an open building_menu screen via targeted OCR.

        Uses building_header region (~3-5s) instead of full screen OCR (~15-20s).
        Returns (display_name, coord_key) or None.
        The building name is typically large text at the top of the menu dialog,
        often followed by "Lv.XX".
        """
        # Try targeted region first (faster — only header area)
        texts = self.ocr.read_building_name(config.SCREENSHOT_PATH)
        all_text_lower = " ".join(t["text"].lower() for t in texts)

        # Check for known building names (longest match first to avoid partial)
        sorted_names = sorted(
            KNOWN_BUILDING_NAMES.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        )
        for display_name, coord_key in sorted_names:
            if display_name.lower() in all_text_lower:
                return (display_name, coord_key)

        # Header region might miss it — try center_popup region
        if not texts:
            texts = self.ocr.read_region(config.SCREENSHOT_PATH, "center_popup")
            all_text_lower = " ".join(t["text"].lower() for t in texts)
            for display_name, coord_key in sorted_names:
                if display_name.lower() in all_text_lower:
                    return (display_name, coord_key)

        return None

    def _auto_capture_template(self, building_name, before_screenshot, x, y):
        """Capture a template image of a building from the before-tap screenshot.

        The building sprite is at approximately (x, y) in the before screenshot.
        We crop a region around it and save as a template for future matching.
        """
        if not self.templates:
            return
        if self.templates.has_template(building_name):
            return

        if not os.path.exists(before_screenshot):
            return

        # Crop a 200x200 region centered on the building position
        x1 = max(0, x - 100)
        y1 = max(0, y - 100)
        x2 = min(1440, x + 100)
        y2 = min(2560, y + 100)

        success = self.templates.capture_template(
            before_screenshot, building_name, x1, y1, x2, y2)
        if success:
            self.log(f"FINDER: Captured template for {building_name}")

    def _close_building_menu(self):
        """Close a building menu and return to city view."""
        from perception.coordinate_map import BUILDING_MENU
        x, y = BUILDING_MENU["close_building"]
        self.actions.tap(x, y, "close_menu")
        time.sleep(1.0)

    def _recover_to_home(self):
        """Try to get back to home_city from an unexpected screen."""
        close_positions = [
            (1300, 400), (1380, 100), (120, 120),
        ]
        for cx, cy in close_positions:
            self.actions.tap(cx, cy, "recover_close")
            time.sleep(0.8)
            self.screen.screenshot()
            if self.analyzer:
                screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
            else:
                screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)
            if screen_type == "home_city":
                return

    # =========================================================
    # CITY EXPLORATION (Strategy 4)
    # =========================================================

    def _explore_city(self, target_name: str) -> bool:
        """Systematic exploration: grid-tap the current view, then scroll
        in each direction and grid-tap again.

        One-time cost: ~2-4 minutes. After this, most buildings are mapped
        and cached for instant future access.
        """
        found_target = False
        buildings_found = 0

        # Phase 1: Reset camera and grid search the centered view
        self.log("FINDER: Exploring center view...")
        self._reset_camera()
        self.screen.screenshot()
        result = self._grid_search(target_name)
        if result:
            return True

        # Phase 2: Scroll in each direction and grid search
        for direction, x1, y1, x2, y2, duration in SCROLL_DIRECTIONS:
            self.log(f"FINDER: Scrolling {direction}...")

            # Reset camera to center before each scroll direction
            self._reset_camera()

            # Scroll to the new area
            self.actions.swipe(x1, y1, x2, y2, duration=duration)
            time.sleep(1.0)

            # Take fresh screenshot
            self.screen.screenshot()

            # Try template match first (fast, if we have templates)
            pos = self._try_template(target_name)
            if pos:
                self.log(f"FINDER: Template found after scroll {direction}")
                if self._tap_and_verify(pos[0], pos[1], target_name):
                    found_target = True
                    break

            # Grid search this view
            if self._grid_search(target_name):
                found_target = True
                break

        self._exploration_done = True

        # Navigate home to clean up
        self._navigate_home_quick()

        total_cached = len(self.world.state.get("cached_positions", {}))
        self.log(f"FINDER: Exploration complete. "
                 f"Total buildings mapped: {total_cached}. "
                 f"Target {'FOUND' if found_target else 'NOT FOUND'}.")

        return found_target

    def _grid_search(self, target_name: str) -> bool:
        """Tap a grid of positions on the current view, identifying buildings.

        Returns True if target_name was found (and its menu is open).
        Side effect: all buildings found are cached + templated.
        """
        for y in EXPLORE_GRID_Y:
            for x in EXPLORE_GRID_X:
                # Skip if this position is already a known building
                # (saves time on re-exploration)
                known = self._position_already_known(x, y)
                if known and known != target_name:
                    continue

                if self._tap_and_verify(x, y, target_name):
                    return True

                # Make sure we're still on home_city for next tap
                self.screen.screenshot()
                if self.analyzer:
                    screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
                else:
                    screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)
                if screen_type != "home_city":
                    self._recover_to_home()

        return False

    def _position_already_known(self, x, y, tolerance=80):
        """Check if a grid position is near a building we've already found."""
        cached = self.world.state.get("cached_positions", {})
        for name, pos in cached.items():
            if abs(pos["x"] - x) < tolerance and abs(pos["y"] - y) < tolerance:
                return name
        return None

    def _navigate_home_quick(self):
        """Quick home navigation without full ensure_home overhead.

        Taps close buttons then checks screen once. For use during
        exploration where we need speed over certainty.
        """
        self.screen.screenshot()
        if self.analyzer:
            screen_type = self.analyzer.classify(config.SCREENSHOT_PATH)
        else:
            screen_type = self.ocr.detect_screen_type(config.SCREENSHOT_PATH)
        if screen_type == "home_city":
            return

        # Quick close attempts
        self.actions.tap(1300, 400, "quick_close")
        time.sleep(0.5)
        self.actions.tap(100, 400, "tap_outside")
        time.sleep(0.8)

    # =========================================================
    # BULK CALIBRATION
    # =========================================================

    def calibrate_all(self) -> dict:
        """Run full city exploration to find and map ALL buildings.

        Returns dict of {building_name: (x, y)} for all buildings found.
        This is a one-time operation that should be run when the bot
        first starts or after a game update changes layouts.
        """
        self.log("FINDER: Starting full calibration...")
        start = time.time()

        # Use a dummy target that doesn't exist to force full exploration
        self._explore_city("__calibration_target__")

        elapsed = time.time() - start
        cached = self.world.state.get("cached_positions", {})
        result = {name: (p["x"], p["y"]) for name, p in cached.items()}

        self.log(f"FINDER: Calibration done in {elapsed:.0f}s. "
                 f"Found {len(result)} buildings: "
                 f"{', '.join(sorted(result.keys()))}")

        return result
