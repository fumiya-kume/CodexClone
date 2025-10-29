"""
Shell command execution
"""
import subprocess
import shlex
from typing import Optional, Tuple
from pathlib import Path
from .utils import print_success, print_error, print_info, console
from .approval import ApprovalManager


class ShellExecutor:
    """Executes shell commands with approval"""

    def __init__(self, approval_manager: ApprovalManager, working_dir: Optional[Path] = None):
        self.approval_manager = approval_manager
        self.working_dir = working_dir or Path.cwd()

    def execute(
        self,
        command: str,
        description: Optional[str] = None,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Execute a shell command

        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        # Request approval
        approved = self.approval_manager.request_shell_command_approval(command, description)

        if not approved:
            return False, "", "Command execution cancelled by user"

        try:
            print_info(f"Executing: {command}")

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode == 0:
                print_success(f"Command completed successfully")
                if stdout:
                    console.print("\n[bold]Output:[/bold]")
                    console.print(stdout)
                return True, stdout, stderr
            else:
                print_error(f"Command failed with exit code {result.returncode}")
                if stderr:
                    console.print("\n[bold red]Error:[/bold red]")
                    console.print(stderr)
                return False, stdout, stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            print_error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error executing command: {e}"
            print_error(error_msg)
            return False, "", error_msg

    def execute_safe(self, command: str, description: Optional[str] = None) -> bool:
        """
        Execute a command and return only success status

        Returns:
            bool: True if command succeeded
        """
        success, _, _ = self.execute(command, description)
        return success

    def get_output(self, command: str, description: Optional[str] = None) -> Optional[str]:
        """
        Execute a command and return its output

        Returns:
            str: Command output if successful, None otherwise
        """
        success, stdout, _ = self.execute(command, description)
        return stdout if success else None

    def is_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            result = subprocess.run(
                f"command -v {shlex.quote(command)}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
