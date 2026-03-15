"""
Template Matching — Find UI elements by visual appearance using OpenCV.

Game-agnostic: works with any game at any resolution on emulators.
Matches visual patterns (building sprites, buttons, icons) regardless
of screen scroll position.
"""
import os
import cv2
import numpy as np


class TemplateMatcher:
    """Find UI elements using OpenCV template matching."""

    def __init__(self, template_dir: str, log_fn=None):
        self.template_dir = template_dir
        self.log = log_fn or print
        self._templates = {}  # name -> (cv2_image, w, h)
        self._load_templates()

    def _load_templates(self):
        """Load all .png template images from template_dir."""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
            return

        for fname in os.listdir(self.template_dir):
            if not fname.endswith(".png"):
                continue
            name = fname[:-4]
            path = os.path.join(self.template_dir, fname)
            img = cv2.imread(path)
            if img is not None:
                h, w = img.shape[:2]
                self._templates[name] = (img, w, h)

        if self._templates:
            self.log(f"TEMPLATES: Loaded {len(self._templates)} templates")

    def find(self, screenshot_path: str, template_name: str,
             threshold: float = 0.7):
        """Find a template in a screenshot (multi-scale).

        Returns (x, y, confidence) of best match center, or None.
        """
        if template_name not in self._templates:
            return None

        screen = cv2.imread(screenshot_path)
        if screen is None:
            return None

        template, tw, th = self._templates[template_name]
        screen_h, screen_w = screen.shape[:2]

        best_val = 0
        best_loc = None
        best_tw, best_th = tw, th

        scales = [1.0]
        for scale in scales:
            stw = int(tw * scale)
            sth = int(th * scale)

            if stw >= screen_w or sth >= screen_h:
                continue
            if stw < 10 or sth < 10:
                continue

            t = template if scale == 1.0 else cv2.resize(template, (stw, sth))
            result = cv2.matchTemplate(screen, t, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_tw, best_th = stw, sth

            if scale == 1.0 and max_val >= threshold:
                break
            if scale == 1.0 and max_val < threshold:
                scales.extend([0.9, 1.1, 0.8, 1.2])

        if best_val >= threshold and best_loc is not None:
            cx = best_loc[0] + best_tw // 2
            cy = best_loc[1] + best_th // 2
            return (cx, cy, round(best_val, 3))
        return None

    def find_all(self, screenshot_path: str, template_name: str,
                 threshold: float = 0.7, max_results: int = 10) -> list:
        """Find all occurrences of a template. Returns [(x, y, conf), ...]."""
        if template_name not in self._templates:
            return []

        screen = cv2.imread(screenshot_path)
        if screen is None:
            return []

        template, tw, th = self._templates[template_name]
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

        locations = np.where(result >= threshold)
        matches = []
        for pt in zip(*locations[::-1]):
            cx = pt[0] + tw // 2
            cy = pt[1] + th // 2
            conf = float(result[pt[1], pt[0]])
            matches.append((cx, cy, round(conf, 3)))

        if not matches:
            return []

        # Deduplicate close matches (within 50px)
        matches.sort(key=lambda m: m[2], reverse=True)
        deduped = [matches[0]]
        for m in matches[1:]:
            if not any(abs(m[0] - d[0]) < 50 and abs(m[1] - d[1]) < 50
                       for d in deduped):
                deduped.append(m)
            if len(deduped) >= max_results:
                break
        return deduped

    def capture_template(self, screenshot_path: str, name: str,
                         x1: int, y1: int, x2: int, y2: int) -> bool:
        """Capture a region as a new template for future matching."""
        screen = cv2.imread(screenshot_path)
        if screen is None:
            return False

        crop = screen[y1:y2, x1:x2]
        if crop.size == 0:
            return False

        os.makedirs(self.template_dir, exist_ok=True)
        path = os.path.join(self.template_dir, f"{name}.png")
        cv2.imwrite(path, crop)

        h, w = crop.shape[:2]
        self._templates[name] = (crop, w, h)
        self.log(f"TEMPLATE: Captured '{name}' ({w}x{h}px)")
        return True

    def has_template(self, name: str) -> bool:
        return name in self._templates

    def list_templates(self) -> list:
        return list(self._templates.keys())
