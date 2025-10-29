"""
Tests for approval module
"""
import pytest
from codexcli.approval import ApprovalManager, ApprovalMode, parse_approval_mode


def test_approval_mode_parsing():
    """Test parsing approval mode from string"""
    assert parse_approval_mode("suggest") == ApprovalMode.SUGGEST
    assert parse_approval_mode("auto") == ApprovalMode.AUTO_EDIT
    assert parse_approval_mode("auto_edit") == ApprovalMode.AUTO_EDIT
    assert parse_approval_mode("full") == ApprovalMode.FULL_AUTO
    assert parse_approval_mode("full_auto") == ApprovalMode.FULL_AUTO
    assert parse_approval_mode("invalid") == ApprovalMode.SUGGEST


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
