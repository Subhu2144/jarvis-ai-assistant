"""Screen capture and vision analysis module."""

import base64
import io
from pathlib import Path
from typing import Any

import pyautogui
from PIL import Image

from jarvis.config import AutomationConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class ScreenCapture:
    """Captures and processes screenshots for vision analysis."""

    def __init__(self, config: AutomationConfig) -> None:
        self.config = config
        self.screenshot_dir = Path.home() / ".jarvis" / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(self, region: tuple[int, int, int, int] | None = None) -> Image.Image:
        """Take a screenshot, optionally of a specific region."""
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        return screenshot

    def screenshot_to_base64(
        self, screenshot: Image.Image | None = None, quality: int | None = None
    ) -> str:
        """Convert a screenshot to base64 string for LLM vision analysis."""
        if screenshot is None:
            screenshot = self.take_screenshot()

        quality = quality or self.config.screenshot_quality

        # Resize for faster processing while maintaining readability
        max_dimension = 1920
        if max(screenshot.size) > max_dimension:
            ratio = max_dimension / max(screenshot.size)
            new_size = (int(screenshot.width * ratio), int(screenshot.height * ratio))
            screenshot = screenshot.resize(new_size, Image.LANCZOS)

        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def save_screenshot(self, filename: str | None = None) -> dict[str, Any]:
        """Take and save a screenshot to disk."""
        try:
            screenshot = self.take_screenshot()
            if filename is None:
                from datetime import datetime

                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            filepath = self.screenshot_dir / filename
            screenshot.save(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return {"success": True, "path": str(filepath)}
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return {"success": False, "error": str(e)}

    def capture_for_analysis(self) -> dict[str, Any]:
        """Take a screenshot and return it ready for LLM analysis."""
        try:
            screenshot = self.take_screenshot()
            base64_image = self.screenshot_to_base64(screenshot)
            return {
                "success": True,
                "base64": base64_image,
                "size": screenshot.size,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> dict[str, Any]:
        """Find an image on screen (useful for finding UI elements)."""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return {
                    "success": True,
                    "found": True,
                    "location": {
                        "x": center.x,
                        "y": center.y,
                        "left": location.left,
                        "top": location.top,
                        "width": location.width,
                        "height": location.height,
                    },
                }
            return {"success": True, "found": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
