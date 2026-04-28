"""Application launcher - open, close, and manage applications."""

import platform
import subprocess
from typing import Any

import psutil

from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

# Common app names mapped to their commands on different platforms
APP_REGISTRY: dict[str, dict[str, str]] = {
    "browser": {
        "linux": "xdg-open http://",
        "darwin": "open -a Safari",
        "windows": "start msedge",
    },
    "chrome": {
        "linux": "google-chrome",
        "darwin": "open -a 'Google Chrome'",
        "windows": "start chrome",
    },
    "firefox": {
        "linux": "firefox",
        "darwin": "open -a Firefox",
        "windows": "start firefox",
    },
    "terminal": {
        "linux": "x-terminal-emulator",
        "darwin": "open -a Terminal",
        "windows": "start cmd",
    },
    "file manager": {
        "linux": "nautilus",
        "darwin": "open ~",
        "windows": "explorer",
    },
    "text editor": {
        "linux": "gedit",
        "darwin": "open -a TextEdit",
        "windows": "notepad",
    },
    "vscode": {
        "linux": "code",
        "darwin": "open -a 'Visual Studio Code'",
        "windows": "code",
    },
    "calculator": {
        "linux": "gnome-calculator",
        "darwin": "open -a Calculator",
        "windows": "calc",
    },
    "settings": {
        "linux": "gnome-control-center",
        "darwin": "open -a 'System Preferences'",
        "windows": "start ms-settings:",
    },
    "music": {
        "linux": "rhythmbox",
        "darwin": "open -a Music",
        "windows": "start mswindowsmusic:",
    },
    "video player": {
        "linux": "vlc",
        "darwin": "open -a 'QuickTime Player'",
        "windows": "start wmplayer",
    },
}


class AppLauncher:
    """Manages launching and closing applications."""

    def __init__(self) -> None:
        self.system = platform.system().lower()

    def _get_platform_key(self) -> str:
        """Get the platform key for app registry."""
        if self.system == "linux":
            return "linux"
        elif self.system == "darwin":
            return "darwin"
        return "windows"

    def open_app(self, app_name: str) -> dict[str, Any]:
        """Open an application by name."""
        app_key = app_name.lower().strip()
        platform_key = self._get_platform_key()

        if app_key in APP_REGISTRY and platform_key in APP_REGISTRY[app_key]:
            command = APP_REGISTRY[app_key][platform_key]
        else:
            command = app_key

        try:
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Opened application: {app_name}")
            return {"success": True, "action": "open_app", "app": app_name}
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return {"success": False, "error": str(e)}

    def close_app(self, app_name: str) -> dict[str, Any]:
        """Close an application by name."""
        app_key = app_name.lower().strip()
        closed = False

        for proc in psutil.process_iter(["name", "pid"]):
            try:
                proc_name = (proc.info["name"] or "").lower()
                if app_key in proc_name:
                    proc.terminate()
                    closed = True
                    logger.info(
                        f"Terminated: {proc_name} (PID: {proc.info['pid']})"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed:
            return {"success": True, "action": "close_app", "app": app_name}
        return {
            "success": False,
            "error": f"No running process found for: {app_name}",
        }

    def list_running_apps(self) -> dict[str, Any]:
        """List all running applications."""
        apps = set()
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name:
                    apps.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {"success": True, "apps": sorted(apps)}

    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is running."""
        app_key = app_name.lower()
        for proc in psutil.process_iter(["name"]):
            try:
                proc_name = (proc.info["name"] or "").lower()
                if app_key in proc_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def open_url(self, url: str) -> dict[str, Any]:
        """Open a URL in the default browser."""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            if self.system == "linux":
                subprocess.Popen(
                    ["xdg-open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif self.system == "darwin":
                subprocess.Popen(
                    ["open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    ["start", url],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return {"success": True, "action": "open_url", "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_command(self, command: str, timeout: int = 30) -> dict[str, Any]:
        """Run a terminal command and return output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
