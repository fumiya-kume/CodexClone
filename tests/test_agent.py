"""
Tests for agent module
"""

import pytest
from unittest.mock import patch, MagicMock
from codexcli.agent import LLMProvider, OpenAIProvider, AnthropicProvider, CodexAgent, create_agent
from codexcli.context import ConversationContext


def test_llm_provider_base_class():
    """Test that LLMProvider is abstract"""
    provider = LLMProvider(api_key="test", model="test-model")
    assert provider.api_key == "test"
    assert provider.model == "test-model"

    with pytest.raises(NotImplementedError):
        provider.generate([])


def test_openai_provider_initialization(mock_openai_client):
    """Test OpenAI provider initialization"""
    with patch("openai.OpenAI", return_value=mock_openai_client):
        provider = OpenAIProvider(api_key="test_key", model="gpt-4")
        assert provider.api_key == "test_key"
        assert provider.model == "gpt-4"
        assert provider.client is not None


def test_openai_provider_generate_success(mock_openai_provider, mock_openai_client):
    """Test successful OpenAI generation"""
    messages = [{"role": "user", "content": "Hello"}]
    success, response = mock_openai_provider.generate(messages)

    assert success is True
    assert response == "This is a test response"
    mock_openai_client.chat.completions.create.assert_called_once()


def test_openai_provider_generate_with_parameters(mock_openai_provider, mock_openai_client):
    """Test OpenAI generation with custom parameters"""
    messages = [{"role": "user", "content": "Hello"}]
    success, response = mock_openai_provider.generate(messages, temperature=0.5, max_tokens=1000)

    assert success is True
    call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
    assert call_kwargs["temperature"] == 0.5
    assert call_kwargs["max_tokens"] == 1000


def test_openai_provider_generate_error(mock_openai_provider, mock_openai_client):
    """Test OpenAI generation error handling"""
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

    messages = [{"role": "user", "content": "Hello"}]
    success, response = mock_openai_provider.generate(messages)

    assert success is False
    assert "API Error" in response


def test_anthropic_provider_initialization(mock_anthropic_client):
    """Test Anthropic provider initialization"""
    with patch("anthropic.Anthropic", return_value=mock_anthropic_client):
        provider = AnthropicProvider(api_key="test_key", model="claude-3-5-sonnet-20241022")
        assert provider.api_key == "test_key"
        assert provider.model == "claude-3-5-sonnet-20241022"
        assert provider.client is not None


def test_anthropic_provider_generate_success(mock_anthropic_provider, mock_anthropic_client):
    """Test successful Anthropic generation"""
    messages = [{"role": "user", "content": "Hello"}]
    success, response = mock_anthropic_provider.generate(messages)

    assert success is True
    assert response == "This is a test response"
    mock_anthropic_client.messages.create.assert_called_once()


def test_anthropic_provider_system_message_handling(mock_anthropic_provider, mock_anthropic_client):
    """Test that Anthropic provider handles system messages correctly"""
    messages = [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello"},
    ]
    success, response = mock_anthropic_provider.generate(messages)

    assert success is True
    call_kwargs = mock_anthropic_client.messages.create.call_args[1]
    assert call_kwargs["system"] == "You are helpful"
    # System message should be filtered from messages list
    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"


def test_anthropic_provider_generate_error(mock_anthropic_provider, mock_anthropic_client):
    """Test Anthropic generation error handling"""
    mock_anthropic_client.messages.create.side_effect = Exception("API Error")

    messages = [{"role": "user", "content": "Hello"}]
    success, response = mock_anthropic_provider.generate(messages)

    assert success is False
    assert "API Error" in response


def test_codex_agent_initialization(mock_openai_provider, conversation_context):
    """Test CodexAgent initialization"""
    agent = CodexAgent(mock_openai_provider, conversation_context)
    assert agent.provider == mock_openai_provider
    assert agent.context == conversation_context


def test_codex_agent_ask(mock_openai_provider, conversation_context, mock_openai_client):
    """Test asking the agent a question"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = agent.ask("Hello, how are you?")

    assert response == "This is a test response"
    assert len(conversation_context.get_messages()) == 2  # user + assistant
    assert conversation_context.get_messages()[0].role == "user"
    assert conversation_context.get_messages()[1].role == "assistant"


def test_codex_agent_ask_with_additional_context(mock_openai_provider, conversation_context):
    """Test asking with additional context"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = agent.ask("What is this?", additional_context="File: test.py")

    assert response is not None
    # Additional context should be added to system message


