"""
Shared pytest fixtures for CodexCLI tests
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from codexcli.context import ConversationContext, Message
from codexcli.approval import ApprovalManager, ApprovalMode
from codexcli.file_ops import FileOperations


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_project_dir(temp_dir):
    """Create a test project directory structure"""
    project = temp_dir / "test_project"
    project.mkdir()

    # Create some test files
    (project / "test.py").write_text("print('hello')")
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("def main():\n    pass")
    (project / "README.md").write_text("# Test Project")

    return project


@pytest.fixture
def conversation_context(temp_dir, monkeypatch):
    """Create a conversation context for testing"""
    # Mock the file paths to use temp directory so tests don't interfere
    monkeypatch.setattr("codexcli.context.get_context_file", lambda: temp_dir / "context.json")
    monkeypatch.setattr("codexcli.context.get_history_file", lambda: temp_dir / "history.json")
    return ConversationContext(max_history=10)


@pytest.fixture
def approval_manager():
    """Create an approval manager in FULL_AUTO mode for testing"""
    return ApprovalManager(mode=ApprovalMode.FULL_AUTO)


@pytest.fixture
def file_ops(approval_manager, temp_dir):
    """Create a file operations instance"""
    return FileOperations(approval_manager, temp_dir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "This is a test response"
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_openai_provider(mock_openai_client):
    """Mock OpenAI provider"""
    with patch("openai.OpenAI", return_value=mock_openai_client):
        from codexcli.agent import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key", model="gpt-4")
        yield provider


@pytest.fixture
def mock_anthropic_provider(mock_anthropic_client):
    """Mock Anthropic provider"""
    with patch("anthropic.Anthropic", return_value=mock_anthropic_client):
        from codexcli.agent import AnthropicProvider

        provider = AnthropicProvider(api_key="test_key", model="claude-3-5-sonnet-20241022")
        yield provider


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


@pytest.fixture
def sample_agent_response():
    """Sample agent response with actions"""
    return """
Here's what I'll do:

<CREATE_FILE>
test.py
---
print('Hello World')
</CREATE_FILE>

<EDIT_FILE>
main.py
---
def main():
    print('Updated')
</EDIT_FILE>

<SHELL_COMMAND>
python test.py
</SHELL_COMMAND>
"""


@pytest.fixture
def mock_console():
    """Mock rich console for testing"""
    with patch("codexcli.utils.console") as mock:
        yield mock


@pytest.fixture
def mock_confirm():
    """Mock confirmation prompt"""
    with patch("codexcli.utils.confirm", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_prompt():
    """Mock prompt_toolkit prompt"""
    with patch("codexcli.utils.prompt", return_value="test input") as mock:
        yield mock


@pytest.fixture
def env_vars():
    """Set up environment variables for testing"""
    original_env = os.environ.copy()
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for shell command tests"""
    with patch("subprocess.run") as mock:
        mock.return_value = MagicMock(returncode=0, stdout="Command output", stderr="")
        yield mock


@pytest.fixture
def sample_file_content():
    """Sample file content for testing"""
    return """def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""


@pytest.fixture
def binary_file_content():
    """Binary content for testing"""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
