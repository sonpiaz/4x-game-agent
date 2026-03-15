"""
OCR Engine — PaddleOCR wrapper for reading game screen text.

This module provides a thin, game-agnostic OCR interface.
Game-specific text parsing (power, gems, screen detection) belongs
in each game's own module, NOT here.
"""
import os
import re
import logging

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

logger = logging.getLogger(__name__)

# Suppress PaddleOCR noise
for _name in ["ppocr", "paddle", "paddleocr", "paddlex"]:
    logging.getLogger(_name).setLevel(logging.ERROR)


class OCREngine:
    """PaddleOCR wrapper. Reads text from screenshots.

    Returns list of dicts: [{text, confidence, x, y}, ...]
    where (x, y) is the center of the detected text bounding box.
    """

    def __init__(self, lang: str = "en"):
        from paddleocr import PaddleOCR
        self._ocr = PaddleOCR(lang=lang)
        self._cached_path = None
        self._cached_texts = None

    def read_all(self, image_path: str) -> list:
        """Full-screen OCR. Returns cached results if same file (by mtime)."""
        try:
            mtime = os.path.getmtime(image_path)
        except OSError:
            mtime = None

        cache_key = f"{image_path}:{mtime}"
        if self._cached_path == cache_key and self._cached_texts is not None:
            return self._cached_texts

        self._cached_texts = self._run(image_path)
        self._cached_path = cache_key
        return self._cached_texts

    def read_region(self, image_path: str, crop_box: tuple) -> list:
        """OCR a specific region. crop_box = (x1, y1, x2, y2) in pixels.

        Returns text dicts with coordinates adjusted to full-image space.
        """
        from PIL import Image
        img = Image.open(image_path)
        x1, y1, x2, y2 = crop_box
        cropped = img.crop((x1, y1, x2, y2))

        temp_path = "/tmp/4x_ocr_crop.png"
        cropped.save(temp_path)

        texts = self._run(temp_path)
        for t in texts:
            t["x"] += x1
            t["y"] += y1
        return texts

    def _run(self, image_path: str) -> list:
        """Run PaddleOCR on an image file."""
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
