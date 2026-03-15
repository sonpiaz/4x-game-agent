"""
Game State Machine - Bot always knows where it is.
Handles screen transitions, popup interrupts, and recovery.

States are determined by local OCR, not by asking Claude.
"""
import time
import logging

logger = logging.getLogger(__name__)


class GameState:
    """Represents a recognized game screen state."""

    # All known game states
    HOME_CITY = "home_city"
    WORLD_MAP = "world_map"
    BUILDING_MENU = "building_menu"
    RESEARCH_TREE = "research_tree"
    TRAINING_MENU = "training_menu"
    CONQUEST_SCREEN = "conquest_screen"
    HERO_SCREEN = "hero_screen"
    ALLIANCE_SCREEN = "alliance_screen"
    BATTLE_PREP = "battle_prep"
    BATTLE_ACTIVE = "battle_active"
    BATTLE_RESULT = "battle_result"
    POPUP_QUIT = "popup_quit"
    POPUP_TOPUP = "popup_topup"
    POPUP_PURCHASE = "popup_purchase"
    POPUP_GENERIC = "popup_generic"
    LOADING = "loading"
    UNKNOWN = "unknown"

    # States that are popups (must be dismissed before continuing)
    POPUP_STATES = {
        POPUP_QUIT, POPUP_TOPUP, POPUP_PURCHASE, POPUP_GENERIC,
    }


class GameFSM:
    """Finite State Machine for game screen management.

    Tracks current state, handles transitions, and manages popup interrupts
    using a state stack (popups push onto stack, dismissing pops back).
    """

    def __init__(self, actions, ocr_engine, log_fn=None):
        self.actions = actions
        self.ocr = ocr_engine
        self.log = log_fn or logger.info
        self.current_state = GameState.UNKNOWN
        self.state_stack = []  # For popup interrupts
        self.state_history = []  # Last 20 states
        self.stuck_counter = 0  # Same state repeat counter
        self.last_state_change = time.time()

    def update(self, screenshot_path_or_type):
        """Detect current screen state.

        Args:
            screenshot_path_or_type: Either a file path (runs OCR) or
                a pre-classified screen type string (skips OCR).
        """
        if screenshot_path_or_type in (
            s for s in dir(GameState) if not s.startswith("_")
            and isinstance(getattr(GameState, s), str)
        ):
            # It's already a classified type
            new_state = screenshot_path_or_type
        elif not screenshot_path_or_type.endswith((".png", ".jpg", ".jpeg")):
            # Looks like a screen type string
            new_state = screenshot_path_or_type
        else:
            # It's a file path — run OCR (uses cache)
            new_state = self.ocr.detect_screen_type(screenshot_path_or_type)

        old_state = self.current_state

        if new_state != old_state:
            self.state_history.append({
                "from": old_state,
                "to": new_state,
                "time": time.time(),
            })
            if len(self.state_history) > 20:
                self.state_history.pop(0)

            # Popup appeared: push previous state
            if new_state in GameState.POPUP_STATES:
                self.state_stack.append(old_state)
                self.log(f"FSM: POPUP detected: {new_state} (was: {old_state})")
            # Popup dismissed: pop back
            elif old_state in GameState.POPUP_STATES and self.state_stack:
                expected = self.state_stack.pop()
                self.log(f"FSM: Popup dismissed, back to: {new_state} (expected: {expected})")
            else:
                self.log(f"FSM: {old_state} → {new_state}")

            self.current_state = new_state
            self.stuck_counter = 0
            self.last_state_change = time.time()
        else:
            self.stuck_counter += 1

        return self.current_state

    def is_popup(self):
        """Check if current state is a popup that needs dismissing."""
        return self.current_state in GameState.POPUP_STATES

    def handle_popup(self):
        """Auto-dismiss known popups. Returns True if handled."""
        from perception.coordinate_map import POPUP, scale_coords

        if self.current_state == GameState.POPUP_QUIT:
            self.log("FSM: Auto-closing quit dialog → tap Cancel")
            x, y = POPUP["quit_cancel"]
            self.actions.tap(x, y, "cancel_quit")
            time.sleep(1.0)
            return True

        if self.current_state == GameState.POPUP_TOPUP:
            self.log("FSM: Auto-closing top-up popup → tap X")
            # Try multiple close positions
            for key in ["topup_close", "close_x", "close_x_high"]:
                x, y = POPUP[key]
                self.actions.tap(x, y, f"close_{key}")
                time.sleep(0.5)
            return True

        if self.current_state == GameState.POPUP_PURCHASE:
            self.log("FSM: Auto-closing purchase popup → tap Cancel")
            x, y = POPUP["cancel"]
            self.actions.tap(x, y, "cancel_purchase")
            time.sleep(1.0)
            return True

        if self.current_state == GameState.POPUP_GENERIC:
            self.log("FSM: Auto-closing generic popup → tap X")
            x, y = POPUP["close_x"]
            self.actions.tap(x, y, "close_popup")
            time.sleep(1.0)
            return True

        return False

    def is_stuck(self, threshold=5):
        """Check if we've been in the same state too long."""
        return self.stuck_counter >= threshold

    def time_in_state(self):
        """Seconds spent in current state."""
        return time.time() - self.last_state_change

    def is_home(self):
        """Check if we're on the main city screen."""
        return self.current_state == GameState.HOME_CITY

    def needs_navigation(self, target_state):
        """Check if we need to navigate to reach target state."""
        return self.current_state != target_state

    def get_status(self):
        """Return FSM status for dashboard/logging."""
        return {
            "current_state": self.current_state,
            "stuck_counter": self.stuck_counter,
            "time_in_state": round(self.time_in_state(), 1),
            "state_stack_depth": len(self.state_stack),
            "is_popup": self.is_popup(),
        }
