"""
Screen Analyzer — Detect which game screen the bot is currently on.

Two approaches (use one or both):
1. Fast pixel-based classification (<100ms) — check colors at fixed positions
2. OCR-based classification (~15-20s) — read text and match patterns

Fast classification should handle 80%+ of cases.
OCR fallback for ambiguous screens.
"""
import cv2
import numpy as np


class ScreenAnalyzer:
    """Pixel-based screen classifier for your game.

    Customize the detection rules for your game's UI patterns.
    """

    def __init__(self, ocr=None):
        self.ocr = ocr

    def classify(self, screenshot_path: str) -> str:
        """Classify screen type. Returns a string like 'home_city', 'popup', etc."""
        result = self.classify_fast(screenshot_path)
        if result != "unknown" or not self.ocr:
            return result
        # Fallback to OCR for ambiguous cases
        return self._classify_ocr(screenshot_path)

    def classify_fast(self, screenshot_path: str) -> str:
        """Pure pixel-based classification. <100ms.

        TODO: Add rules for your game's screens.
        Check colors at known positions to identify screen type.
        """
        img = cv2.imread(screenshot_path)
        if img is None:
            return "unknown"

        # h, w = img.shape[:2]

        # Example: check if bottom nav bar exists
        # strip = img[int(0.94*h):int(0.99*h), :]
        # if strip.mean() < 100:  # Dark nav bar
        #     return "home_city"

        return "unknown"

    def _classify_ocr(self, screenshot_path: str) -> str:
        """OCR-based classification. Slower but more accurate."""
        if not self.ocr:
            return "unknown"
        texts = self.ocr.read_all(screenshot_path)
        all_text = " ".join(t["text"].lower() for t in texts)

        # Example: detect screens by text patterns
        # if "upgrade" in all_text and "level" in all_text:
        #     return "building_menu"

        return "unknown"
