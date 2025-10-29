"""
Tests for context module
"""
import pytest
from pathlib import Path
from codexcli.context import Message, ConversationContext, ProjectContext


def test_message_creation():
    """Test creating a message"""
    msg = Message(role="user", content="Hello", timestamp="2024-01-01T00:00:00")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_message_with_metadata():
    """Test creating a message with metadata"""
    metadata = {"action": "file_create", "filename": "test.py"}
    msg = Message(role="assistant", content="Done", timestamp="2024-01-01T00:00:00", metadata=metadata)
    assert msg.metadata == metadata
    assert msg.metadata["action"] == "file_create"


def test_message_to_dict():
    """Test converting message to dict"""
    msg = Message(role="user", content="Hello", timestamp="2024-01-01T00:00:00")
    data = msg.to_dict()
    assert data["role"] == "user"
    assert data["content"] == "Hello"


def test_message_from_dict():
    """Test creating message from dict"""
    data = {
        "role": "assistant",
        "content": "Hi there",
        "timestamp": "2024-01-01T00:00:00",
        "metadata": {}
    }
    msg = Message.from_dict(data)
    assert msg.role == "assistant"
    assert msg.content == "Hi there"


def test_conversation_context():
    """Test conversation context"""
    context = ConversationContext(max_history=5)
    context.clear()  # Clear any loaded history
    assert len(context.get_messages()) == 0

    context.add_user_message("Hello")
    assert len(context.get_messages()) == 1

    context.add_assistant_message("Hi there")
    assert len(context.get_messages()) == 2


def test_conversation_context_max_history():
    """Test that conversation context respects max_history"""
    context = ConversationContext(max_history=3)

    for i in range(5):
        context.add_user_message(f"Message {i}")

    messages = context.get_messages()
    assert len(messages) == 3
    assert messages[0].content == "Message 2"
    assert messages[-1].content == "Message 4"


def test_conversation_context_clear():
    """Test clearing conversation context"""
    context = ConversationContext()
    context.clear()  # Start fresh
    context.add_user_message("Hello")
    context.add_assistant_message("Hi")

    assert len(context.get_messages()) == 2

    context.clear()
    assert len(context.get_messages()) == 0


def test_conversation_context_system_message():
    """Test adding system message"""
    context = ConversationContext(max_history=5)
    context.clear()  # Start fresh
    context.add_system_message("You are a helpful assistant")

    messages = context.get_messages()
    assert len(messages) == 1
    assert messages[0].role == "system"


def test_conversation_context_get_messages_for_api():
    """Test getting messages formatted for API"""
    context = ConversationContext(max_history=5)
    context.clear()  # Start fresh
    context.add_user_message("Hello")
    context.add_assistant_message("Hi")

    api_messages = context.get_messages_for_api()
    assert len(api_messages) == 2
    assert api_messages[0] == {"role": "user", "content": "Hello"}
    assert api_messages[1] == {"role": "assistant", "content": "Hi"}


def test_conversation_context_summary():
    """Test getting conversation summary"""
    context = ConversationContext(max_history=5)
    context.clear()  # Start fresh
    summary = context.get_summary()
    assert "No conversation history" in summary

    context.add_user_message("Test message")
    summary = context.get_summary()
    assert "Messages: 1" in summary
    assert "Session:" in summary


def test_conversation_context_session_id():
    """Test that session ID is set"""
    context = ConversationContext()
    assert context.session_id is not None
    assert len(context.session_id) > 0


def test_project_context_initialization(test_project_dir):
    """Test initializing project context"""
    context = ProjectContext(test_project_dir)
    assert context.project_root == test_project_dir
    assert len(context.files_context) == 0
    assert len(context.relevant_files) == 0


def test_project_context_add_file(test_project_dir):
    """Test adding file to project context"""
    context = ProjectContext(test_project_dir)
    test_file = test_project_dir / "test.py"

    context.add_file(test_file)

    assert len(context.files_context) == 1
    assert "test.py" in context.files_context
    assert context.files_context["test.py"] == "print('hello')"
    assert test_file in context.relevant_files


def test_project_context_add_file_with_content(test_project_dir):
    """Test adding file with explicit content"""
    context = ProjectContext(test_project_dir)
    test_file = test_project_dir / "test.py"

    context.add_file(test_file, "custom content")

    assert context.files_context["test.py"] == "custom content"


def test_project_context_add_nonexistent_file(test_project_dir):
    """Test adding non-existent file"""
    context = ProjectContext(test_project_dir)
    fake_file = test_project_dir / "nonexistent.py"

    # Should not crash, just not add it
    context.add_file(fake_file)
    assert len(context.files_context) == 0


def test_project_context_get_context_summary(test_project_dir):
    """Test getting project context summary"""
    context = ProjectContext(test_project_dir)
    summary = context.get_context_summary()
    assert "test_project" in summary
    assert "Files in context: 0" in summary

    test_file = test_project_dir / "test.py"
    context.add_file(test_file)

    summary = context.get_context_summary()
    assert "Files in context: 1" in summary
    assert "Recent files:" in summary


def test_project_context_get_files_content(test_project_dir):
    """Test getting formatted files content"""
    context = ProjectContext(test_project_dir)

    # Empty context
    content = context.get_files_content()
    assert content == ""

    # Add a file
    test_file = test_project_dir / "test.py"
    context.add_file(test_file)

    content = context.get_files_content()
    assert "Project Files Context" in content
    assert "test.py" in content
    assert "print('hello')" in content


def test_project_context_multiple_files(test_project_dir):
    """Test adding multiple files to context"""
    context = ProjectContext(test_project_dir)

    files = [
        test_project_dir / "test.py",
        test_project_dir / "src" / "main.py",
        test_project_dir / "README.md"
    ]

    for file in files:
        context.add_file(file)

    assert len(context.files_context) == 3
    assert len(context.relevant_files) == 3
    assert "test.py" in context.files_context
    assert "src/main.py" in context.files_context
    assert "README.md" in context.files_context


def test_project_context_binary_file(test_project_dir):
    """Test adding binary file to context"""
    context = ProjectContext(test_project_dir)
    binary_file = test_project_dir / "test.bin"
    binary_file.write_bytes(b'\x89PNG\r\n\x1a\n')

    context.add_file(binary_file)

    assert "test.bin" in context.files_context
    assert "[Binary or unreadable file]" in context.files_context["test.bin"]
