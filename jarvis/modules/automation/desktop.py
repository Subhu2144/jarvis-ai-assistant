"""Desktop automation - mouse, keyboard, and screen control."""

from typing import Any

import pyautogui
import pyperclip

from jarvis.config import AutomationConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class DesktopController:
    """Controls mouse, keyboard, and desktop interactions."""

    def __init__(self, config: AutomationConfig) -> None:
        self.config = config
        pyautogui.FAILSAFE = config.failsafe
        pyautogui.PAUSE = 0.1

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
        """Click at a position on screen."""
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            logger.info(f"Clicked at ({x}, {y}) with {button} button")
            return {"success": True, "action": "click", "position": (x, y)}
        except Exception as e:
            logger.error(f"Click error: {e}")
            return {"success": False, "error": str(e)}

    def double_click(self, x: int, y: int) -> dict[str, Any]:
        """Double-click at a position."""
        return self.click(x, y, clicks=2)

    def right_click(self, x: int, y: int) -> dict[str, Any]:
        """Right-click at a position."""
        return self.click(x, y, button="right")

    def move_mouse(self, x: int, y: int) -> dict[str, Any]:
        """Move mouse to a position."""
        try:
            pyautogui.moveTo(x, y, duration=self.config.mouse_move_duration)
            return {"success": True, "action": "move_mouse", "position": (x, y)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def type_text(self, text: str, interval: float | None = None) -> dict[str, Any]:
        """Type text using the keyboard."""
        try:
            interval = interval or self.config.typing_interval
            pyautogui.typewrite(text, interval=interval)
            logger.info(f"Typed: {text[:50]}...")
            return {"success": True, "action": "type_text", "text": text[:50]}
        except Exception:
            # Fallback: use clipboard for non-ASCII text
            try:
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                return {
                    "success": True,
                    "action": "type_text",
                    "text": text[:50],
                    "method": "clipboard",
                }
            except Exception as e2:
                return {"success": False, "error": str(e2)}

    def press_key(self, *keys: str) -> dict[str, Any]:
        """Press a key or key combination."""
        try:
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            logger.info(f"Pressed: {'+'.join(keys)}")
            return {"success": True, "action": "press_key", "keys": list(keys)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scroll(self, direction: str = "down", amount: int = 3) -> dict[str, Any]:
        """Scroll up or down."""
        try:
            scroll_amount = amount if direction == "up" else -amount
            pyautogui.scroll(scroll_amount)
            return {"success": True, "action": "scroll", "direction": direction}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> dict[str, Any]:
        """Drag from one position to another."""
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(
                end_x - start_x,
                end_y - start_y,
                duration=self.config.mouse_move_duration,
            )
            return {"success": True, "action": "drag"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_screen_size(self) -> tuple[int, int]:
        """Get screen resolution."""
        return pyautogui.size()

    def get_mouse_position(self) -> tuple[int, int]:
        """Get current mouse position."""
        return pyautogui.position()

    def select_all(self) -> dict[str, Any]:
        """Select all text (Ctrl+A)."""
        return self.press_key("ctrl", "a")

    def copy(self) -> dict[str, Any]:
        """Copy selection (Ctrl+C)."""
        return self.press_key("ctrl", "c")

    def paste(self) -> dict[str, Any]:
        """Paste from clipboard (Ctrl+V)."""
        return self.press_key("ctrl", "v")

    def undo(self) -> dict[str, Any]:
        """Undo (Ctrl+Z)."""
        return self.press_key("ctrl", "z")

    def save(self) -> dict[str, Any]:
        """Save (Ctrl+S)."""
        return self.press_key("ctrl", "s")

    def get_clipboard_text(self) -> str:
        """Get text from clipboard."""
        return pyperclip.paste()