def test_codex_agent_ask_failure(mock_openai_provider, conversation_context, mock_openai_client):
    """Test agent handling API failure"""
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

    agent = CodexAgent(mock_openai_provider, conversation_context)
    response = agent.ask("Hello")

    assert response is None


def test_codex_agent_parse_actions_create_file(conversation_context, mock_openai_provider):
    """Test parsing CREATE_FILE actions"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = """
Let me create a file for you.

<CREATE_FILE>
test.py
---
print('Hello World')
</CREATE_FILE>
"""

    actions = agent.parse_actions(response)

    assert len(actions) == 1
    assert actions[0]["type"] == "create_file"
    assert actions[0]["filepath"] == "test.py"
    assert "print('Hello World')" in actions[0]["content"]


def test_codex_agent_parse_actions_edit_file(conversation_context, mock_openai_provider):
    """Test parsing EDIT_FILE actions"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = """
<EDIT_FILE>
main.py
---
def main():
    print('Updated')
</EDIT_FILE>
"""

    actions = agent.parse_actions(response)

    assert len(actions) == 1
    assert actions[0]["type"] == "edit_file"
    assert actions[0]["filepath"] == "main.py"
    assert "Updated" in actions[0]["content"]


def test_codex_agent_parse_actions_shell_command(conversation_context, mock_openai_provider):
    """Test parsing SHELL_COMMAND actions"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = """
<SHELL_COMMAND>
python test.py
</SHELL_COMMAND>
"""

    actions = agent.parse_actions(response)

    assert len(actions) == 1
    assert actions[0]["type"] == "shell_command"
    assert actions[0]["command"] == "python test.py"


def test_codex_agent_parse_actions_multiple(conversation_context, mock_openai_provider):
    """Test parsing multiple actions"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = """
I'll do three things:

<CREATE_FILE>
test.py
---
print('test')
</CREATE_FILE>

<EDIT_FILE>
main.py
---
updated content
</EDIT_FILE>

<SHELL_COMMAND>
python test.py
</SHELL_COMMAND>
"""

    actions = agent.parse_actions(response)

    assert len(actions) == 3
    assert actions[0]["type"] == "create_file"
    assert actions[1]["type"] == "edit_file"
    assert actions[2]["type"] == "shell_command"


def test_codex_agent_parse_actions_none(conversation_context, mock_openai_provider):
    """Test parsing response with no actions"""
    agent = CodexAgent(mock_openai_provider, conversation_context)

    response = "Just a regular response with no actions."

    actions = agent.parse_actions(response)

    assert len(actions) == 0


def test_create_agent_openai(env_vars):
    """Test creating OpenAI agent"""
    with patch("openai.OpenAI"):
        agent = create_agent(provider="openai")
        assert agent is not None
        assert isinstance(agent.provider, OpenAIProvider)


def test_create_agent_anthropic(env_vars):
    """Test creating Anthropic agent"""
    with patch("anthropic.Anthropic"):
        agent = create_agent(provider="anthropic")
        assert agent is not None
        assert isinstance(agent.provider, AnthropicProvider)


def test_create_agent_with_api_key():
    """Test creating agent with explicit API key"""
    with patch("openai.OpenAI"):
        agent = create_agent(provider="openai", api_key="custom_key")
        assert agent.provider.api_key == "custom_key"


def test_create_agent_with_model():
    """Test creating agent with custom model"""
    with patch("openai.OpenAI"):
        agent = create_agent(provider="openai", api_key="test", model="gpt-3.5-turbo")
        assert agent.provider.model == "gpt-3.5-turbo"


def test_create_agent_with_context(conversation_context):
    """Test creating agent with existing context"""
    with patch("openai.OpenAI"):
        agent = create_agent(provider="openai", api_key="test", context=conversation_context)
        assert agent.context == conversation_context


def test_create_agent_unknown_provider():
    """Test creating agent with unknown provider"""
    with pytest.raises(ValueError, match="Unknown provider"):
        create_agent(provider="unknown", api_key="test")


def test_create_agent_missing_api_key():
    """Test creating agent without API key"""
    with pytest.raises(ValueError, match="API_KEY not set"):
        create_agent(provider="openai")


@pytest.mark.unit
def test_codex_agent_system_prompt():
    """Test that system prompt is properly defined"""
    assert CodexAgent.SYSTEM_PROMPT is not None
    assert "CREATE_FILE" in CodexAgent.SYSTEM_PROMPT
    assert "EDIT_FILE" in CodexAgent.SYSTEM_PROMPT
    assert "SHELL_COMMAND" in CodexAgent.SYSTEM_PROMPT
