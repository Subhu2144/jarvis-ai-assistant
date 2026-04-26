"""Text-to-speech module for Jarvis voice output."""

import queue
import threading

import pyttsx3

from jarvis.config import VoiceConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class VoiceSpeaker:
    """Handles text-to-speech output with queued speech."""

    def __init__(self, config: VoiceConfig) -> None:
        self.config = config
        self._speech_queue: queue.Queue[str | None] = queue.Queue()
        self._speaking = False
        self._thread: threading.Thread | None = None
        self._engine_initialized = False

    def _init_engine(self) -> pyttsx3.Engine:
        """Initialize the TTS engine (must be done in the speaking thread)."""
        engine = pyttsx3.init()
        engine.setProperty("rate", self.config.voice_rate)
        engine.setProperty("volume", self.config.voice_volume)

        voices = engine.getProperty("voices")
        if voices:
            for voice in voices:
                if "english" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break

        self._engine_initialized = True
        return engine

    def _speech_loop(self) -> None:
        """Background thread that processes the speech queue."""
        engine = self._init_engine()

        while self._speaking:
            try:
                text = self._speech_queue.get(timeout=1)
                if text is None:
                    self._speech_queue.task_done()
                    break

                logger.debug(f"Speaking: {text}")
                engine.say(text)
                engine.runAndWait()
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Speech error: {e}")
                self._speech_queue.task_done()

        engine.stop()

    def speak(self, text: str) -> None:
        """Add text to the speech queue."""
        if not text.strip():
            return
        logger.info(f"[bold blue]Jarvis:[/] {text}")
        self._speech_queue.put(text)

    def speak_and_wait(self, text: str) -> None:
        """Speak text and wait until it's done."""
        self.speak(text)
        self._speech_queue.join()

    def start(self) -> None:
        """Start the speech processing thread."""
        if self._speaking:
            return
        self._speaking = True
        self._thread = threading.Thread(target=self._speech_loop, daemon=True)
        self._thread.start()
        logger.info("[green]Voice speaker started.[/]")

    def stop(self) -> None:
        """Stop the speech processor."""
        self._speaking = False
        self._speech_queue.put(None)
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("[yellow]Voice speaker stopped.[/]")

    @property
    def is_speaking(self) -> bool:
        return self._speaking and not self._speech_queue.empty()
