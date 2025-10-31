"""
Utility functions for CodexCLI
"""

import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path.cwd()


def get_config_dir() -> Path:
    """Get or create the config directory for storing history and context"""
    config_dir = Path.home() / ".codexcli"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_history_file() -> Path:
    """Get the history file path"""
    return get_config_dir() / "history.json"


def get_context_file() -> Path:
    """Get the context file path"""
    return get_config_dir() / "context.json"


def print_info(message: str):
    """Print info message"""
    console.print(f"[cyan]ℹ[/cyan] {message}")


def print_success(message: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message"""
    error_console = Console(stderr=True)
    error_console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_code(code: str, language: str = "python", title: Optional[str] = None):
    """Print code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    if title:
        console.print(Panel(syntax, title=title, border_style="blue"))
    else:
        console.print(syntax)


def print_diff(old_content: str, new_content: str, filename: str):
    """Print a diff between old and new content"""
    import difflib

    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm="",
    )

    diff_text = "".join(diff)
    if diff_text:
        print_code(diff_text, "diff", f"Changes to {filename}")


def confirm(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    from prompt_toolkit import prompt
    from prompt_toolkit.validation import Validator, ValidationError

    class YesNoValidator(Validator):
        def validate(self, document):
            text = document.text.lower()
            if text and text not in ["y", "n", "yes", "no"]:
                raise ValidationError(message="Please enter 'y' or 'n'")

    default_str = "Y/n" if default else "y/N"
    try:
        result = prompt(f"{message} [{default_str}]: ", validator=YesNoValidator())
        if not result:
            return default
        return result.lower() in ["y", "yes"]
    except (KeyboardInterrupt, EOFError):
        return False


def truncate_content(content: str, max_length: int = 1000) -> str:
    """Truncate content if too long"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + f"\n... (truncated, {len(content) - max_length} more characters)"


def is_text_file(filepath: Path) -> bool:
    """Check if a file is a text file"""
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".txt",
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".html",
        ".css",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".sql",
        ".r",
        ".m",
        ".swift",
    }
    return filepath.suffix.lower() in text_extensions


def read_file_safe(filepath: Path, max_size_kb: int = 500) -> Optional[str]:
    """Safely read a file with size limit"""
    try:
        file_size = filepath.stat().st_size / 1024  # KB
        if file_size > max_size_kb:
            print_warning(f"File {filepath} is too large ({file_size:.1f}KB > {max_size_kb}KB)")
            return None

        if not is_text_file(filepath):
            print_warning(f"File {filepath} is not a text file")
            return None

        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        print_error(f"Error reading file {filepath}: {e}")
        return None
