"""Voice listener module - continuous microphone listening with wake word detection."""

import threading
import time
from collections.abc import Callable

import speech_recognition as sr

from jarvis.config import VoiceConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class VoiceListener:
    """Continuously listens for voice input with wake word detection."""

    def __init__(self, config: VoiceConfig) -> None:
        self.config = config
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.energy_threshold
        self.recognizer.pause_threshold = config.pause_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = sr.Microphone()
        self._listening = False
        self._wake_word_active = True
        self._on_command: Callable[[str], None] | None = None
        self._thread: threading.Thread | None = None

    def calibrate(self) -> None:
        """Calibrate microphone for ambient noise."""
        logger.info("[bold cyan]Calibrating microphone...[/]")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info(
            f"[green]Calibration complete. Energy threshold: "
            f"{self.recognizer.energy_threshold:.0f}[/]"
        )

    def on_command(self, callback: Callable[[str], None]) -> None:
        """Register a callback for when a voice command is recognized."""
        self._on_command = callback

    def _recognize_speech(self, audio: sr.AudioData) -> str | None:
        """Convert audio to text using Google Speech Recognition."""
        try:
            text = self.recognizer.recognize_google(audio, language=self.config.language)
            return str(text).lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None

    def _listen_loop(self) -> None:
        """Main listening loop running in a background thread."""
        logger.info("[bold green]Voice listener started. Say the wake word to begin.[/]")

        while self._listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.config.listen_timeout,
                        phrase_time_limit=self.config.phrase_time_limit,
                    )

                text = self._recognize_speech(audio)
                if text is None:
                    continue

                logger.debug(f"Heard: {text}")

                if self._wake_word_active:
                    if self.config.wake_word in text:
                        command = text.replace(self.config.wake_word, "").strip()
                        if command:
                            self._process_command(command)
                        else:
                            logger.info("[cyan]Wake word detected. Listening for command...[/]")
                            self._listen_for_followup()
                else:
                    self._process_command(text)

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                logger.error(f"Listener error: {e}")
                time.sleep(1)

    def _listen_for_followup(self) -> None:
        """Listen for a follow-up command after wake word detection."""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.listen_timeout,
                    phrase_time_limit=self.config.phrase_time_limit,
                )
            text = self._recognize_speech(audio)
            if text:
                self._process_command(text)
        except sr.WaitTimeoutError:
            logger.info("[yellow]No follow-up command heard.[/]")

    def _process_command(self, command: str) -> None:
        """Process a recognized command."""
        logger.info(f"[bold magenta]Command: {command}[/]")
        if self._on_command:
            self._on_command(command)

    def start(self) -> None:
        """Start listening in a background thread."""
        if self._listening:
            return
        self._listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the listener."""
        self._listening = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("[yellow]Voice listener stopped.[/]")

    def set_continuous_mode(self, enabled: bool) -> None:
        """Toggle continuous listening (no wake word needed)."""
        self._wake_word_active = not enabled
        mode = "continuous" if enabled else "wake word"
        logger.info(f"[cyan]Listening mode: {mode}[/]")

    @property
    def is_listening(self) -> bool:
        return self._listening
