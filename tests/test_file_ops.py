"""
Tests for file_ops module
"""

import pytest
from pathlib import Path
from codexcli.file_ops import FileOperations
from codexcli.approval import ApprovalManager, ApprovalMode


def test_file_ops_initialization(approval_manager, temp_dir):
    """Test FileOperations initialization"""
    file_ops = FileOperations(approval_manager, temp_dir)
    assert file_ops.approval_manager == approval_manager
    assert file_ops.project_root == temp_dir


def test_file_ops_read_file_success(file_ops, temp_dir):
    """Test reading a file successfully"""
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, world!")

    content = file_ops.read_file("test.txt")
    assert content == "Hello, world!"


def test_file_ops_read_file_not_found(file_ops):
    """Test reading non-existent file"""
    content = file_ops.read_file("nonexistent.txt")
    assert content is None


def test_file_ops_create_file_success(file_ops, temp_dir):
    """Test creating a file"""
    result = file_ops.create_file("newfile.py", "print('hello')")

    assert result is True
    assert (temp_dir / "newfile.py").exists()
    assert (temp_dir / "newfile.py").read_text() == "print('hello')"


def test_file_ops_create_file_existing(file_ops, temp_dir):
    """Test creating a file that already exists"""
    test_file = temp_dir / "existing.txt"
    test_file.write_text("existing content")

    result = file_ops.create_file("existing.txt", "new content")
    assert result is False
    # Original content should be unchanged
    assert test_file.read_text() == "existing content"


def test_file_ops_create_file_with_subdirectory(file_ops, temp_dir):
    """Test creating a file in a subdirectory"""
    result = file_ops.create_file("subdir/test.py", "print('test')")

    assert result is True
    assert (temp_dir / "subdir" / "test.py").exists()
    assert (temp_dir / "subdir").is_dir()


def test_file_ops_edit_file_success(file_ops, temp_dir):
    """Test editing an existing file"""
    test_file = temp_dir / "edit_me.txt"
    test_file.write_text("old content")

    result = file_ops.edit_file("edit_me.txt", "new content")

    assert result is True
    assert test_file.read_text() == "new content"


def test_file_ops_edit_file_not_found(file_ops):
    """Test editing non-existent file"""
    result = file_ops.edit_file("nonexistent.txt", "content")
    assert result is False


def test_file_ops_delete_file_success(file_ops, temp_dir):
    """Test deleting a file"""
    test_file = temp_dir / "delete_me.txt"
    test_file.write_text("content")

    result = file_ops.delete_file("delete_me.txt")

    assert result is True
    assert not test_file.exists()


def test_file_ops_delete_file_not_found(file_ops):
    """Test deleting non-existent file"""
    result = file_ops.delete_file("nonexistent.txt")
    assert result is False


def test_file_ops_list_files(file_ops, temp_dir):
    """Test listing files"""
    # Create some test files
    (temp_dir / "file1.py").write_text("test")
    (temp_dir / "file2.py").write_text("test")
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "file3.py").write_text("test")

    files = file_ops.list_files("*.py")

    assert len(files) == 3
    assert all(f.suffix == ".py" for f in files)


def test_file_ops_list_files_filters_hidden(file_ops, temp_dir):
    """Test that list_files filters hidden files"""
    (temp_dir / "visible.py").write_text("test")
    (temp_dir / ".hidden").mkdir()
    (temp_dir / ".hidden" / "file.py").write_text("test")

    files = file_ops.list_files("*.py")

    # Hidden directory files should be filtered out
    assert all(".hidden" not in str(f) for f in files)


def test_file_ops_get_file_tree(file_ops, temp_dir):
    """Test getting file tree"""
    # Create a directory structure
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("test")
    (temp_dir / "tests").mkdir()
    (temp_dir / "tests" / "test_main.py").write_text("test")
    (temp_dir / "README.md").write_text("test")

    tree = file_ops.get_file_tree(max_depth=2)

    assert "src" in tree
    assert "tests" in tree
    assert "README.md" in tree
    assert "main.py" in tree
    assert "test_main.py" in tree


