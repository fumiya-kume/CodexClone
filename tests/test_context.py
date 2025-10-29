"""
Tests for context module
"""
import pytest
from codexcli.context import Message, ConversationContext


def test_message_creation():
    """Test creating a message"""
    msg = Message(role="user", content="Hello", timestamp="2024-01-01T00:00:00")
    assert msg.role == "user"
    assert msg.content == "Hello"


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
    context.add_user_message("Hello")
    context.add_assistant_message("Hi")

    assert len(context.get_messages()) == 2

    context.clear()
    assert len(context.get_messages()) == 0
