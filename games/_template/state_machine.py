"""
Game State Machine — Track which screen the bot is on.

Define all possible game states (screens) and handle transitions.
Popup states are managed with a stack (push on appear, pop on dismiss).
"""
import time


# Define your game's screen states
STATES = {
    "home_city",
    "world_map",
    "building_menu",
    "popup_quit",
    "popup_generic",
    "loading",
    "unknown",
    # Add more states for your game
}

POPUP_STATES = {
    "popup_quit",
    "popup_generic",
    # Add popup states that need auto-dismissing
}


class GameFSM:
    """Finite State Machine for game screen management."""

    def __init__(self, actions, screen_analyzer, log_fn=None):
        self.actions = actions
        self.analyzer = screen_analyzer
        self.log = log_fn or print
        self.current_state = "unknown"
        self.state_stack = []
        self.stuck_counter = 0
        self.last_state_change = time.time()

    def update(self, screenshot_path_or_type: str) -> str:
        """Update state from screenshot path or pre-classified type string."""
        if screenshot_path_or_type.endswith((".png", ".jpg", ".jpeg")):
            new_state = self.analyzer.classify(screenshot_path_or_type)
        else:
            new_state = screenshot_path_or_type

        if new_state != self.current_state:
            if new_state in POPUP_STATES:
                self.state_stack.append(self.current_state)
            elif self.current_state in POPUP_STATES and self.state_stack:
                self.state_stack.pop()

            self.current_state = new_state
            self.stuck_counter = 0
            self.last_state_change = time.time()
        else:
            self.stuck_counter += 1

        return self.current_state

    def is_popup(self) -> bool:
        return self.current_state in POPUP_STATES

    def handle_popup(self) -> bool:
        """Auto-dismiss known popups. Customize for your game.

        Returns True if handled.
        """
        # Example:
        # if self.current_state == "popup_quit":
        #     from coordinate_map import POPUP
        #     x, y = POPUP["cancel"]
        #     self.actions.tap(x, y, "cancel_quit")
        #     time.sleep(1.0)
        #     return True
        return False

    def is_stuck(self, threshold: int = 5) -> bool:
        return self.stuck_counter >= threshold

    def is_home(self) -> bool:
        return self.current_state == "home_city"
