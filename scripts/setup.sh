#!/bin/bash
# Jarvis AI Assistant - Setup Script
# Installs system dependencies and sets up the Python environment.

set -e

echo "======================================"
echo "  Jarvis AI Assistant - Setup Script"
echo "======================================"
echo

# Detect OS
OS="$(uname -s)"
echo "Detected OS: $OS"

# Install system dependencies
if [ "$OS" = "Linux" ]; then
    echo "Installing Linux dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        portaudio19-dev \
        python3-pyaudio \
        espeak \
        libespeak1 \
        xdotool \
        xclip \
        scrot \
        python3-tk \
        python3-dev \
        libasound2-dev \
        2>/dev/null

elif [ "$OS" = "Darwin" ]; then
    echo "Installing macOS dependencies..."
    brew install portaudio espeak 2>/dev/null || true

else
    echo "Windows detected. Please install the following manually:"
    echo "  - PyAudio: pip install pyaudio"
    echo "  - espeak: https://espeak.sourceforge.net/"
fi

echo

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install the package
echo "Installing Jarvis AI Assistant..."
pip install -e ".[dev]"

echo
echo "======================================"
echo "  Setup complete!"
echo "======================================"
echo
echo "Next steps:"
echo "  1. Copy .env.example to .env:"
echo "     cp .env.example .env"
echo "  2. Add your OpenAI API key to .env"
echo "  3. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo "  4. Run Jarvis:"
echo "     jarvis              # Voice mode"
echo "     jarvis --mode text  # Text mode (no mic needed)"
echo "     jarvis --continuous # No wake word needed"
echo
