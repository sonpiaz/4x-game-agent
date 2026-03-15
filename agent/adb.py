"""
ADB Device Interface — Screenshot capture + input actions.

Works with any Android emulator (BlueStacks, LDPlayer, Nox, etc.)
or physical device connected via ADB.

Coordinates are in device pixel space. The caller is responsible
for mapping game UI coordinates to device coordinates.
"""
import subprocess
import base64
import io
import os
import time
import random
from PIL import Image


class GameScreen:
    """ADB screenshot capture with Claude API compression."""

    def __init__(self, device: str = "emulator-5554",
                 screenshot_path: str = "/tmp/game_screen.png",
                 max_compress_dim: int = 1280):
        self.device = device
        self.screenshot_path = screenshot_path
        self.max_compress_dim = max_compress_dim
        self.device_w = 0
        self.device_h = 0

    def _adb(self, *args):
        cmd = ["adb", "-s", self.device] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode

    def connect(self) -> bool:
        """Connect to ADB device. Returns True if connected."""
        out, _ = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True
        ).stdout, 0
        if self.device in out:
            self._detect_resolution()
            return True
        out, code = self._adb("connect", self.device)
        connected = "connected" in out.lower() or "already" in out.lower()
        if connected:
            self._detect_resolution()
        return connected

    def _detect_resolution(self):
        """Detect actual device resolution from a test screenshot."""
        self._adb("shell", "screencap", "-p", "/sdcard/screen.png")
        self._adb("pull", "/sdcard/screen.png", self.screenshot_path)
        if os.path.exists(self.screenshot_path):
            img = Image.open(self.screenshot_path)
            self.device_w, self.device_h = img.size

    def is_connected(self) -> bool:
        out, _ = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True
        ).stdout, 0
        return self.device in out

    def screenshot(self, retries: int = 3):
        """Take screenshot, return (base64, scale_x, scale_y).

        The base64 image is compressed for LLM APIs.
        Scale factors convert LLM coordinates back to device coordinates:
            device_x = llm_x * scale_x
        """
        for attempt in range(retries):
            self._adb("shell", "screencap", "-p", "/sdcard/screen.png")
            self._adb("pull", "/sdcard/screen.png", self.screenshot_path)

            if not os.path.exists(self.screenshot_path):
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None, 1.0, 1.0

            try:
                img = Image.open(self.screenshot_path).convert("RGB")
                break
            except Exception:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None, 1.0, 1.0

        orig_w, orig_h = img.size
        if orig_w > 0:
            self.device_w = orig_w
            self.device_h = orig_h

        if max(img.size) > self.max_compress_dim:
            img.thumbnail(
                (self.max_compress_dim, self.max_compress_dim), Image.LANCZOS
            )

        compressed_w, compressed_h = img.size
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        scale_x = orig_w / compressed_w if compressed_w > 0 else 1.0
        scale_y = orig_h / compressed_h if compressed_h > 0 else 1.0
        return b64, scale_x, scale_y

    def get_resolution(self):
        if self.device_w > 0:
            return self.device_w, self.device_h
        out, _ = self._adb("shell", "wm", "size")
        if "size:" in out:
            parts = out.split(":")[-1].strip().split("x")
            return int(parts[0]), int(parts[1])
        return 1080, 1920


class GameActions:
    """ADB input actions with human-like randomization."""

    def __init__(self, device: str = "emulator-5554",
                 tap_delay: float = 0.08,
                 action_delay: float = 0.3):
        self.device = device
        self.tap_delay = tap_delay
        self.action_delay = action_delay
        self.tap_count = 0

    def _adb(self, *args):
        cmd = ["adb", "-s", self.device] + list(args)
        subprocess.run(cmd, capture_output=True, text=True)

    def tap(self, x: int, y: int, label: str = ""):
        """Normal tap with human-like noise (+-3px)."""
        rx = x + random.randint(-3, 3)
        ry = y + random.randint(-3, 3)
        self._adb("shell", "input", "tap", str(rx), str(ry))
        self.tap_count += 1
        time.sleep(self.action_delay)

    def fast_tap(self, x: int, y: int):
        """Ultra-fast tap for rapid sequences."""
        rx = x + random.randint(-2, 2)
        ry = y + random.randint(-2, 2)
        self._adb("shell", "input", "tap", str(rx), str(ry))
        self.tap_count += 1
        time.sleep(self.tap_delay)

    def multi_tap(self, x: int, y: int, count: int, label: str = ""):
        """Tap same position N times rapidly."""
        for _ in range(count):
            self.fast_tap(x, y)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """Swipe gesture with slight randomization."""
        dur = duration + random.randint(-30, 50)
        self._adb("shell", "input", "swipe",
                  str(x1), str(y1), str(x2), str(y2), str(dur))
        time.sleep(self.action_delay)

    def back(self):
        """Press Android back button. WARNING: Many games trigger quit dialogs!"""
        self._adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(self.action_delay)

    def scroll_up(self, x: int = 720, y: int = 1200, distance: int = 530):
        self.swipe(x, y, x, y - distance, 400)

    def scroll_down(self, x: int = 720, y: int = 670, distance: int = 530):
        self.swipe(x, y, x, y + distance, 400)
