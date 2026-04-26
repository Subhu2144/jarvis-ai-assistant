"""Jarvis AI Assistant - Main entry point."""

import argparse

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from jarvis.config import AppConfig
from jarvis.core.agent import JarvisAgent

console = Console()


BANNER = """
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    Voice-Controlled AI Desktop Assistant
"""


def print_banner() -> None:
    """Display the Jarvis startup banner."""
    console.print(Panel(Text(BANNER, style="bold cyan"), border_style="bright_blue"))


def run_voice_mode(config: AppConfig) -> None:
    """Run Jarvis in voice-controlled mode."""
    agent = JarvisAgent(config)
    agent.start()


def run_text_mode(config: AppConfig) -> None:
    """Run Jarvis in text input mode (for testing or when no microphone)."""
    agent = JarvisAgent(config)

    # Start only the speaker (no listener needed)
    agent.speaker.start()
    agent.speaker.speak("Jarvis is running in text mode. Type your commands.")

    console.print("[bold green]Jarvis Text Mode[/] - Type commands below. Type 'quit' to exit.\n")

    try:
        while True:
            try:
                user_input = console.input("[bold cyan]You:[/] ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye"):
                agent.speaker.speak_and_wait("Goodbye!")
                break

            result = agent.process_text_command(user_input)

            if result.get("response"):
                console.print(f"[bold blue]Jarvis:[/] {result['response']}\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/]")
    finally:
        agent.stop()


def main() -> None:
    """Main entry point for Jarvis AI Assistant."""
    parser = argparse.ArgumentParser(
        description="Jarvis AI Assistant - Voice-controlled desktop automation"
    )
    parser.add_argument(
        "--mode",
        choices=["voice", "text"],
        default="voice",
        help="Input mode: 'voice' for microphone, 'text' for keyboard (default: voice)",
    )
    parser.add_argument(
        "--wake-word",
        default=None,
        help="Custom wake word (default: jarvis)",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Enable continuous listening (no wake word needed)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use (default: gpt-4o)",
    )

    args = parser.parse_args()

    print_banner()

    # Load configuration
    config = AppConfig()

    # Apply CLI overrides
    if args.wake_word:
        config.voice.wake_word = args.wake_word
    if args.model:
        config.llm.model = args.model

    # Validate
    issues = config.validate()
    if issues:
        for issue in issues:
            console.print(f"[bold red]Warning:[/] {issue}")
        console.print(
            "\n[yellow]Tip: Copy .env.example to .env and fill in your API keys.[/]\n"
        )

    # Run in selected mode
    if args.mode == "text":
        run_text_mode(config)
    else:
        if args.continuous:
            console.print("[cyan]Continuous listening mode enabled.[/]")
            agent = JarvisAgent(config)
            agent.listener.set_continuous_mode(True)
            agent.start()
        else:
            run_voice_mode(config)


if __name__ == "__main__":
    main()