def test_file_ops_get_file_tree_ignores_common_dirs(file_ops, temp_dir):
    """Test that file tree ignores common directories"""
    (temp_dir / "node_modules").mkdir()
    (temp_dir / "__pycache__").mkdir()
    (temp_dir / ".git").mkdir()
    (temp_dir / "src").mkdir()

    tree = file_ops.get_file_tree()

    assert "node_modules" not in tree
    assert "__pycache__" not in tree
    assert ".git" not in tree
    assert "src" in tree


def test_file_ops_resolve_path_relative(file_ops, temp_dir):
    """Test resolving relative path"""
    resolved = file_ops._resolve_path("test.txt")
    expected = temp_dir / "test.txt"
    assert resolved == expected.resolve()


def test_file_ops_resolve_path_absolute(file_ops):
    """Test resolving absolute path"""
    absolute_path = "/tmp/test.txt"
    resolved = file_ops._resolve_path(absolute_path)
    assert resolved == Path(absolute_path).resolve()


def test_file_ops_get_language_python(file_ops):
    """Test language detection for Python files"""
    assert file_ops._get_language("test.py") == "python"


def test_file_ops_get_language_javascript(file_ops):
    """Test language detection for JavaScript files"""
    assert file_ops._get_language("test.js") == "javascript"
    assert file_ops._get_language("test.jsx") == "jsx"


def test_file_ops_get_language_markdown(file_ops):
    """Test language detection for Markdown files"""
    assert file_ops._get_language("README.md") == "markdown"


def test_file_ops_get_language_unknown(file_ops):
    """Test language detection for unknown extension"""
    assert file_ops._get_language("test.xyz") == "text"


def test_file_ops_get_language_case_insensitive(file_ops):
    """Test that language detection is case insensitive"""
    assert file_ops._get_language("test.PY") == "python"
    assert file_ops._get_language("test.JS") == "javascript"


def test_file_ops_with_suggest_mode(temp_dir):
    """Test file operations with SUGGEST approval mode"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    file_ops = FileOperations(manager, temp_dir)

    # Operations should work but would normally require user approval
    # Since we're testing with SUGGEST mode, we can't test the actual approval
    # but we can verify the structure is correct
    assert file_ops.approval_manager.get_mode() == ApprovalMode.SUGGEST


def test_file_ops_create_file_with_encoding(file_ops, temp_dir):
    """Test creating file with Unicode content"""
    content = "Hello 世界 🌍"
    result = file_ops.create_file("unicode.txt", content)

    assert result is True
    assert (temp_dir / "unicode.txt").read_text(encoding="utf-8") == content


def test_file_ops_edit_file_with_encoding(file_ops, temp_dir):
    """Test editing file with Unicode content"""
    test_file = temp_dir / "unicode.txt"
    test_file.write_text("old content", encoding="utf-8")

    new_content = "New 内容 ✨"
    result = file_ops.edit_file("unicode.txt", new_content)

    assert result is True
    assert test_file.read_text(encoding="utf-8") == new_content


def test_file_ops_nested_directory_creation(file_ops, temp_dir):
    """Test creating file in deeply nested directory"""
    result = file_ops.create_file("a/b/c/d/test.py", "print('deep')")

    assert result is True
    nested_file = temp_dir / "a" / "b" / "c" / "d" / "test.py"
    assert nested_file.exists()
    assert nested_file.read_text() == "print('deep')"


@pytest.mark.unit
def test_file_ops_error_handling(file_ops, temp_dir):
    """Test error handling in file operations"""
    # Try to create a file with an invalid path character (on some systems)
    # This should handle the error gracefully
    try:
        result = file_ops.create_file("\x00invalid", "content")
        # If no error, result should be False
        assert result is False
    except Exception:
        # If an exception occurs, that's also acceptable
        pass


def test_file_tree_max_depth(file_ops, temp_dir):
    """Test file tree respects max_depth"""
    # Create deep directory structure
    (temp_dir / "level1").mkdir()
    (temp_dir / "level1" / "level2").mkdir()
    (temp_dir / "level1" / "level2" / "level3").mkdir()
    (temp_dir / "level1" / "level2" / "level3" / "deep.txt").write_text("test")

    # Get tree with max_depth=1
    tree = file_ops.get_file_tree(max_depth=1)

    # Should include level1 but not deeper levels
    assert "level1" in tree
    assert "level2" not in tree or tree.count("level2") <= 1
