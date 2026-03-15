"""
Static UI Coordinate Map for Kingshot.
Resolution: 1440x2560 (BlueStacks portrait)

All coordinates are absolute device coordinates.
No AI needed to know where things are — just tap directly.
"""


# Bottom navigation tabs (y ≈ 2493)
TABS = {
    "conquest":  (95, 2493),
    "heroes":    (287, 2493),
    "backpack":  (480, 2493),
    "shop":      (670, 2493),
    "alliance":  (918, 2493),
    "world":     (1345, 2493),
}

# Common popup buttons
POPUP = {
    # Quit game dialog
    "quit_cancel":   (500, 1450),
    "quit_confirm":  (940, 1450),
    # Generic popup close (X button, top-right of popup)
    "close_x":       (1200, 300),
    "close_x_high":  (1350, 150),
    "close_x_mid":   (1200, 500),
    # Purchase/top-up popup close
    "topup_close":   (1300, 250),
    # Generic confirm/cancel
    "confirm":       (940, 1600),
    "cancel":        (500, 1600),
}

# Resource collection sweep points (for floating icons on base)
RESOURCE_SWEEP = [
    # 5x5 grid covering base area
    (200, 500), (450, 500), (700, 500), (950, 500), (1200, 500),
    (200, 750), (450, 750), (700, 750), (950, 750), (1200, 750),
    (200, 1000), (450, 1000), (700, 1000), (950, 1000), (1200, 1000),
    (200, 1250), (450, 1250), (700, 1250), (950, 1250), (1200, 1250),
    (200, 1500), (450, 1500), (700, 1500), (950, 1500), (1200, 1500),
]

# Right-side panel icons (dismiss/close area)
RIGHT_PANEL = {
    "path_of_growth": (1350, 120),
    "events":         (1400, 85),
    "deals":          (1380, 340),
    "topup_gift":     (1108, 384),
    "survey":         (1106, 620),
    "7day":           (1376, 825),
}

# Building positions (calibrated from screenshot TC9 layout)
# Reference: 1440x2560 device coords, verified against /tmp/kingshot_screen.png
BUILDINGS = {
    "town_center":   (720, 850),
    "wall":          (720, 400),
    "academy":       (980, 620),
    "hospital":      (310, 1080),
    "barracks":      (350, 1400),
    "archery_range": (680, 1500),
    "stables":       (1040, 1360),
    "embassy":       (330, 700),
}

# Building upgrade dialog buttons
BUILDING_MENU = {
    "upgrade_button":    (720, 2100),
    "info_button":       (720, 1800),
    "confirm_upgrade":   (720, 1500),
    "cancel_upgrade":    (400, 1500),
    "help_button":       (1100, 1200),
    "close_building":    (1300, 400),
}

# Training interface
TRAINING = {
    "train_button":      (720, 2000),
    "max_button":        (1000, 1400),
    "increase_count":    (900, 1400),
    "confirm_train":     (720, 1800),
}

# Alliance screen
ALLIANCE = {
    "help_all":          (720, 400),
    "tech_tab":          (400, 300),
    "donate_button":     (720, 1800),
}

# Conquest screen
CONQUEST = {
    "battle_button":     (720, 1200),
    "confirm_battle":    (720, 1600),
    "collect_reward":    (720, 1800),
}

# Hero screen
HERO = {
    "first_hero":        (300, 500),
    "skills_tab":        (600, 300),
    "skill_upgrade":     (720, 1600),
}

# Daily claim positions (notifications, rewards)
CLAIM = {
    "claim_center":      (720, 1800),
    "claim_mid":         (720, 1600),
    "claim_lower":       (720, 2000),
    "claim_right":       (1100, 900),
    "claim_right2":      (1100, 1200),
}


def get_coords(category, element):
    """Get coordinates for a UI element.
    Usage: get_coords('TABS', 'conquest') → (95, 2493)
    """
    maps = {
        "TABS": TABS,
        "POPUP": POPUP,
        "BUILDINGS": BUILDINGS,
        "BUILDING_MENU": BUILDING_MENU,
        "TRAINING": TRAINING,
        "ALLIANCE": ALLIANCE,
        "CONQUEST": CONQUEST,
        "HERO": HERO,
        "CLAIM": CLAIM,
    }
    category_map = maps.get(category, {})
    return category_map.get(element)


def scale_coords(x, y, device_w, device_h):
    """Scale coordinates from 1440x2560 reference to actual device resolution."""
    sx = device_w / 1440
    sy = device_h / 2560
    return int(x * sx), int(y * sy)
