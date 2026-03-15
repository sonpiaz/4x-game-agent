"""
Fast Screen Analyzer — Classify game screens without OCR.

Uses pixel sampling and color analysis for <100ms classification.
Falls back to OCR only for ambiguous cases.

Key insight from ROK bot research: game UIs have consistent visual patterns
at fixed positions. We don't need to READ text to know WHAT screen we're on.

Performance: ~30-50ms per classify vs 15-20s for full OCR.
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FastScreenAnalyzer:
    """Pixel-based screen classifier for Kingshot.

    Resolution reference: 1440x2560 (BlueStacks portrait).
    Sampling positions are defined as fractions (0-1) for resolution independence.
    """

    def __init__(self, ocr=None):
        """
        Args:
            ocr: Optional GameOCR instance for fallback classification.
        """
        self.ocr = ocr
        self._stats = {"fast": 0, "ocr_fallback": 0}

    def classify(self, screenshot_path: str, allow_ocr_fallback: bool = True) -> str:
        """Classify screen type. Fast pixel check first, OCR fallback if needed.

        Returns: screen_type string (compatible with GameState constants).
        """
        self._stats["fast"] += 1

        result = self.classify_fast(screenshot_path)

        if result != "ambiguous":
            return result

        if not allow_ocr_fallback or not self.ocr:
            return "unknown"

        # Ambiguous — fall back to full OCR
        self._stats["ocr_fallback"] += 1
        return self.ocr.detect_screen_type(screenshot_path)

    def classify_fast(self, screenshot_path: str) -> str:
        """Pure pixel-based classification. <50ms, no OCR.

        Reliably detects:
        - home_city: bottom nav bar + top resource bar
        - popup_quit / popup_topup / popup_generic: dark overlay + dialog
        - building_menu: dialog panel visible, no nav bar
        - ambiguous: can't determine (needs OCR fallback)
        """
        img = cv2.imread(screenshot_path)
        if img is None:
            return "ambiguous"

        h, w = img.shape[:2]

        # Check key visual features
        has_nav = self._has_bottom_nav(img, w, h)
        overlay = self._overlay_level(img, w, h)
        has_top = self._has_top_bar(img, w, h)
        has_panel = self._has_dialog_panel(img, w, h)

        # Decision tree (ordered by frequency)
        if overlay > 0.5:
            return self._classify_popup(img, w, h)

        if has_nav:
            return "home_city"

        if has_panel and not has_nav:
            # Dialog panel without nav = building/training/research menu
            return "building_menu"

        if has_top and not has_nav and not has_panel:
            # Top bar visible but no nav or panel — could be many screens
            return "ambiguous"

        return "ambiguous"

    def screen_changed(self, before_path: str, after_path: str,
                       threshold: float = 0.92) -> bool:
        """Fast check if two screenshots are significantly different. ~5ms."""
        try:
            a = cv2.imread(before_path, cv2.IMREAD_GRAYSCALE)
            b = cv2.imread(after_path, cv2.IMREAD_GRAYSCALE)
            if a is None or b is None:
                return True

            size = (180, 320)
            a_small = cv2.resize(a, size)
            b_small = cv2.resize(b, size)

            result = cv2.matchTemplate(a_small, b_small, cv2.TM_CCOEFF_NORMED)
            similarity = result[0][0]
            return similarity < threshold
        except Exception:
            return True

    def menu_opened(self, before_path: str, after_path: str) -> bool:
        """Check if a menu/dialog appeared after a tap.

        More specific than screen_changed — verifies a dialog panel
        is now present in the lower screen area.
        """
        if not self.screen_changed(before_path, after_path):
            return False

        try:
            img = cv2.imread(after_path)
            if img is None:
                return False
            h, w = img.shape[:2]
            return self._has_dialog_panel(img, w, h)
        except Exception:
            return False

    # =========================================================
    # DETECTION HELPERS
    # =========================================================

    def _has_bottom_nav(self, img, w, h):
        """Detect bottom navigation bar.

        Kingshot's nav bar has a warm beige background (~brightness 150-180).
        The strongest signal is the CONTRAST between the dark area above
        the nav (quest/chat, ~50-80) and the bright nav bar below (~150-180).
        """
        # Primary: contrast between area above nav and nav area
        above = img[int(0.85 * h):int(0.91 * h), :]
        nav = img[int(0.92 * h):int(0.99 * h), :]

        if above.size == 0 or nav.size == 0:
            return False

        above_brightness = above.mean()
        nav_brightness = nav.mean()
        contrast = nav_brightness - above_brightness

        # Home city: dark area above (~50-80) + bright nav below (~150-180)
        # Contrast is typically > 60 on home_city, < 30 on other screens
        if contrast > 50 and nav_brightness > 120:
            return True

        # Secondary: check for warm-toned nav bar (R > G > B pattern)
        if nav_brightness > 130:
            b, g, r = cv2.split(nav)
            r_avg, g_avg, b_avg = r.mean(), g.mean(), b.mean()
            # Kingshot nav: warm tone (R ~170, G ~160, B ~140)
            if r_avg > g_avg > b_avg and r_avg > 130:
                return True

        return False

    def _overlay_level(self, img, w, h):
        """Measure popup overlay darkness. Returns 0-1.

        Popups darken screen edges while showing a bright center dialog.
        """
        edges = [
            img[int(0.12 * h):int(0.18 * h), 0:int(0.08 * w)],
            img[int(0.12 * h):int(0.18 * h), int(0.92 * w):w],
            img[int(0.82 * h):int(0.88 * h), 0:int(0.08 * w)],
            img[int(0.82 * h):int(0.88 * h), int(0.92 * w):w],
        ]
        edge_vals = [e.mean() for e in edges if e.size > 0]
        if not edge_vals:
            return 0

        avg_edge = np.mean(edge_vals)

        center = img[int(0.35 * h):int(0.65 * h), int(0.2 * w):int(0.8 * w)]
        center_val = center.mean() if center.size > 0 else avg_edge

        # Popup: dark edges (< 50) with brighter center, strong contrast
        if avg_edge < 50 and center_val > avg_edge + 30:
            return min(1.0, (center_val - avg_edge) / 80)

        return 0

    def _has_top_bar(self, img, w, h):
        """Check if top resource bar (power, gems, stamina) is visible.

        The top bar in Kingshot has a dark-ish background with colored elements.
        Average brightness is typically 60-120. Very dark (<15) = no top bar.
        Very bright (>180) = different screen entirely.
        """
        strip = img[0:int(0.05 * h), :]
        if strip.size == 0:
            return False
        brightness = strip.mean()
        # Top bar exists if brightness is in typical game UI range
        return 30 < brightness < 150

    def _has_dialog_panel(self, img, w, h):
        """Check for bright UI panel in the lower portion of the screen.

        Building, training, and research dialogs appear as bright panels
        in the bottom 30-40% of the screen. They have distinctive high
        brightness AND low color variance (uniform panel background).
        """
        panel = img[int(0.60 * h):int(0.85 * h), int(0.1 * w):int(0.9 * w)]
        if panel.size == 0:
            return False

        brightness = panel.mean()

        # City view (above panel) for comparison
        city = img[int(0.15 * h):int(0.45 * h), int(0.1 * w):int(0.9 * w)]
        city_brightness = city.mean() if city.size > 0 else brightness

        # Dialog panels have higher brightness than city AND are bright enough
        # Also check standard deviation — panels are more uniform than game world
        panel_std = panel.std()

        # Panel: bright (>120), brighter than city (+15), relatively uniform (std < 70)
        if brightness > 120 and brightness > city_brightness + 15 and panel_std < 70:
            return True

        # Alternative: very bright panel (>160) regardless of city comparison
        if brightness > 160 and panel_std < 60:
            return True

        return False

    def _classify_popup(self, img, w, h):
        """Differentiate popup types based on visual features."""
        # Check button area for red (quit) / green (confirm) buttons
        button_area = img[int(0.52 * h):int(0.62 * h), int(0.2 * w):int(0.8 * w)]
        if button_area.size == 0:
            return "popup_generic"

        b, g, r = cv2.split(button_area)
        total = max(button_area.shape[0] * button_area.shape[1], 1)

        # Red button presence → quit dialog
        red_count = np.sum((r > 150) & (r > g + 50) & (r > b + 50))
        if red_count / total > 0.02:
            return "popup_quit"

        # Colorful content → promotional/topup popup
        center = img[int(0.25 * h):int(0.45 * h), int(0.15 * w):int(0.85 * w)]
        if center.size > 0:
            avg_bgr = center.mean(axis=(0, 1))
            color_spread = np.std(avg_bgr)
            if color_spread > 15:
                return "popup_topup"

        return "popup_generic"

    def get_stats(self):
        total = self._stats["fast"]
        fb = self._stats["ocr_fallback"]
        return {
            "total": total,
            "ocr_fallbacks": fb,
            "fast_pct": round((total - fb) / max(total, 1) * 100, 1),
        }
