"""Desktop automation modules."""

from jarvis.modules.automation.app_launcher import AppLauncher
from jarvis.modules.automation.desktop import DesktopController
from jarvis.modules.automation.file_manager import FileManager
from jarvis.modules.automation.system_control import SystemController

__all__ = ["DesktopController", "FileManager", "AppLauncher", "SystemController"]
