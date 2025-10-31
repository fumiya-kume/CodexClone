"""
Tests for shell module
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from codexcli.shell import ShellExecutor
from codexcli.approval import ApprovalManager, ApprovalMode


def test_shell_executor_initialization(approval_manager, temp_dir):
    """Test ShellExecutor initialization"""
    executor = ShellExecutor(approval_manager, temp_dir)
    assert executor.approval_manager == approval_manager
    assert executor.working_dir == temp_dir


def test_shell_executor_initialization_default_dir(approval_manager):
    """Test ShellExecutor initialization with default directory"""
    executor = ShellExecutor(approval_manager)
    assert executor.working_dir == Path.cwd()


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_success(mock_run, approval_manager, temp_dir):
    """Test successful command execution"""
    mock_run.return_value = MagicMock(returncode=0, stdout="command output", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("echo hello")

    assert success is True
    assert stdout == "command output"
    assert stderr == ""
    mock_run.assert_called_once()


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_failure(mock_run, approval_manager, temp_dir):
    """Test failed command execution"""
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error message")

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("false")

    assert success is False
    assert stderr == "error message"


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_timeout(mock_run, approval_manager, temp_dir):
    """Test command timeout"""
    mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("sleep 100", timeout=30)

    assert success is False
    assert "timed out" in stderr


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_exception(mock_run, approval_manager, temp_dir):
    """Test command execution exception"""
    mock_run.side_effect = Exception("Execution error")

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("invalid_command")

    assert success is False
    assert "Error executing command" in stderr


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_with_description(mock_run, approval_manager, temp_dir):
    """Test command execution with description"""
    mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("ls", description="List files")

    assert success is True


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_safe(mock_run, approval_manager, temp_dir):
    """Test execute_safe method"""
    mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    result = executor.execute_safe("echo test")

    assert result is True


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_execute_safe_failure(mock_run, approval_manager, temp_dir):
    """Test execute_safe method with failure"""
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

    executor = ShellExecutor(approval_manager, temp_dir)
    result = executor.execute_safe("false")

    assert result is False


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_get_output(mock_run, approval_manager, temp_dir):
    """Test get_output method"""
    mock_run.return_value = MagicMock(returncode=0, stdout="command output", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    output = executor.get_output("echo test")

    assert output == "command output"


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_get_output_failure(mock_run, approval_manager, temp_dir):
    """Test get_output method with failure"""
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

    executor = ShellExecutor(approval_manager, temp_dir)
    output = executor.get_output("false")

    assert output is None


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_is_command_available(mock_run, approval_manager, temp_dir):
    """Test checking if command is available"""
    mock_run.return_value = MagicMock(returncode=0)

    executor = ShellExecutor(approval_manager, temp_dir)
    available = executor.is_command_available("python")

    assert available is True


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_is_command_not_available(mock_run, approval_manager, temp_dir):
    """Test checking if command is not available"""
    mock_run.return_value = MagicMock(returncode=1)

    executor = ShellExecutor(approval_manager, temp_dir)
    available = executor.is_command_available("nonexistent_command_xyz")

    assert available is False


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_is_command_available_exception(mock_run, approval_manager, temp_dir):
    """Test is_command_available with exception"""
    mock_run.side_effect = Exception("Error")

    executor = ShellExecutor(approval_manager, temp_dir)
    available = executor.is_command_available("python")

    assert available is False


def test_shell_executor_with_suggest_mode(temp_dir):
    """Test shell executor with SUGGEST approval mode"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    executor = ShellExecutor(manager, temp_dir)

    assert executor.approval_manager.get_mode() == ApprovalMode.SUGGEST


@patch("codexcli.approval.confirm", return_value=False)
@patch("codexcli.shell.subprocess.run")
def test_shell_executor_approval_denied(mock_run, mock_confirm, temp_dir):
    """Test command execution when approval is denied"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    executor = ShellExecutor(manager, temp_dir)

    success, stdout, stderr = executor.execute("dangerous_command")

    assert success is False
    assert "cancelled" in stderr
    # subprocess.run should not be called if approval is denied
    mock_run.assert_not_called()


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_working_directory(mock_run, approval_manager, temp_dir):
    """Test that command is executed in working directory"""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    executor.execute("pwd")

    # Check that cwd parameter was passed to subprocess.run
    call_kwargs = mock_run.call_args[1]
    assert call_kwargs["cwd"] == temp_dir


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_custom_timeout(mock_run, approval_manager, temp_dir):
    """Test command execution with custom timeout"""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)
    executor.execute("sleep 1", timeout=60)

    # Check that timeout parameter was passed to subprocess.run
    call_kwargs = mock_run.call_args[1]
    assert call_kwargs["timeout"] == 60


@patch("codexcli.shell.subprocess.run")
def test_shell_executor_output_stripping(mock_run, approval_manager, temp_dir):
    """Test that output is stripped of whitespace"""
    mock_run.return_value = MagicMock(
        returncode=0, stdout="  output with spaces  \n", stderr="  error with spaces  \n"
    )

    executor = ShellExecutor(approval_manager, temp_dir)
    success, stdout, stderr = executor.execute("echo test")

    assert stdout == "output with spaces"
    assert stderr == "error with spaces"


@pytest.mark.unit
@patch("codexcli.shell.subprocess.run")
def test_shell_executor_multiple_commands(mock_run, approval_manager, temp_dir):
    """Test executing multiple commands"""
    mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")

    executor = ShellExecutor(approval_manager, temp_dir)

    # Execute multiple commands
    for i in range(3):
        success, stdout, stderr = executor.execute(f"echo test{i}")
        assert success is True

    assert mock_run.call_count == 3
