"""
Local OCR Engine - reads game text without API calls.
Uses PaddleOCR for text detection + recognition.
Extracts: power, gems, resources, timers, builders status, screen text.
"""
import os
import re
import logging

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from PIL import Image

logger = logging.getLogger(__name__)

# Suppress PaddleOCR noise
for name in ["ppocr", "paddle", "paddleocr", "paddlex"]:
    logging.getLogger(name).setLevel(logging.ERROR)


class GameOCR:
    """Local OCR engine for reading game screen text.

    IMPORTANT: OCR is slow (~15-20s per call on CPU).
    Use cached results via read_screen_once() to avoid redundant calls.
    """

    # Regions of interest (ROI) on 1440x2560 screen
    # Format: (x1, y1, x2, y2) - crop box
    REGIONS = {
        "top_bar": (0, 0, 1440, 120),
        "power_badge": (0, 50, 400, 120),
        "gems": (1100, 0, 1350, 55),
        "stamina": (300, 0, 550, 55),
        "rss_food": (550, 0, 900, 55),
        "vip": (1300, 50, 1440, 120),
        "quest_bar": (0, 2150, 1440, 2300),
        "chat_area": (0, 2300, 1440, 2430),
        "bottom_tabs": (0, 2430, 1440, 2560),
        "right_panel": (1050, 50, 1440, 900),
        "center_popup": (200, 600, 1240, 2000),
        "building_menu": (100, 1600, 1340, 2200),
        "building_header": (0, 200, 1440, 1200),  # Building name + level in dialog
        "timer_area": (1100, 500, 1440, 700),
        "full_screen": None,
    }

    def __init__(self):
        from paddleocr import PaddleOCR
        self._ocr = PaddleOCR(lang="en")
        self._initialized = True
        # Cache: avoid running OCR twice on the same screenshot
        self._cached_path = None
        self._cached_texts = None

    def _get_cached_or_read(self, screenshot_path):
        """Return cached OCR results if same file, else run OCR once."""
        # Check if file has changed (by mtime)
        try:
            mtime = os.path.getmtime(screenshot_path)
        except OSError:
            mtime = None

        cache_key = f"{screenshot_path}:{mtime}"
        if self._cached_path == cache_key and self._cached_texts is not None:
            return self._cached_texts

        # Run OCR once, cache results
        self._cached_texts = self._run_ocr(screenshot_path)
        self._cached_path = cache_key
        return self._cached_texts

    def _run_ocr(self, image_path):
        """Run PaddleOCR on an image file. Returns list of text dicts."""
        results = list(self._ocr.predict(image_path))
        texts = []
        for res in results:
            rec_texts = res.get("rec_texts", [])
            rec_scores = res.get("rec_scores", [])
            dt_polys = res.get("dt_polys", [])
            for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                if score < 0.5 or not text.strip():
                    continue
                box = dt_polys[i] if i < len(dt_polys) else [[0, 0]] * 4
                cx = int((box[0][0] + box[2][0]) / 2)
                cy = int((box[0][1] + box[2][1]) / 2)
                texts.append({
                    "text": text.strip(),
                    "confidence": round(score, 3),
                    "x": cx,
                    "y": cy,
                })
        return texts

    def read_region(self, screenshot_path, region_name="full_screen"):
        """OCR a specific region of the screenshot.
        For full_screen, uses cache. For specific regions, crops and runs fresh OCR.
        """
        if region_name == "full_screen":
            return self._get_cached_or_read(screenshot_path)

        # Crop and run fresh OCR for specific regions
        img = Image.open(screenshot_path)
        region = self.REGIONS.get(region_name)
        if not region:
            return self._get_cached_or_read(screenshot_path)

        w, h = img.size
        sx, sy = w / 1440, h / 2560
        crop_box = (
            int(region[0] * sx), int(region[1] * sy),
            int(region[2] * sx), int(region[3] * sy),
        )
        img = img.crop(crop_box)
        offset_x, offset_y = crop_box[0], crop_box[1]

        temp_path = "/tmp/kingshot_ocr_crop.png"
        img.save(temp_path)

        raw_texts = self._run_ocr(temp_path)
        # Adjust coordinates to full-screen space
        for t in raw_texts:
            t["x"] += offset_x
            t["y"] += offset_y
        return raw_texts

    def read_all_text(self, screenshot_path):
        """Full screen OCR - returns cached results if same file."""
        return self._get_cached_or_read(screenshot_path)

    def read_game_state(self, screenshot_path):
        """Extract structured game state from screenshot.
        Returns dict with power, gems, stamina, timers, screen_texts, etc.
        """
        state = {
            "power": None,
            "gems": None,
            "stamina": None,
            "stamina_max": None,
            "food": None,
            "vip_level": None,
            "quest_text": None,
            "active_timers": [],
            "screen_texts": [],
            "has_popup": False,
            "popup_texts": [],
        }

        # Read full screen for comprehensive text
        all_texts = self.read_all_text(screenshot_path)
        state["screen_texts"] = [t["text"] for t in all_texts]
        all_text_joined = " ".join(state["screen_texts"]).lower()

        # Extract power (format: "314,444" or "314444")
        for t in all_texts:
            text = t["text"].replace(",", "").replace(" ", "")
            # Power is typically a large number near top-left
            if t["y"] < 200 and re.match(r"^\d{4,}$", text):
                val = int(text)
                if 10000 < val < 100000000:  # Reasonable power range
                    if state["power"] is None or val > state["power"]:
                        state["power"] = val

        # Extract gems (format: "4,492" near top-right)
        for t in all_texts:
            text = t["text"].replace(",", "").replace(" ", "")
            if t["x"] > 900 and t["y"] < 100 and re.match(r"^\d{2,}$", text):
                val = int(text)
                if 0 < val < 1000000:
                    state["gems"] = val

        # Extract stamina (format: "24/24")
        for t in all_texts:
            m = re.match(r"(\d+)\s*/\s*(\d+)", t["text"])
            if m and t["y"] < 100:
                state["stamina"] = int(m.group(1))
                state["stamina_max"] = int(m.group(2))

        # Extract VIP level
        for t in all_texts:
            m = re.search(r"VIP\s*(\d+)", t["text"], re.IGNORECASE)
            if m:
                state["vip_level"] = int(m.group(1))

        # Extract quest/objective text
        for t in all_texts:
            if t["y"] > 2000 and t["y"] < 2350:
                if any(kw in t["text"].lower() for kw in [
                    "clear", "stage", "upgrade", "train", "collect",
                    "complete", "reach", "defeat",
                ]):
                    state["quest_text"] = t["text"]
                    break

        # Extract active timers (format: "HH:MM:SS" or "MM:SS")
        for t in all_texts:
            if re.match(r"\d{1,2}:\d{2}(:\d{2})?$", t["text"]):
                state["active_timers"].append({
                    "timer": t["text"],
                    "x": t["x"],
                    "y": t["y"],
                })

        # Detect popups
        popup_keywords = [
            "quit game", "confirmation", "purchase", "top-up",
            "buy", "confirm", "cancel", "close",
        ]
        for t in all_texts:
            if 300 < t["x"] < 1100 and 600 < t["y"] < 2000:
                if any(kw in t["text"].lower() for kw in popup_keywords):
                    state["has_popup"] = True
                    state["popup_texts"].append(t["text"])

        # Extract food/resources (format: "397.7K" or "1.2M")
        for t in all_texts:
            m = re.match(r"([\d.]+)\s*([KMB])?$", t["text"], re.IGNORECASE)
            if m and t["y"] < 100 and 400 < t["x"] < 900:
                val = float(m.group(1))
                suffix = (m.group(2) or "").upper()
                if suffix == "K":
                    val *= 1000
                elif suffix == "M":
                    val *= 1000000
                elif suffix == "B":
                    val *= 1000000000
                state["food"] = int(val)

        return state

    def read_building_name(self, screenshot_path):
        """Read building name from an open building dialog using targeted OCR.

        Only OCRs the header area of the dialog (where name + level appear),
        not the entire screen. ~3-5s instead of 15-20s.

        Returns list of text dicts from the building_header region.
        """
        return self.read_region(screenshot_path, "building_header")

    def read_timers_targeted(self, screenshot_path, regions):
        """Read timer text from specific screen regions.

        Args:
            screenshot_path: Path to screenshot
            regions: List of (x, y, w, h) tuples defining crop areas
                     in device coordinates (1440x2560 reference)

        Returns list of {timer: "HH:MM:SS", x: int, y: int}
        """
        timers = []
        img = Image.open(screenshot_path)
        img_w, img_h = img.size
        sx, sy = img_w / 1440, img_h / 2560

        for rx, ry, rw, rh in regions:
            crop_box = (
                int(rx * sx), int(ry * sy),
                int((rx + rw) * sx), int((ry + rh) * sy),
            )
            crop = img.crop(crop_box)

            temp_path = "/tmp/kingshot_timer_crop.png"
            crop.save(temp_path)

            texts = self._run_ocr(temp_path)
            for t in texts:
                if re.match(r"\d{1,2}:\d{2}(:\d{2})?$", t["text"]):
                    timers.append({
                        "timer": t["text"],
                        "x": int(rx + t["x"] / sx),
                        "y": int(ry + t["y"] / sy),
                    })

        return timers

    def detect_screen_type(self, screenshot_path):
        """Classify current screen based on OCR text.
        Returns: screen type string matching GameState constants.

        Detection priority:
        1. home_city — right panel icons, bottom tabs, or power+VIP badge
        2. popups — quit, purchase, topup (only center-area text, not right panel)
        3. battle screens — prep, active, result
        4. specific screens — conquest, building, research, training, etc.
        """
        texts = self.read_all_text(screenshot_path)
        all_text = " ".join(t["text"].lower() for t in texts)

        # Pre-compute: are bottom nav tabs visible? (strong home_city signal)
        bottom_tabs = ["conquest", "heroes", "backpack", "shop", "alliance", "world"]
        visible_tabs = sum(1 for tab in bottom_tabs if tab in all_text)

        # Pre-compute: right panel icons visible? (home_city indicator)
        # These icons (Events, Deals, 7-Day, Survey, Path of Growth) only appear
        # on the home city screen in the right sidebar (x > 1000, y < 900)
        right_panel_icons = ["events", "deals", "7-day", "survey", "pathof",
                             "path of growth", "top-up gift"]
        right_panel_texts = [t for t in texts
                             if t["x"] > 1000 and t["y"] < 900]
        right_panel_matches = sum(
            1 for icon in right_panel_icons
            if any(icon in t["text"].lower() for t in right_panel_texts)
        )

        # === HOME CITY (highest priority) ===
        # Method 1: 3+ bottom tab names visible
        if visible_tabs >= 3:
            return "home_city"
        # Method 2: Right panel has 3+ recognizable icons
        if right_panel_matches >= 3:
            return "home_city"
        # Method 3: Right panel has 2+ icons AND quest text visible (bottom area)
        has_quest = any(t["y"] > 2100 and t["y"] < 2300 for t in texts)
        if right_panel_matches >= 2 and has_quest:
            return "home_city"
        # Method 4: Power number + VIP badge visible at top
        has_power_badge = False
        for t in texts:
            clean = t["text"].replace(",", "").replace(" ", "")
            if t["y"] < 200 and t["x"] < 500 and re.match(r"^\d{5,}$", clean):
                has_power_badge = True
                break
        has_vip = any("vip" in t["text"].lower() and t["y"] < 200 for t in texts)
        if has_power_badge and has_vip:
            return "home_city"

        # === POPUPS (must dismiss before continuing) ===
        if "quit game" in all_text:
            return "popup_quit"

        # Top-up / purchase popups — only trigger on CENTER text, not right panel
        purchase_signals = [
            "value pack", "rookie", "limited offer",
            "special gift", "boost city",
            "construction expert", "eternal legend",
            "master's collection", "crafter's diligence",
            "supreme deal", "discount", "first purchase",
            "resident status",
        ]
        # Use center-only text for popup detection (x: 100-1000, y: 300-2200)
        # Excludes right panel (x > 1000) to prevent false positives on home
        center_only_texts = [t for t in texts
                             if 100 < t["x"] < 1000 and 300 < t["y"] < 2200]
        center_text = " ".join(t["text"].lower() for t in center_only_texts)
        if any(sig in center_text for sig in purchase_signals):
            if len(center_only_texts) >= 3:
                return "popup_topup"

        # Also check for "top-up" but only in the center area, not right panel
        if "top-up" in center_text and len(center_only_texts) >= 5:
            return "popup_topup"

        if "purchase" in all_text and ("confirm" in all_text or "cancel" in all_text):
            return "popup_purchase"

        if "confirmation" in all_text and ("confirm" in all_text or "cancel" in all_text):
            return "popup_generic"

        # === BATTLE SCREENS ===
        if "quick deploy" in all_text or ("deploy" in all_text and "fight" in all_text):
            return "battle_prep"
        if "auto" in all_text and "x1" in all_text:
            return "battle_active"
        for t in texts:
            if t["text"].lower() in ("victory", "defeat", "victory!", "defeat!"):
                if 300 < t["x"] < 1100 and t["y"] < 800:
                    return "battle_result"

        # === CONQUEST ===
        # Must have "conquest" in MAIN area (not just quest bar text)
        conquest_main = any(
            "conquest" in t["text"].lower() and t["y"] < 2100
            for t in texts
        )
        if conquest_main and "leaderboard" in all_text:
            return "conquest_screen"
        if "conquer" in all_text:
            return "conquest_screen"

        # Building/upgrade (game shows "Lv.X" not "Level X")
        if "upgrade" in all_text and (
            "level" in all_text or "lv." in all_text or "lv" in all_text
            or "require" in all_text or "production" in all_text
        ):
            return "building_menu"
        if "research" in all_text and ("academy" in all_text or "speed" in all_text):
            return "research_tree"
        if "train" in all_text and (
            "barracks" in all_text or "range" in all_text
            or "stable" in all_text or "infantry" in all_text
            or "cavalry" in all_text or "archer" in all_text
        ):
            return "training_menu"

        # Events screen
        if "events" in all_text and ("calendar" in all_text or "strongest" in all_text
                                      or "private" in all_text):
            return "unknown"

        # Hero management
        if "hero" in all_text and ("skill" in all_text or "shard" in all_text):
            return "hero_screen"

        # Alliance
        if "alliance" in all_text and (
            "tech" in all_text or "help" in all_text or "member" in all_text
        ):
            return "alliance_screen"

        # World map
        if "search" in all_text and "kingdom" in all_text:
            return "world_map"

        return "unknown"
