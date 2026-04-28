# Jarvis AI Assistant

A voice-controlled agentic AI that runs on your laptop. Speak naturally and Jarvis will execute tasks on your computer — opening apps, managing files, browsing the web, controlling system settings, and more.

## Features

- **Always-On Voice Listening** — Continuous microphone listening with wake word detection ("Jarvis")
- **Natural Conversation** — Speak like you're talking to a human assistant
- **Desktop Automation** — Control mouse, keyboard, open/close apps, type text, click, scroll
- **File Management** — Create, read, move, delete, and search files using voice commands
- **Web Browsing** — Open URLs, search the web, all hands-free
- **System Control** — Adjust volume, brightness, lock screen, get system info
- **Screen Understanding** — Takes screenshots and uses LLM vision to understand what's on your screen
- **Context-Aware** — Remembers your conversation and uses it to give better responses
- **Persistent Memory** — Saves preferences and context between sessions
- **Text Mode** — Fall back to text input when no microphone is available

## Architecture

```
jarvis/
├── config.py                    # Configuration management
├── main.py                      # Entry point & CLI
├── core/
│   ├── agent.py                 # Main orchestrator
│   ├── brain.py                 # LLM integration (Groq / Llama)
│   └── action_executor.py       # Translates plans to actions
├── modules/
│   ├── voice/
│   │   ├── listener.py          # Microphone listening & speech recognition
│   │   └── speaker.py           # Text-to-speech output
│   ├── automation/
│   │   ├── desktop.py           # Mouse, keyboard, clipboard control
│   │   ├── file_manager.py      # File system operations
│   │   ├── app_launcher.py      # Open/close applications
│   │   └── system_control.py    # Volume, brightness, system info
│   ├── vision/
│   │   └── screen_capture.py    # Screenshot & vision analysis
│   └── conversation/
│       └── manager.py           # Dialogue history & memory
└── utils/
    └── logger.py                # Logging with rich output
```

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai-assistant.git
cd jarvis-ai-assistant
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

### 3. Run

```bash
source .venv/bin/activate

# Voice mode (default) — say "Jarvis" to start
jarvis

# Text mode — type commands instead
jarvis --mode text

# Continuous listening — no wake word needed
jarvis --continuous

# Custom wake word
jarvis --wake-word hey-computer

# Use a specific model
jarvis --model llama-3.1-8b-instant
```

## Requirements

- **Python 3.10+**
- **Groq API Key** (free at https://console.groq.com/keys)
- **Microphone** (for voice mode)
- **Speakers** (for voice output)

### System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt install portaudio19-dev espeak xdotool xclip scrot python3-tk
```

**macOS:**
```bash
brew install portaudio espeak
```

**Windows:**
- Install [PyAudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Install [espeak](https://espeak.sourceforge.net/)

## Usage Examples

### Voice Commands

| Say this | Jarvis does |
|----------|-------------|
| "Open Chrome" | Launches Google Chrome |
| "Search the web for Python tutorials" | Opens Google search |
| "Create a file called notes.txt on my desktop" | Creates the file |
| "What's on my screen?" | Takes a screenshot, analyzes it |
| "Set volume to 50 percent" | Adjusts system volume |
| "Open VS Code and create a new file" | Multi-step task execution |
| "What files are in my Downloads folder?" | Lists directory contents |
| "Type Hello World" | Types text at cursor position |
| "Press Control C" | Presses keyboard shortcut |
| "What's my battery level?" | Reports system info |
| "Run the command 'ls -la'" | Executes terminal command |

### Text Mode

```
You: open chrome and go to github.com
Jarvis: Opening Chrome and navigating to GitHub for you.

You: what's my system info
Jarvis: Here's your system information: CPU at 12%, 8GB RAM, 45% disk used, battery at 78%.

You: create a folder called projects in my home directory
Jarvis: Created the 'projects' folder in your home directory.
```

## Configuration

All settings can be configured via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (required) | Your Groq API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | LLM API endpoint |
| `WAKE_WORD` | `jarvis` | Word to activate listening |
| `VOICE_RATE` | `175` | Speech speed (words per minute) |
| `VOICE_VOLUME` | `0.9` | Speech volume (0.0 to 1.0) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model for understanding |
| `LLM_TEMPERATURE` | `0.3` | Response creativity (0.0 to 1.0) |
| `MAX_CONVERSATION_HISTORY` | `20` | Messages to remember |
| `CONVERSATION_TIMEOUT` | `300` | Seconds before session resets |

## How It Works

1. **Listen** — Microphone captures your voice continuously
2. **Recognize** — Google Speech Recognition converts speech to text
3. **Understand** — Llama 3.3 (via Groq) interprets your intent and plans actions
4. **Execute** — Actions are performed on your laptop (mouse, keyboard, apps, files, etc.)
5. **Respond** — Jarvis speaks back to confirm what was done
6. **Remember** — Conversation context is maintained for follow-up commands

## License

MIT License - see [LICENSE](LICENSE) for details.
