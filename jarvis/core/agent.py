"""Main Jarvis Agent - orchestrates all modules together."""

import signal
import sys
import time
from typing import Any

from jarvis.config import AppConfig
from jarvis.core.action_executor import ActionExecutor
from jarvis.core.brain import Brain
from jarvis.modules.conversation.manager import ConversationManager
from jarvis.modules.vision.screen_capture import ScreenCapture
from jarvis.modules.voice.listener import VoiceListener
from jarvis.modules.voice.speaker import VoiceSpeaker
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class JarvisAgent:
    """The main Jarvis AI Agent that ties all modules together."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.brain = Brain(config.llm)
        self.executor = ActionExecutor(config)
        self.listener = VoiceListener(config.voice)
        self.speaker = VoiceSpeaker(config.voice)
        self.conversation = ConversationManager(config.conversation)
        self.screen = ScreenCapture(config.automation)
        self._running = False
        self._processing = False

    def start(self) -> None:
        """Start the Jarvis agent with all modules."""
        logger.info("[bold green]Starting Jarvis AI Assistant...[/]")

        # Validate configuration
        issues = self.config.validate()
        if issues:
            for issue in issues:
                logger.warning(f"[yellow]Config issue: {issue}[/]")

        # Set up graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start modules
        self.speaker.start()
        self.speaker.speak("Jarvis is online and ready to help.")

        self.listener.on_command(self._handle_command)
        self.listener.calibrate()
        self.listener.start()

        self._running = True
        logger.info("[bold green]Jarvis is ready! Say the wake word to begin.[/]")

        # Main loop
        self._main_loop()

    def _main_loop(self) -> None:
        """Main event loop."""
        try:
            while self._running:
                # Check for session timeout
                if self.conversation.is_session_expired():
                    if self.conversation.history:
                        logger.info("[yellow]Conversation session expired. History cleared.[/]")
                        self.conversation.clear_history()

                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()

    def _handle_command(self, command: str) -> None:
        """Handle a voice command from the listener."""
        if self._processing:
            logger.info("[yellow]Still processing previous command...[/]")
            return

        self._processing = True

        try:
            # Check for built-in commands
            if self._handle_builtin_command(command):
                return

            # Add user message to conversation
            self.conversation.add_user_message(command)

            # Check if user wants screen context
            use_vision = any(
                word in command
                for word in ["screen", "see", "look", "showing", "what's on", "read this"]
            )

            if use_vision:
                result = self._process_with_vision(command)
            else:
                result = self._process_command(command)

            # Speak the response
            if result.get("response"):
                self.speaker.speak(result["response"])
                self.conversation.add_assistant_message(result["response"])

            # Execute planned actions
            actions = result.get("actions", [])
            if actions:
                self._execute_actions(actions)

        except Exception as e:
            logger.error(f"Command handling error: {e}")
            self.speaker.speak("I encountered an error. Please try again.")
        finally:
            self._processing = False

    def _handle_builtin_command(self, command: str) -> bool:
        """Handle built-in commands that don't need LLM processing."""
        command_lower = command.lower().strip()

        if command_lower in ("stop", "quit", "exit", "goodbye", "bye"):
            self.speaker.speak_and_wait("Goodbye! Shutting down.")
            self.stop()
            return True

        if command_lower in ("stop listening", "pause"):
            self.speaker.speak("Pausing voice recognition.")
            self.listener.stop()
            return True

        if command_lower in ("continuous mode", "always listen"):
            self.listener.set_continuous_mode(True)
            self.speaker.speak("Continuous listening mode enabled. No wake word needed.")
            return True

        if command_lower in ("wake word mode", "normal mode"):
            self.listener.set_continuous_mode(False)
            self.speaker.speak("Wake word mode enabled.")
            return True

        if command_lower in ("clear history", "forget everything"):
            self.conversation.clear_history()
            self.speaker.speak("Conversation history cleared.")
            return True

        if command_lower in ("what can you do", "help"):
            self._speak_capabilities()
            return True

        return False

    def _process_command(self, command: str) -> dict[str, Any]:
        """Process a command through the LLM brain."""
        context = self.conversation.get_context()
        return self.brain.think(command, context)

    def _process_with_vision(self, command: str) -> dict[str, Any]:
        """Process a command with screen capture context."""
        self.speaker.speak("Let me take a look at your screen...")
        capture = self.screen.capture_for_analysis()

        if not capture.get("success"):
            return {
                "response": "I couldn't capture your screen. Let me try without it.",
                "actions": [],
            }

        context = self.conversation.get_context()
        return self.brain.analyze_screen(capture["base64"], command, context)

    def _execute_actions(self, actions: list[dict[str, Any]]) -> None:
        """Execute a list of planned actions."""
        for i, action in enumerate(actions):
            action_type = action.get("type", "")

            # Handle speak actions separately
            if action_type == "speak":
                text = action.get("params", {}).get("text", "")
                if text:
                    self.speaker.speak(text)
                continue

            # Execute the action
            result = self.executor.execute(action)

            # Report result to conversation context
            status = "succeeded" if result.get("success") else "failed"
            result_summary = f"Action '{action_type}': {status}"
            if not result.get("success"):
                result_summary += f" - {result.get('error', 'unknown error')}"
            self.conversation.add_system_context(result_summary)

            logger.info(f"Step {i + 1}: {result_summary}")

    def _speak_capabilities(self) -> None:
        """List Jarvis capabilities."""
        self.speaker.speak(
            "I can help you with many things. "
            "I can open and close applications, type text, control your mouse, "
            "manage files, browse the web, adjust system settings like volume and brightness, "
            "take screenshots, run terminal commands, and much more. "
            "Just tell me what you need in natural language!"
        )

    def process_text_command(self, command: str) -> dict[str, Any]:
        """Process a text command (for non-voice input). Returns the result."""
        self.conversation.add_user_message(command)
        result = self._process_command(command)

        if result.get("response"):
            self.conversation.add_assistant_message(result["response"])

        actions = result.get("actions", [])
        if actions:
            self._execute_actions(actions)

        return result

    def stop(self) -> None:
        """Stop the Jarvis agent."""
        logger.info("[yellow]Shutting down Jarvis...[/]")
        self._running = False
        self.listener.stop()
        self.speaker.stop()
        self.conversation._save_long_term_memory()
        logger.info("[red]Jarvis has been shut down.[/]")

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down...")
        self.stop()
        sys.exit(0)
