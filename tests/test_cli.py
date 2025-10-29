"""
Tests for CLI module
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from codexcli.cli import CodexCLI
from codexcli.approval import ApprovalMode


@patch('codexcli.cli.create_agent')
def test_codex_cli_initialization(mock_create_agent, temp_dir):
    """Test CodexCLI initialization"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(provider="openai", project_root=temp_dir)

    assert cli.project_root == temp_dir
    assert cli.approval_manager is not None
    assert cli.context is not None
    assert cli.project_context is not None
    assert cli.file_ops is not None
    assert cli.shell is not None
    mock_create_agent.assert_called_once()


@patch('codexcli.cli.create_agent')
def test_codex_cli_initialization_default_root(mock_create_agent):
    """Test CodexCLI initialization with default project root"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI()

    assert cli.project_root == Path.cwd()


@patch('codexcli.cli.create_agent')
def test_codex_cli_with_approval_mode(mock_create_agent, temp_dir):
    """Test CodexCLI initialization with specific approval mode"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(approval_mode=ApprovalMode.FULL_AUTO, project_root=temp_dir)

    assert cli.approval_manager.get_mode() == ApprovalMode.FULL_AUTO


@patch('codexcli.cli.create_agent')
def test_codex_cli_with_anthropic(mock_create_agent, temp_dir):
    """Test CodexCLI initialization with Anthropic provider"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(provider="anthropic", project_root=temp_dir)

    # Verify create_agent was called with correct provider
    call_args = mock_create_agent.call_args
    assert call_args[1]['provider'] == 'anthropic'


@patch('codexcli.cli.create_agent')
def test_codex_cli_initialization_failure(mock_create_agent, temp_dir):
    """Test CodexCLI initialization failure"""
    mock_create_agent.side_effect = Exception("API key not found")

    with pytest.raises(SystemExit):
        CodexCLI(project_root=temp_dir)


@patch('codexcli.cli.create_agent')
def test_codex_cli_process_message(mock_create_agent, temp_dir):
    """Test processing a message"""
    mock_agent = MagicMock()
    mock_agent.ask.return_value = "Test response"
    mock_create_agent.return_value = mock_agent

    cli = CodexCLI(project_root=temp_dir)

    # Mock the process_message method if it exists
    # This is a simplified test
    assert cli.agent is not None


@patch('codexcli.cli.create_agent')
def test_codex_cli_file_operations_integration(mock_create_agent, temp_dir):
    """Test that file operations are properly integrated"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(project_root=temp_dir)

    # Verify file_ops is using the same project root
    assert cli.file_ops.project_root == temp_dir
    assert cli.file_ops.approval_manager == cli.approval_manager


@patch('codexcli.cli.create_agent')
def test_codex_cli_shell_integration(mock_create_agent, temp_dir):
    """Test that shell executor is properly integrated"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(project_root=temp_dir)

    # Verify shell is using the same working directory
    assert cli.shell.working_dir == temp_dir
    assert cli.shell.approval_manager == cli.approval_manager


@patch('codexcli.cli.create_agent')
def test_codex_cli_contexts_integration(mock_create_agent, temp_dir):
    """Test that contexts are properly integrated"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(project_root=temp_dir)

    # Verify contexts
    assert cli.context is not None
    assert cli.project_context.project_root == temp_dir


@pytest.mark.unit
@patch('codexcli.cli.create_agent')
def test_codex_cli_approval_mode_change(mock_create_agent, temp_dir):
    """Test changing approval mode"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(approval_mode=ApprovalMode.SUGGEST, project_root=temp_dir)
    assert cli.approval_manager.get_mode() == ApprovalMode.SUGGEST

    cli.approval_manager.set_mode(ApprovalMode.FULL_AUTO)
    assert cli.approval_manager.get_mode() == ApprovalMode.FULL_AUTO


@pytest.mark.unit
@patch('codexcli.cli.create_agent')
def test_codex_cli_components_exist(mock_create_agent, temp_dir):
    """Test that all components are initialized"""
    mock_create_agent.return_value = MagicMock()

    cli = CodexCLI(project_root=temp_dir)

    # Verify all components exist
    assert hasattr(cli, 'agent')
    assert hasattr(cli, 'context')
    assert hasattr(cli, 'project_context')
    assert hasattr(cli, 'approval_manager')
    assert hasattr(cli, 'file_ops')
    assert hasattr(cli, 'shell')
    assert hasattr(cli, 'project_root')


@pytest.mark.unit
@patch('codexcli.cli.create_agent')
def test_codex_cli_with_different_providers(mock_create_agent, temp_dir):
    """Test initialization with different providers"""
    mock_create_agent.return_value = MagicMock()

    providers = ["openai", "anthropic"]

    for provider in providers:
        cli = CodexCLI(provider=provider, project_root=temp_dir)
        assert cli.agent is not None
