"""System control - volume, brightness, power, and system information."""

import platform
import subprocess
from datetime import datetime
from typing import Any

import psutil

from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class SystemController:
    """Controls system settings and retrieves system information."""

    def __init__(self) -> None:
        self.system = platform.system().lower()

    def set_volume(self, level: int) -> dict[str, Any]:
        """Set system volume (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.system == "linux":
                subprocess.run(
                    ["amixer", "set", "Master", f"{level}%"],
                    capture_output=True,
                )
            elif self.system == "darwin":
                subprocess.run(
                    ["osascript", "-e", f"set volume output volume {level}"],
                    capture_output=True,
                )
            else:
                subprocess.run(
                    [
                        "powershell",
                        "-c",
                        (
                            "$vol = New-Object -ComObject WScript.Shell; "
                            "1..50 | ForEach-Object { $vol.SendKeys([char]174) }; "
                            f"1..{level // 2} | ForEach-Object {{ $vol.SendKeys([char]175) }}"
                        ),
                    ],
                    capture_output=True,
                )

            logger.info(f"Volume set to {level}%")
            return {"success": True, "action": "set_volume", "level": level}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_brightness(self, level: int) -> dict[str, Any]:
        """Set screen brightness (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.system == "linux":
                subprocess.run(
                    ["xrandr", "--output", "eDP-1", "--brightness", str(level / 100)],
                    capture_output=True,
                )
            elif self.system == "darwin":
                brightness_val = level / 100
                cmd = (
                    'tell application "System Events" to set value of'
                    " slider 1 of group 1 of window 1 of application"
                    f' process "SystemUIServer" to {brightness_val}'
                )
                subprocess.run(
                    ["osascript", "-e", cmd],
                    capture_output=True,
                )

            logger.info(f"Brightness set to {level}%")
            return {"success": True, "action": "set_brightness", "level": level}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mute(self) -> dict[str, Any]:
        """Toggle mute."""
        try:
            if self.system == "linux":
                subprocess.run(["amixer", "set", "Master", "toggle"], capture_output=True)
            elif self.system == "darwin":
                subprocess.run(
                    ["osascript", "-e", "set volume with output muted"],
                    capture_output=True,
                )
            return {"success": True, "action": "mute"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_system_info(self) -> dict[str, Any]:
        """Get comprehensive system information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()

            info = {
                "success": True,
                "system": {
                    "os": platform.system(),
                    "os_version": platform.version(),
                    "hostname": platform.node(),
                    "architecture": platform.machine(),
                    "python_version": platform.python_version(),
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "physical_cores": psutil.cpu_count(logical=False),
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent,
                },
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if battery:
                info["battery"] = {
                    "percent": battery.percent,
                    "charging": battery.power_plugged,
                    "time_left": str(battery.secsleft) if battery.secsleft > 0 else "calculating",
                }

            return info
        except Exception as e:
            return {"success": False, "error": str(e)}

    def shutdown(self, mode: str = "shutdown") -> dict[str, Any]:
        """Shutdown, restart, or sleep the system."""
        try:
            if mode == "shutdown":
                if self.system == "linux":
                    subprocess.run(["systemctl", "poweroff"])
                elif self.system == "darwin":
                    subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
                else:
                    subprocess.run(["shutdown", "/s", "/t", "0"])
            elif mode == "restart":
                if self.system == "linux":
                    subprocess.run(["systemctl", "reboot"])
                elif self.system == "darwin":
                    subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'])
                else:
                    subprocess.run(["shutdown", "/r", "/t", "0"])
            elif mode == "sleep":
                if self.system == "linux":
                    subprocess.run(["systemctl", "suspend"])
                elif self.system == "darwin":
                    subprocess.run(["pmset", "sleepnow"])

            return {"success": True, "action": mode}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def lock_screen(self) -> dict[str, Any]:
        """Lock the screen."""
        try:
            if self.system == "linux":
                subprocess.run(["xdg-screensaver", "lock"])
            elif self.system == "darwin":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events"'
                        ' to keystroke "q" using'
                        " {command down, control down}",
                    ]
                )
            else:
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return {"success": True, "action": "lock_screen"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_wifi_info(self) -> dict[str, Any]:
        """Get current WiFi connection info."""
        try:
            if self.system == "linux":
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                    capture_output=True,
                    text=True,
                )
                for line in result.stdout.strip().split("\n"):
                    if line.startswith("yes:"):
                        return {"success": True, "ssid": line.split(":")[1]}
            elif self.system == "darwin":
                result = subprocess.run(
                    [
                        "/System/Library/PrivateFrameworks"
                        "/Apple80211.framework/Versions"
                        "/Current/Resources/airport",
                        "-I",
                    ],
                    capture_output=True,
                    text=True,
                )
                for line in result.stdout.split("\n"):
                    if "SSID" in line and "BSSID" not in line:
                        return {"success": True, "ssid": line.split(":")[1].strip()}
            return {"success": True, "ssid": "Unknown"}
        except Exception as e:
            return {"success": False, "error": str(e)}
