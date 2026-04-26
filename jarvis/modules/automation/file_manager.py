"""File management module - create, read, move, delete, search files."""

import shutil
from pathlib import Path
from typing import Any

from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileManager:
    """Handles file system operations."""

    def create_file(self, path: str, content: str = "") -> dict[str, Any]:
        """Create a new file with optional content."""
        try:
            file_path = Path(path).expanduser()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Created file: {file_path}")
            return {"success": True, "action": "create_file", "path": str(file_path)}
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return {"success": False, "error": str(e)}

    def read_file(self, path: str) -> dict[str, Any]:
        """Read contents of a file."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            content = file_path.read_text(encoding="utf-8")
            return {"success": True, "content": content, "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, path: str) -> dict[str, Any]:
        """Delete a file or directory."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                return {"success": False, "error": f"Not found: {path}"}
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
            logger.info(f"Deleted: {file_path}")
            return {"success": True, "action": "delete", "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_file(self, source: str, destination: str) -> dict[str, Any]:
        """Move or rename a file."""
        try:
            src = Path(source).expanduser()
            dst = Path(destination).expanduser()
            if not src.exists():
                return {"success": False, "error": f"Source not found: {source}"}
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            logger.info(f"Moved: {src} -> {dst}")
            return {"success": True, "source": str(src), "destination": str(dst)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_file(self, source: str, destination: str) -> dict[str, Any]:
        """Copy a file or directory."""
        try:
            src = Path(source).expanduser()
            dst = Path(destination).expanduser()
            if not src.exists():
                return {"success": False, "error": f"Source not found: {source}"}
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(str(src), str(dst))
            else:
                shutil.copy2(str(src), str(dst))
            return {"success": True, "source": str(src), "destination": str(dst)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, path: str = ".", show_hidden: bool = False) -> dict[str, Any]:
        """List files in a directory."""
        try:
            dir_path = Path(path).expanduser()
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {path}"}

            items = []
            for item in sorted(dir_path.iterdir()):
                if not show_hidden and item.name.startswith("."):
                    continue
                items.append(
                    {
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0,
                    }
                )
            return {"success": True, "path": str(dir_path), "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, query: str, path: str = "~", max_results: int = 20) -> dict[str, Any]:
        """Search for files matching a pattern."""
        try:
            search_path = Path(path).expanduser()
            results = []
            for item in search_path.rglob(f"*{query}*"):
                if len(results) >= max_results:
                    break
                results.append(
                    {
                        "path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0,
                    }
                )
            return {"success": True, "query": query, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_info(self, path: str) -> dict[str, Any]:
        """Get detailed information about a file."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                return {"success": False, "error": f"Not found: {path}"}
            stat = file_path.stat()
            return {
                "success": True,
                "path": str(file_path),
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": file_path.suffix,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
