"""
AI Agent - LLM integration with OpenAI and Anthropic
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from .utils import print_error, print_info, print_warning, console
from .context import ConversationContext


class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, messages: List[Dict], **kwargs) -> Tuple[bool, str]:
        """
        Generate a response from the LLM

        Returns:
            Tuple of (success: bool, response: str)
        """
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        try:
            import openai

            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: uv sync")

    def generate(
        self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000
    ) -> Tuple[bool, str]:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            return True, content

        except Exception as e:
            error_msg = f"OpenAI API error: {e}"
            print_error(error_msg)
            return False, error_msg


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: uv sync")

    def generate(
        self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000
    ) -> Tuple[bool, str]:
        """Generate response using Anthropic API"""
        try:
            # Anthropic requires system messages to be separate
            system_message = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    filtered_messages.append(msg)

            kwargs = {
                "model": self.model,
                "messages": filtered_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if system_message:
                kwargs["system"] = system_message

            response = self.client.messages.create(**kwargs)

            content = response.content[0].text
            return True, content

        except Exception as e:
            error_msg = f"Anthropic API error: {e}"
            print_error(error_msg)
            return False, error_msg


class CodexAgent:
    """Main AI agent for code assistance"""

    SYSTEM_PROMPT = """You are a helpful AI coding assistant. You can:
- Read, create, edit, and analyze code files
- Execute shell commands
- Answer questions about code
- Suggest improvements and fixes
- Generate new code based on requirements

When suggesting file operations or shell commands, format them clearly:

For file creation:
<CREATE_FILE>
path/to/file.py
---
file content here
</CREATE_FILE>

For file editing:
<EDIT_FILE>
path/to/file.py
---
new file content here
</EDIT_FILE>

For shell commands:
<SHELL_COMMAND>
command to execute
</SHELL_COMMAND>

Always explain your reasoning and be concise but thorough."""

    def __init__(self, provider: LLMProvider, context: ConversationContext):
        self.provider = provider
        self.context = context

    def ask(self, user_input: str, additional_context: Optional[str] = None) -> Optional[str]:
        """
        Ask the agent a question or give it a task

        Returns:
            str: Agent's response, or None if failed
        """
        # Add user message to context
        self.context.add_user_message(user_input)

        # Build messages for API
        messages = self._build_messages(additional_context)

        # Generate response
        print_info(f"Thinking... (using {self.provider.model})")
        success, response = self.provider.generate(messages)

        if success:
            # Add assistant response to context
            self.context.add_assistant_message(response)
            return response
        else:
            return None

    def parse_actions(self, response: str) -> List[Dict]:
        """
        Parse actions from agent response

        Returns:
            List of actions to perform
        """
        actions = []

        # Parse CREATE_FILE actions
        import re

        create_pattern = r"<CREATE_FILE>\s*\n(.+?)\n---\n(.*?)</CREATE_FILE>"
        for match in re.finditer(create_pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            content = match.group(2).strip()
            actions.append({"type": "create_file", "filepath": filepath, "content": content})

        # Parse EDIT_FILE actions
        edit_pattern = r"<EDIT_FILE>\s*\n(.+?)\n---\n(.*?)</EDIT_FILE>"
        for match in re.finditer(edit_pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            content = match.group(2).strip()
            actions.append({"type": "edit_file", "filepath": filepath, "content": content})

        # Parse SHELL_COMMAND actions
        shell_pattern = r"<SHELL_COMMAND>\s*\n(.*?)\n</SHELL_COMMAND>"
        for match in re.finditer(shell_pattern, response, re.DOTALL):
            command = match.group(1).strip()
            actions.append({"type": "shell_command", "command": command})

        return actions

    def _build_messages(self, additional_context: Optional[str] = None) -> List[Dict]:
        """Build messages list for API call"""
        messages = []

        # Add system message
        system_content = self.SYSTEM_PROMPT
        if additional_context:
            system_content += f"\n\nAdditional Context:\n{additional_context}"

        messages.append({"role": "system", "content": system_content})

        # Add conversation history
        messages.extend(self.context.get_messages_for_api())

        return messages


def create_agent(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    context: Optional[ConversationContext] = None,
) -> CodexAgent:
    """
    Create an AI agent with the specified provider

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (if None, will try to get from environment)
        model: Model name (if None, will use default)
        context: Conversation context (if None, will create new)

    Returns:
        CodexAgent instance
    """
    # Get API key from environment if not provided
    if provider == "openai":
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        llm_provider = OpenAIProvider(api_key, model)

    elif provider == "anthropic":
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        llm_provider = AnthropicProvider(api_key, model)

    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Create context if not provided
    if context is None:
        context = ConversationContext()

    return CodexAgent(llm_provider, context)
