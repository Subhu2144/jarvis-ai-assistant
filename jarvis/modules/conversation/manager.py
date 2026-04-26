"""Conversation manager - handles dialogue history and context."""

import json
import time
from pathlib import Path
from typing import Any

from jarvis.config import ConversationConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationManager:
    """Manages conversation history, context, and memory."""

    def __init__(self, config: ConversationConfig) -> None:
        self.config = config
        self.history: list[dict[str, str]] = []
        self.last_interaction: float = time.time()
        self.session_data: dict[str, Any] = {}
        self.memory_file = Path.home() / ".jarvis" / "conversation_memory.json"
        self._load_long_term_memory()

    def add_user_message(self, message: str) -> None:
        """Add a user message to the conversation history."""
        self.history.append({"role": "user", "content": message})
        self.last_interaction = time.time()
        self._trim_history()

    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the conversation history."""
        self.history.append({"role": "assistant", "content": message})
        self._trim_history()

    def add_system_context(self, context: str) -> None:
        """Add a system context message (e.g., action results)."""
        self.history.append({"role": "system", "content": context})
        self._trim_history()

    def get_context(self) -> list[dict[str, str]]:
        """Get the conversation context for the LLM."""
        return list(self.history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history.clear()
        logger.info("Conversation history cleared.")

    def is_session_expired(self) -> bool:
        """Check if the conversation session has expired."""
        return (time.time() - self.last_interaction) > self.config.timeout

    def save_to_memory(self, key: str, value: Any) -> None:
        """Save a value to persistent memory."""
        self.session_data[key] = value
        self._save_long_term_memory()

    def recall_from_memory(self, key: str) -> Any:
        """Recall a value from persistent memory."""
        return self.session_data.get(key)

    def get_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.history:
            return "No conversation yet."

        user_messages = [m["content"] for m in self.history if m["role"] == "user"]
        topics = ", ".join(user_messages[-3:])
        return f"Conversation with {len(self.history)} messages. Topics: {topics}"

    def _trim_history(self) -> None:
        """Keep conversation history within the configured limit."""
        if len(self.history) > self.config.max_history:
            # Keep the most recent messages
            self.history = self.history[-self.config.max_history :]

    def _load_long_term_memory(self) -> None:
        """Load persistent memory from disk."""
        try:
            if self.memory_file.exists():
                self.session_data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                logger.debug(f"Loaded {len(self.session_data)} memory items.")
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.session_data = {}

    def _save_long_term_memory(self) -> None:
        """Save persistent memory to disk."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text(
                json.dumps(self.session_data, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def export_conversation(self, filepath: str | None = None) -> str:
        """Export conversation history to a file."""
        if filepath is None:
            filepath = str(
                Path.home()
                / ".jarvis"
                / f"conversation_{int(time.time())}.json"
            )

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(
            json.dumps(self.history, indent=2),
            encoding="utf-8",
        )
        return filepath
