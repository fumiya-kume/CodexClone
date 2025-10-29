"""
Tests for approval module
"""
import pytest
from unittest.mock import patch, MagicMock
from codexcli.approval import ApprovalManager, ApprovalMode, parse_approval_mode


def test_approval_mode_parsing():
    """Test parsing approval mode from string"""
    assert parse_approval_mode("suggest") == ApprovalMode.SUGGEST
    assert parse_approval_mode("auto") == ApprovalMode.AUTO_EDIT
    assert parse_approval_mode("auto_edit") == ApprovalMode.AUTO_EDIT
    assert parse_approval_mode("full") == ApprovalMode.FULL_AUTO
    assert parse_approval_mode("full_auto") == ApprovalMode.FULL_AUTO
    assert parse_approval_mode("invalid") == ApprovalMode.SUGGEST


def test_approval_mode_parsing_case_insensitive():
    """Test that approval mode parsing is case insensitive"""
    assert parse_approval_mode("SUGGEST") == ApprovalMode.SUGGEST
    assert parse_approval_mode("Auto") == ApprovalMode.AUTO_EDIT
    assert parse_approval_mode("FULL_AUTO") == ApprovalMode.FULL_AUTO


def test_approval_manager_initialization():
    """Test ApprovalManager initialization"""
    manager = ApprovalManager()
    assert manager.get_mode() == ApprovalMode.SUGGEST

    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    assert manager.get_mode() == ApprovalMode.FULL_AUTO


def test_approval_manager_set_mode():
    """Test setting approval mode"""
    manager = ApprovalManager()
    manager.set_mode(ApprovalMode.AUTO_EDIT)
    assert manager.get_mode() == ApprovalMode.AUTO_EDIT


def test_file_create_approval_full_auto():
    """Test file creation approval in FULL_AUTO mode"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    approved = manager.request_file_create_approval("test.py", "print('hello')")
    assert approved is True


def test_file_create_approval_auto_edit():
    """Test file creation approval in AUTO_EDIT mode"""
    manager = ApprovalManager(ApprovalMode.AUTO_EDIT)
    approved = manager.request_file_create_approval("test.py", "print('hello')")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=True)
def test_file_create_approval_suggest_approved(mock_confirm):
    """Test file creation approval in SUGGEST mode - approved"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_create_approval("test.py", "print('hello')")
    assert approved is True
    mock_confirm.assert_called_once()


@patch('codexcli.approval.confirm', return_value=False)
def test_file_create_approval_suggest_denied(mock_confirm):
    """Test file creation approval in SUGGEST mode - denied"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_create_approval("test.py", "print('hello')")
    assert approved is False
    mock_confirm.assert_called_once()


def test_file_edit_approval_full_auto():
    """Test file edit approval in FULL_AUTO mode"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    approved = manager.request_file_edit_approval("test.py", "old", "new")
    assert approved is True


def test_file_edit_approval_auto_edit():
    """Test file edit approval in AUTO_EDIT mode"""
    manager = ApprovalManager(ApprovalMode.AUTO_EDIT)
    approved = manager.request_file_edit_approval("test.py", "old", "new")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=True)
def test_file_edit_approval_suggest_approved(mock_confirm):
    """Test file edit approval in SUGGEST mode - approved"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_edit_approval("test.py", "old", "new")
    assert approved is True
    mock_confirm.assert_called_once()


@patch('codexcli.approval.confirm', return_value=False)
def test_file_edit_approval_suggest_denied(mock_confirm):
    """Test file edit approval in SUGGEST mode - denied"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_edit_approval("test.py", "old", "new")
    assert approved is False


def test_file_delete_approval_full_auto():
    """Test file deletion approval in FULL_AUTO mode"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    approved = manager.request_file_delete_approval("test.py")
    assert approved is True


def test_file_delete_approval_auto_edit():
    """Test file deletion approval in AUTO_EDIT mode"""
    manager = ApprovalManager(ApprovalMode.AUTO_EDIT)
    approved = manager.request_file_delete_approval("test.py")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=True)
def test_file_delete_approval_suggest_approved(mock_confirm):
    """Test file deletion approval in SUGGEST mode - approved"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_delete_approval("test.py")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=False)
def test_file_delete_approval_suggest_denied(mock_confirm):
    """Test file deletion approval in SUGGEST mode - denied"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_file_delete_approval("test.py")
    assert approved is False


def test_shell_command_approval_full_auto():
    """Test shell command approval in FULL_AUTO mode"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    approved = manager.request_shell_command_approval("ls -la")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=True)
def test_shell_command_approval_auto_edit(mock_confirm):
    """Test shell command approval in AUTO_EDIT mode - requires confirmation"""
    manager = ApprovalManager(ApprovalMode.AUTO_EDIT)
    approved = manager.request_shell_command_approval("ls -la")
    assert approved is True
    mock_confirm.assert_called_once()


@patch('codexcli.approval.confirm', return_value=True)
def test_shell_command_approval_suggest(mock_confirm):
    """Test shell command approval in SUGGEST mode"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_shell_command_approval("ls -la", "List files")
    assert approved is True


def test_api_call_approval_full_auto():
    """Test API call approval in FULL_AUTO mode"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    approved = manager.request_api_call_approval("openai", "gpt-4", "test prompt")
    assert approved is True


def test_api_call_approval_auto_edit():
    """Test API call approval in AUTO_EDIT mode"""
    manager = ApprovalManager(ApprovalMode.AUTO_EDIT)
    approved = manager.request_api_call_approval("openai", "gpt-4", "test prompt")
    assert approved is True


@patch('codexcli.approval.confirm', return_value=True)
def test_api_call_approval_suggest(mock_confirm):
    """Test API call approval in SUGGEST mode"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    approved = manager.request_api_call_approval("openai", "gpt-4", "test prompt")
    assert approved is True


@pytest.mark.unit
@patch('codexcli.approval.console')
def test_show_mode_info(mock_console):
    """Test showing mode info"""
    manager = ApprovalManager(ApprovalMode.SUGGEST)
    manager.show_mode_info()
    mock_console.print.assert_called()


@pytest.mark.unit
def test_file_create_with_preview_callback():
    """Test file creation with preview callback"""
    manager = ApprovalManager(ApprovalMode.FULL_AUTO)
    preview_called = False

    def preview_callback(content):
        nonlocal preview_called
        preview_called = True

    manager.request_file_create_approval("test.py", "content", preview_callback)
    # In FULL_AUTO mode, preview should not be called
    assert preview_called is False
