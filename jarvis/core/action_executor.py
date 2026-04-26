"""Action executor - translates LLM planned actions into real desktop operations."""

import time
from typing import Any

from jarvis.config import AppConfig
from jarvis.modules.automation.app_launcher import AppLauncher
from jarvis.modules.automation.desktop import DesktopController
from jarvis.modules.automation.file_manager import FileManager
from jarvis.modules.automation.system_control import SystemController
from jarvis.modules.vision.screen_capture import ScreenCapture
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class ActionExecutor:
    """Executes planned actions from the LLM brain."""

    def __init__(self, config: AppConfig) -> None:
        self.desktop = DesktopController(config.automation)
        self.file_manager = FileManager()
        self.app_launcher = AppLauncher()
        self.system_control = SystemController()
        self.screen_capture = ScreenCapture(config.automation)

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a single action and return the result."""
        action_type = action.get("type", "")
        params = action.get("params", {})

        logger.info(f"Executing action: {action_type}")

        handler = self._get_handler(action_type)
        if handler is None:
            return {"success": False, "error": f"Unknown action type: {action_type}"}

        try:
            result = handler(params)
            logger.debug(f"Action result: {result}")
            return result
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {"success": False, "error": str(e)}

    def execute_chain(self, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute a chain of actions sequentially."""
        results = []
        for i, action in enumerate(actions):
            logger.info(f"Chain step {i + 1}/{len(actions)}: {action.get('type')}")
            result = self.execute(action)
            results.append(result)

            if not result.get("success", False):
                logger.warning(f"Chain step {i + 1} failed: {result.get('error')}")
                # Continue executing unless it's critical
                if action.get("critical", False):
                    break

            # Small delay between actions for stability
            time.sleep(0.3)

        return results

    def _get_handler(self, action_type: str):  # noqa: ANN202
        """Get the handler function for an action type."""
        handlers = {
            "open_app": self._handle_open_app,
            "close_app": self._handle_close_app,
            "type_text": self._handle_type_text,
            "press_key": self._handle_press_key,
            "click": self._handle_click,
            "double_click": self._handle_double_click,
            "right_click": self._handle_right_click,
            "scroll": self._handle_scroll,
            "move_mouse": self._handle_move_mouse,
            "drag": self._handle_drag,
            "screenshot": self._handle_screenshot,
            "create_file": self._handle_create_file,
            "read_file": self._handle_read_file,
            "delete_file": self._handle_delete_file,
            "move_file": self._handle_move_file,
            "copy_file": self._handle_copy_file,
            "list_files": self._handle_list_files,
            "search_files": self._handle_search_files,
            "run_command": self._handle_run_command,
            "open_url": self._handle_open_url,
            "search_web": self._handle_search_web,
            "set_volume": self._handle_set_volume,
            "set_brightness": self._handle_set_brightness,
            "mute": self._handle_mute,
            "system_info": self._handle_system_info,
            "select_all": self._handle_select_all,
            "copy_clipboard": self._handle_copy_clipboard,
            "paste": self._handle_paste,
            "undo": self._handle_undo,
            "save": self._handle_save,
            "lock_screen": self._handle_lock_screen,
            "wait": self._handle_wait,
            "speak": self._handle_speak,
            "chain": self._handle_chain,
        }
        return handlers.get(action_type)

    # --- Action handlers ---

    def _handle_open_app(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.app_launcher.open_app(params.get("app_name", ""))

    def _handle_close_app(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.app_launcher.close_app(params.get("app_name", ""))

    def _handle_type_text(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.type_text(params.get("text", ""))

    def _handle_press_key(self, params: dict[str, Any]) -> dict[str, Any]:
        keys = params.get("keys", [])
        if isinstance(keys, str):
            keys = keys.split("+")
        return self.desktop.press_key(*keys)

    def _handle_click(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.click(
            x=params.get("x", 0),
            y=params.get("y", 0),
            button=params.get("button", "left"),
        )

    def _handle_double_click(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.double_click(x=params.get("x", 0), y=params.get("y", 0))

    def _handle_right_click(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.right_click(x=params.get("x", 0), y=params.get("y", 0))

    def _handle_scroll(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.scroll(
            direction=params.get("direction", "down"),
            amount=params.get("amount", 3),
        )

    def _handle_move_mouse(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.move_mouse(x=params.get("x", 0), y=params.get("y", 0))

    def _handle_drag(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.drag(
            start_x=params.get("start_x", 0),
            start_y=params.get("start_y", 0),
            end_x=params.get("end_x", 0),
            end_y=params.get("end_y", 0),
        )

    def _handle_screenshot(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.screen_capture.save_screenshot(params.get("filename"))

    def _handle_create_file(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.create_file(
            path=params.get("path", ""),
            content=params.get("content", ""),
        )

    def _handle_read_file(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.read_file(params.get("path", ""))

    def _handle_delete_file(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.delete_file(params.get("path", ""))

    def _handle_move_file(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.move_file(
            source=params.get("source", ""),
            destination=params.get("destination", ""),
        )

    def _handle_copy_file(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.copy_file(
            source=params.get("source", ""),
            destination=params.get("destination", ""),
        )

    def _handle_list_files(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.list_files(
            path=params.get("path", "."),
            show_hidden=params.get("show_hidden", False),
        )

    def _handle_search_files(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.file_manager.search_files(
            query=params.get("query", ""),
            path=params.get("path", "~"),
        )

    def _handle_run_command(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.app_launcher.run_command(
            command=params.get("command", ""),
            timeout=params.get("timeout", 30),
        )

    def _handle_open_url(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.app_launcher.open_url(params.get("url", ""))

    def _handle_search_web(self, params: dict[str, Any]) -> dict[str, Any]:
        query = params.get("query", "")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return self.app_launcher.open_url(url)

    def _handle_set_volume(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.system_control.set_volume(params.get("level", 50))

    def _handle_set_brightness(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.system_control.set_brightness(params.get("level", 50))

    def _handle_mute(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.system_control.mute()

    def _handle_system_info(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.system_control.get_system_info()

    def _handle_select_all(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.select_all()

    def _handle_copy_clipboard(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.copy()

    def _handle_paste(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.paste()

    def _handle_undo(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.undo()

    def _handle_save(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.desktop.save()

    def _handle_lock_screen(self, params: dict[str, Any]) -> dict[str, Any]:
        return self.system_control.lock_screen()

    def _handle_wait(self, params: dict[str, Any]) -> dict[str, Any]:
        seconds = params.get("seconds", 1)
        time.sleep(seconds)
        return {"success": True, "action": "wait", "seconds": seconds}

    def _handle_speak(self, params: dict[str, Any]) -> dict[str, Any]:
        # This is handled by the agent, just return the text
        return {"success": True, "action": "speak", "text": params.get("text", "")}

    def _handle_chain(self, params: dict[str, Any]) -> dict[str, Any]:
        actions = params.get("actions", [])
        results = self.execute_chain(actions)
        return {"success": all(r.get("success", False) for r in results), "results": results}
