"""
Tests for utils module
"""
import pytest
from pathlib import Path
from codexcli.utils import truncate_content, is_text_file


def test_truncate_content():
    """Test truncating content"""
    short_text = "Hello, world!"
    assert truncate_content(short_text, max_length=100) == short_text

    long_text = "a" * 2000
    truncated = truncate_content(long_text, max_length=100)
    assert len(truncated) < len(long_text)
    assert "truncated" in truncated


def test_is_text_file():
    """Test checking if file is text file"""
    assert is_text_file(Path("test.py")) is True
    assert is_text_file(Path("test.js")) is True
    assert is_text_file(Path("test.md")) is True
    assert is_text_file(Path("test.json")) is True
    assert is_text_file(Path("test.txt")) is True
    assert is_text_file(Path("test.pdf")) is False
    assert is_text_file(Path("test.jpg")) is False
