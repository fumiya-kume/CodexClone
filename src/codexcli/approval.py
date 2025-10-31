"""
Approval modes and user consent management
"""

from enum import Enum
from typing import Optional, Callable
from .utils import console, confirm, print_info, print_warning


class ApprovalMode(Enum):
    """Approval modes for operations"""

    SUGGEST = "suggest"  # Ask for approval on all operations
    AUTO_EDIT = "auto_edit"  # Auto edit files, ask for shell commands
    FULL_AUTO = "full_auto"  # Fully automated


class ApprovalManager:
    """Manages user approvals for different operations"""

    def __init__(self, mode: ApprovalMode = ApprovalMode.SUGGEST):
        self.mode = mode

    def set_mode(self, mode: ApprovalMode):
        """Set the approval mode"""
        self.mode = mode
        print_info(f"Approval mode set to: {mode.value}")

    def get_mode(self) -> ApprovalMode:
        """Get current approval mode"""
        return self.mode

    def request_file_create_approval(
        self, filepath: str, content: str, preview_callback: Optional[Callable] = None
    ) -> bool:
        """Request approval to create a file"""
        if self.mode == ApprovalMode.FULL_AUTO or self.mode == ApprovalMode.AUTO_EDIT:
            print_info(f"Creating file: {filepath}")
            return True

        console.print(f"\n[bold yellow]File Creation Request[/bold yellow]")
        console.print(f"File: [cyan]{filepath}[/cyan]")

        if preview_callback:
            preview_callback(content)

        return confirm(f"Create this file?", default=False)

    def request_file_edit_approval(
        self,
        filepath: str,
        old_content: str,
        new_content: str,
        preview_callback: Optional[Callable] = None,
    ) -> bool:
        """Request approval to edit a file"""
        if self.mode == ApprovalMode.FULL_AUTO or self.mode == ApprovalMode.AUTO_EDIT:
            print_info(f"Editing file: {filepath}")
            return True

        console.print(f"\n[bold yellow]File Edit Request[/bold yellow]")
        console.print(f"File: [cyan]{filepath}[/cyan]")

        if preview_callback:
            preview_callback(old_content, new_content)

        return confirm(f"Apply these changes?", default=False)

    def request_file_delete_approval(self, filepath: str) -> bool:
        """Request approval to delete a file"""
        if self.mode == ApprovalMode.FULL_AUTO or self.mode == ApprovalMode.AUTO_EDIT:
            print_warning(f"Deleting file: {filepath}")
            return True

        console.print(f"\n[bold red]File Deletion Request[/bold red]")
        console.print(f"File: [cyan]{filepath}[/cyan]")

        return confirm(f"Delete this file? This cannot be undone!", default=False)

    def request_shell_command_approval(
        self, command: str, description: Optional[str] = None
    ) -> bool:
        """Request approval to run a shell command"""
        if self.mode == ApprovalMode.FULL_AUTO:
            print_info(f"Running command: {command}")
            return True

        console.print(f"\n[bold yellow]Shell Command Request[/bold yellow]")
        console.print(f"Command: [cyan]{command}[/cyan]")
        if description:
            console.print(f"Description: {description}")

        return confirm(f"Execute this command?", default=False)

    def request_api_call_approval(self, provider: str, model: str, prompt: str) -> bool:
        """Request approval for API call (mainly for cost awareness)"""
        if self.mode != ApprovalMode.SUGGEST:
            return True

        console.print(f"\n[bold blue]API Call Request[/bold blue]")
        console.print(f"Provider: [cyan]{provider}[/cyan]")
        console.print(f"Model: [cyan]{model}[/cyan]")
        console.print(f"Prompt length: [cyan]{len(prompt)} characters[/cyan]")

        return confirm("Make this API call?", default=True)

    def show_mode_info(self):
        """Display information about current approval mode"""
        mode_descriptions = {
            ApprovalMode.SUGGEST: (
                "Suggest Mode - You will be asked for approval for:\n"
                "  • File creation\n"
                "  • File editing\n"
                "  • File deletion\n"
                "  • Shell command execution\n"
                "  • API calls"
            ),
            ApprovalMode.AUTO_EDIT: (
                "Auto Edit Mode - Automatic approval for:\n"
                "  • File creation\n"
                "  • File editing\n"
                "\nYou will be asked for approval for:\n"
                "  • File deletion\n"
                "  • Shell command execution"
            ),
            ApprovalMode.FULL_AUTO: (
                "Full Auto Mode - All operations are automatic:\n"
                "  • File operations (create, edit, delete)\n"
                "  • Shell command execution\n"
                "  • API calls\n"
                "\n[bold red]Warning: Use with caution![/bold red]"
            ),
        }

        console.print(f"\n[bold]Current Approval Mode:[/bold] {self.mode.value}")
        console.print(mode_descriptions[self.mode])
        console.print()


def parse_approval_mode(mode_str: str) -> ApprovalMode:
    """Parse approval mode from string"""
    mode_map = {
        "suggest": ApprovalMode.SUGGEST,
        "auto": ApprovalMode.AUTO_EDIT,
        "auto_edit": ApprovalMode.AUTO_EDIT,
        "full": ApprovalMode.FULL_AUTO,
        "full_auto": ApprovalMode.FULL_AUTO,
    }
    return mode_map.get(mode_str.lower(), ApprovalMode.SUGGEST)
