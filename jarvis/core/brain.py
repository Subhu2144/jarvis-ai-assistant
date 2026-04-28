"""LLM Brain - The intelligence behind Jarvis that understands instructions and plans actions."""

import json
from typing import Any

from openai import OpenAI

from jarvis.config import LLMConfig
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

SYSTEM_PROMPT = """You are Jarvis, an intelligent AI assistant that controls the user's laptop.
You understand natural language instructions and convert them into executable actions.

You can perform the following action types:
- open_app: Open an application (params: app_name)
- close_app: Close an application (params: app_name)
- type_text: Type text using keyboard (params: text)
- press_key: Press a key or key combination (params: keys)
- click: Click at screen coordinates or on an element (params: x, y, button)
- scroll: Scroll up or down (params: direction, amount)
- move_mouse: Move mouse to position (params: x, y)
- screenshot: Take a screenshot (params: none)
- create_file: Create a file (params: path, content)
- read_file: Read a file (params: path)
- delete_file: Delete a file (params: path)
- move_file: Move/rename a file (params: source, destination)
- list_files: List files in a directory (params: path)
- search_files: Search for files (params: query, path)
- run_command: Run a terminal command (params: command)
- open_url: Open a URL in browser (params: url)
- search_web: Search the web (params: query)
- set_volume: Set system volume (params: level)
- set_brightness: Set screen brightness (params: level)
- system_info: Get system information (params: none)
- speak: Say something to the user (params: text)
- wait: Wait for some time (params: seconds)
- chain: Execute multiple actions in sequence (params: actions)

When responding, output a JSON object with:
{
    "thought": "Your reasoning about what the user wants",
    "response": "What to say to the user",
    "actions": [
        {
            "type": "action_type",
            "params": {param: value}
        }
    ]
}

Rules:
- Always think step by step about what the user wants
- Break complex tasks into multiple simple actions
- Provide helpful responses explaining what you're doing
- If unsure, ask for clarification (no actions, just response)
- For dangerous operations (deleting files, running commands), confirm first
- Be conversational and friendly like a human assistant
"""


class Brain:
    """The LLM-powered brain that understands and plans actions."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self.model = config.model

    def think(self, user_input: str, context: list[dict[str, str]] | None = None) -> dict[str, Any]:
        """Process user input and return thought, response, and planned actions."""
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            if "thought" not in result:
                result["thought"] = ""
            if "response" not in result:
                result["response"] = "I'm not sure how to help with that."
            if "actions" not in result:
                result["actions"] = []

            logger.debug(f"Brain thought: {result['thought']}")
            logger.debug(f"Planned actions: {len(result['actions'])}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "thought": "Failed to parse response",
                "response": "I had trouble understanding that. Could you rephrase?",
                "actions": [],
            }
        except Exception as e:
            logger.error(f"Brain error: {e}")
            return {
                "thought": f"Error: {e}",
                "response": "I encountered an error. Please try again.",
                "actions": [],
            }

    def analyze_screen(
        self, screenshot_base64: str, user_input: str, context: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """Analyze a screenshot with the user's question for context-aware actions."""
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.extend(context)

        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Here's what's on my screen. {user_input}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"},
                    },
                ],
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config.vision_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            result = json.loads(content)

            if "thought" not in result:
                result["thought"] = ""
            if "response" not in result:
                result["response"] = "I'm not sure how to help with that."
            if "actions" not in result:
                result["actions"] = []

            return result

        except Exception as e:
            logger.error(f"Screen analysis error: {e}")
            return {
                "thought": f"Error analyzing screen: {e}",
                "response": "I had trouble analyzing the screen.",
                "actions": [],
            }
