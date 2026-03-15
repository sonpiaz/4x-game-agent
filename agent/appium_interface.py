"""
iOS Device Interface via Appium — Screenshot capture + input actions.

Works with iOS simulators or physical devices connected via Appium.
Coordinates are in device pixel space. The caller is responsible
for mapping game UI coordinates to device coordinates.
"""
import base64
import io
import logging
import time
from typing import Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)

# Optional import for Appium - allows module to be imported without Appium installed
try:
    from appium import webdriver
    from appium.options.ios import XCUITestOptions
    from appium.webdriver.common.appiumby import AppiumBy
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False
    logger.warning("appium-python-client not installed. iOS features unavailable.")


class GameScreen:
    """iOS screenshot capture with LLM API compression via Appium."""

    def __init__(
        self,
        appium_url: str = "http://localhost:4723",
        udid: Optional[str] = None,
        bundle_id: Optional[str] = None,
        max_compress_dim: int = 1280,
        platform_version: Optional[str] = None,
        device_name: Optional[str] = None,
    ):
        """
        Initialize iOS GameScreen interface.

        Args:
            appium_url: Appium server URL (default: http://localhost:4723)
            udid: iOS device UDID (for physical devices) or simulator ID
            bundle_id: Target app bundle ID (e.g., com.example.game)
            max_compress_dim: Maximum dimension for compressed screenshots
            platform_version: iOS version (e.g., "17.0")
            device_name: Device name for simulator selection
        """
        if not APPIUM_AVAILABLE:
            raise ImportError(
                "appium-python-client is required for iOS support. "
                "Install with: pip install appium-python-client"
            )

        self.appium_url = appium_url
        self.udid = udid
        self.bundle_id = bundle_id
        self.max_compress_dim = max_compress_dim
        self.platform_version = platform_version
        self.device_name = device_name

        self.driver: Optional[webdriver.Remote] = None
        self.device_w = 0
        self.device_h = 0

    def _build_capabilities(self) -> dict:
        """Build XCUITest capabilities for iOS."""
        options = XCUITestOptions()

        if self.udid:
            options.set_capability("appium:udid", self.udid)

        if self.bundle_id:
            options.set_capability("appium:bundleId", self.bundle_id)
        else:
            # Launch without app - for system-level automation
            options.set_capability("appium:bundleId", "com.apple.springboard")

        if self.platform_version:
            options.set_capability("appium:platformVersion", self.platform_version)

        if self.device_name:
            options.set_capability("appium:deviceName", self.device_name)

        # Common settings for game automation
        options.set_capability("platformName", "iOS")
        options.set_capability("automationName", "XCUITest")
        options.set_capability("appium:noReset", True)
        options.set_capability("appium:fullContextList", True)
        options.set_capability("appium:screenshotQuality", 2)  # High quality

        return options.to_capabilities()

    def connect(self) -> bool:
        """
        Connect to iOS device via Appium.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            capabilities = self._build_capabilities()
            self.driver = webdriver.Remote(self.appium_url, capabilities)

            # Detect device resolution
            self._detect_resolution()

            logger.info(f"Connected to iOS device: {self.udid or 'simulator'}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to iOS device: {e}")
            self.driver = None
            return False

    def _detect_resolution(self):
        """Detect actual device resolution."""
        if self.driver:
            window_size = self.driver.get_window_size()
            self.device_w = window_size.get("width", 0)
            self.device_h = window_size.get("height", 0)
            logger.debug(f"Detected resolution: {self.device_w}x{self.device_h}")

    def is_connected(self) -> bool:
        """
        Check if device is still connected.

        Returns:
            True if connected and session is active
        """
        if self.driver is None:
            return False

        try:
            # Ping the session by checking session_id
            _ = self.driver.session_id
            return True
        except Exception:
            self.driver = None
            return False

    def screenshot(self, retries: int = 3) -> Tuple[Optional[str], float, float]:
        """
        Take screenshot, return (base64, scale_x, scale_y).

        The base64 image is compressed for LLM APIs.
        Scale factors convert LLM coordinates back to device coordinates:
            device_x = llm_x * scale_x

        Args:
            retries: Number of retry attempts

        Returns:
            Tuple of (base64_string, scale_x, scale_y) or (None, 1.0, 1.0) on failure
        """
        if not self.driver:
            logger.error("Not connected to iOS device")
            return None, 1.0, 1.0

        for attempt in range(retries):
            try:
                # Take screenshot as PNG bytes
                png_bytes = self.driver.get_screenshot_as_png()

                if not png_bytes:
                    if attempt < retries - 1:
                        time.sleep(0.5)
                        continue
                    return None, 1.0, 1.0

                # Load image with PIL
                img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
                break

            except Exception as e:
                logger.warning(f"Screenshot attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None, 1.0, 1.0

        orig_w, orig_h = img.size
        if orig_w > 0:
            self.device_w = orig_w
            self.device_h = orig_h

        # Compress if needed
        if max(img.size) > self.max_compress_dim:
            img.thumbnail(
                (self.max_compress_dim, self.max_compress_dim), Image.LANCZOS
            )

        compressed_w, compressed_h = img.size

        # Convert to JPEG and base64
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Calculate scale factors
        scale_x = orig_w / compressed_w if compressed_w > 0 else 1.0
        scale_y = orig_h / compressed_h if compressed_h > 0 else 1.0

        return b64, scale_x, scale_y

    def get_resolution(self) -> Tuple[int, int]:
        """
        Get device resolution.

        Returns:
            Tuple of (width, height)
        """
        if self.device_w > 0 and self.device_h > 0:
            return self.device_w, self.device_h

        if self.driver:
            try:
                window_size = self.driver.get_window_size()
                self.device_w = window_size.get("width", 0)
                self.device_h = window_size.get("height", 0)
                return self.device_w, self.device_h
            except Exception as e:
                logger.warning(f"Failed to get resolution: {e}")

        # Default fallback
        return 1170, 2532  # iPhone 14 Pro default

    def tap(self, x: int, y: int) -> bool:
        """
        Tap at screen coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if tap was successful
        """
        if not self.driver:
            logger.error("Not connected to iOS device")
            return False

        try:
            # Use W3C actions for tap
            actions = self.driver.w3c_actions
            actions.pointer_action.move_to_location(x, y)
            actions.pointer_action.click()
            actions.perform()
            return True
        except Exception as e:
            logger.error(f"Tap failed at ({x}, {y}): {e}")
            return False

    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: int = 300
    ) -> bool:
        """
        Swipe from one point to another.

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Swipe duration in milliseconds

        Returns:
            True if swipe was successful
        """
        if not self.driver:
            logger.error("Not connected to iOS device")
            return False

        try:
            self.driver.swipe(x1, y1, x2, y2, duration)
            return True
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            return False

    def press_home(self) -> bool:
        """
        Press home button (iOS: go to home screen).

        Returns:
            True if successful
        """
        if not self.driver:
            logger.error("Not connected to iOS device")
            return False

        try:
            # Simulate home button press
            self.driver.execute_script("mobile: pressButton", {"name": "home"})
            return True
        except Exception as e:
            logger.error(f"Home button press failed: {e}")
            return False

    def press_back(self) -> bool:
        """
        Press back button (iOS: swipe from left edge).

        Note: iOS doesn't have a hardware back button.
        This performs a swipe from the left edge as a back gesture.

        Returns:
            True if successful
        """
        if not self.driver:
            logger.error("Not connected to iOS device")
            return False

        try:
            # Swipe from left edge as back gesture
            width, height = self.get_resolution()
            self.swipe(10, height // 2, width // 3, height // 2, duration=200)
            return True
        except Exception as e:
            logger.error(f"Back gesture failed: {e}")
            return False

    def quit(self):
        """Close the Appium session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error quitting session: {e}")
            finally:
                self.driver = None
