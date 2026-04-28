"""Configuration management for Jarvis AI Assistant."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class VoiceConfig:
    """Voice recognition and TTS settings."""

    wake_word: str = os.getenv("WAKE_WORD", "jarvis")
    voice_rate: int = int(os.getenv("VOICE_RATE", "175"))
    voice_volume: float = float(os.getenv("VOICE_VOLUME", "0.9"))
    language: str = os.getenv("LANGUAGE", "en")
    listen_timeout: int = 5
    phrase_time_limit: int = 15
    energy_threshold: int = 300
    pause_threshold: float = 1.0


@dataclass
class LLMConfig:
    """LLM settings."""

    api_key: str = os.getenv("GROQ_API_KEY", "")
    base_url: str = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    vision_model: str = os.getenv("LLM_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")


@dataclass
class AutomationConfig:
    """Desktop automation settings."""

    mouse_move_duration: float = float(os.getenv("MOUSE_MOVE_DURATION", "0.3"))
    typing_interval: float = float(os.getenv("TYPING_INTERVAL", "0.02"))
    screenshot_quality: int = int(os.getenv("SCREENSHOT_QUALITY", "85"))
    failsafe: bool = True


@dataclass
class ConversationConfig:
    """Conversation management settings."""

    max_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    timeout: int = int(os.getenv("CONVERSATION_TIMEOUT", "300"))


@dataclass
class AppConfig:
    """Main application configuration."""

    voice: VoiceConfig = field(default_factory=VoiceConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "jarvis.log")
    data_dir: Path = Path.home() / ".jarvis"

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """Validate configuration and return list of issues."""
        issues = []
        if not self.llm.api_key:
            issues.append("GROQ_API_KEY is not set. Set it in .env or environment.")
        return issues
