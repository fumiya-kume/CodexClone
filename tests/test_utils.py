"""
Tests for utils module
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from codexcli.utils import (
    truncate_content,
    is_text_file,
    get_project_root,
    get_config_dir,
    get_history_file,
    get_context_file,
    read_file_safe,
    print_info,
    print_success,
    print_error,
    print_warning,
)


def test_truncate_content():
    """Test truncating content"""
    short_text = "Hello, world!"
    assert truncate_content(short_text, max_length=100) == short_text

    long_text = "a" * 2000
    truncated = truncate_content(long_text, max_length=100)
    assert len(truncated) < len(long_text)
    assert "truncated" in truncated


def test_truncate_content_exact_length():
    """Test truncating content at exact max length"""
    text = "a" * 100
    assert truncate_content(text, max_length=100) == text


def test_truncate_content_empty():
    """Test truncating empty content"""
    assert truncate_content("", max_length=100) == ""


def test_is_text_file():
    """Test checking if file is text file"""
    # Text files
    assert is_text_file(Path("test.py")) is True
    assert is_text_file(Path("test.js")) is True
    assert is_text_file(Path("test.md")) is True
    assert is_text_file(Path("test.json")) is True
    assert is_text_file(Path("test.txt")) is True
    assert is_text_file(Path("test.yaml")) is True
    assert is_text_file(Path("test.yml")) is True
    assert is_text_file(Path("test.toml")) is True

    # Non-text files
    assert is_text_file(Path("test.pdf")) is False
    assert is_text_file(Path("test.jpg")) is False
    assert is_text_file(Path("test.png")) is False
    assert is_text_file(Path("test.exe")) is False


def test_is_text_file_case_insensitive():
    """Test that extension check is case insensitive"""
    assert is_text_file(Path("test.PY")) is True
    assert is_text_file(Path("test.Js")) is True
    assert is_text_file(Path("test.JSON")) is True


def test_get_project_root():
    """Test getting project root"""
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()


def test_get_config_dir():
    """Test getting config directory"""
    config_dir = get_config_dir()
    assert isinstance(config_dir, Path)
    assert config_dir.exists()
    assert config_dir.name == ".codexcli"


def test_get_history_file():
    """Test getting history file path"""
    history_file = get_history_file()
    assert isinstance(history_file, Path)
    assert history_file.name == "history.json"
    assert history_file.parent.name == ".codexcli"


def test_get_context_file():
    """Test getting context file path"""
    context_file = get_context_file()
    assert isinstance(context_file, Path)
    assert context_file.name == "context.json"
    assert context_file.parent.name == ".codexcli"


def test_read_file_safe_success(temp_dir):
    """Test reading a file successfully"""
    test_file = temp_dir / "test.txt"
    test_content = "Hello, world!"
    test_file.write_text(test_content)

    content = read_file_safe(test_file)
    assert content == test_content


def test_read_file_safe_too_large(temp_dir):
    """Test reading a file that is too large"""
    test_file = temp_dir / "large.txt"
    # Create a file larger than 500KB (default limit)
    large_content = "a" * (600 * 1024)
    test_file.write_text(large_content)

    content = read_file_safe(test_file, max_size_kb=500)
    assert content is None


def test_read_file_safe_binary_file(temp_dir):
    """Test reading a binary file"""
    test_file = temp_dir / "test.bin"
    test_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    content = read_file_safe(test_file)
    assert content is None


def test_read_file_safe_nonexistent(temp_dir):
    """Test reading a non-existent file"""
    test_file = temp_dir / "nonexistent.txt"
    content = read_file_safe(test_file)
    assert content is None


def test_read_file_safe_custom_size_limit(temp_dir):
    """Test reading with custom size limit"""
    test_file = temp_dir / "test.txt"
    test_content = "a" * 100
    test_file.write_text(test_content)

    # Should succeed with higher limit
    content = read_file_safe(test_file, max_size_kb=1)
    assert content == test_content

    # Should fail with very low limit
    content = read_file_safe(test_file, max_size_kb=0)
    assert content is None


@pytest.mark.unit
def test_print_functions():
    """Test print utility functions"""
    # Just verify they don't crash
    print_info("info message")
    print_success("success message")
    print_error("error message")
    print_warning("warning message")
