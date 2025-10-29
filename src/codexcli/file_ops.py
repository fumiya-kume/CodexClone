"""
File operations (read, create, edit, delete)
"""
import os
from pathlib import Path
from typing import Optional, List
from .utils import (
    print_success,
    print_error,
    print_warning,
    print_diff,
    print_code,
    read_file_safe
)
from .approval import ApprovalManager


class FileOperations:
    """Handles file operations with approval flow"""

    def __init__(self, approval_manager: ApprovalManager, project_root: Optional[Path] = None):
        self.approval_manager = approval_manager
        self.project_root = project_root or Path.cwd()

    def read_file(self, filepath: str) -> Optional[str]:
        """Read a file and return its content"""
        try:
            file_path = self._resolve_path(filepath)
            if not file_path.exists():
                print_error(f"File not found: {filepath}")
                return None

            content = read_file_safe(file_path)
            if content is not None:
                print_success(f"Read file: {filepath}")
            return content

        except Exception as e:
            print_error(f"Error reading file {filepath}: {e}")
            return None

    def create_file(self, filepath: str, content: str) -> bool:
        """Create a new file with content"""
        try:
            file_path = self._resolve_path(filepath)

            if file_path.exists():
                print_warning(f"File already exists: {filepath}")
                return False

            # Request approval
            def preview(content):
                print_code(content, self._get_language(filepath), f"Content of {filepath}")

            approved = self.approval_manager.request_file_create_approval(
                filepath, content, preview
            )

            if not approved:
                print_warning("File creation cancelled")
                return False

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content, encoding='utf-8')
            print_success(f"Created file: {filepath}")
            return True

        except Exception as e:
            print_error(f"Error creating file {filepath}: {e}")
            return False

    def edit_file(self, filepath: str, new_content: str) -> bool:
        """Edit an existing file"""
        try:
            file_path = self._resolve_path(filepath)

            if not file_path.exists():
                print_error(f"File not found: {filepath}")
                return False

            old_content = file_path.read_text(encoding='utf-8')

            # Request approval
            def preview(old, new):
                print_diff(old, new, filepath)

            approved = self.approval_manager.request_file_edit_approval(
                filepath, old_content, new_content, preview
            )

            if not approved:
                print_warning("File edit cancelled")
                return False

            # Write file
            file_path.write_text(new_content, encoding='utf-8')
            print_success(f"Edited file: {filepath}")
            return True

        except Exception as e:
            print_error(f"Error editing file {filepath}: {e}")
            return False

    def delete_file(self, filepath: str) -> bool:
        """Delete a file"""
        try:
            file_path = self._resolve_path(filepath)

            if not file_path.exists():
                print_error(f"File not found: {filepath}")
                return False

            # Request approval
            approved = self.approval_manager.request_file_delete_approval(filepath)

            if not approved:
                print_warning("File deletion cancelled")
                return False

            # Delete file
            file_path.unlink()
            print_success(f"Deleted file: {filepath}")
            return True

        except Exception as e:
            print_error(f"Error deleting file {filepath}: {e}")
            return False

    def list_files(self, pattern: str = "*") -> List[Path]:
        """List files matching a pattern"""
        try:
            files = list(self.project_root.rglob(pattern))
            # Filter out hidden files and directories
            files = [f for f in files if not any(part.startswith('.') for part in f.parts)]
            return sorted(files)
        except Exception as e:
            print_error(f"Error listing files: {e}")
            return []

    def get_file_tree(self, max_depth: int = 3) -> str:
        """Get a tree representation of the project structure"""
        def build_tree(path: Path, prefix: str = "", depth: int = 0) -> List[str]:
            if depth > max_depth:
                return []

            lines = []
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                # Filter out hidden and common ignore patterns
                items = [
                    item for item in items
                    if not item.name.startswith('.') and
                    item.name not in ['node_modules', '__pycache__', 'venv', 'env']
                ]

                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{item.name}")

                    if item.is_dir():
                        extension = "    " if is_last else "│   "
                        lines.extend(build_tree(item, prefix + extension, depth + 1))

            except PermissionError:
                pass

            return lines

        tree_lines = [str(self.project_root)]
        tree_lines.extend(build_tree(self.project_root))
        return "\n".join(tree_lines)

    def _resolve_path(self, filepath: str) -> Path:
        """Resolve a filepath relative to project root"""
        path = Path(filepath)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def _get_language(self, filepath: str) -> str:
        """Get language for syntax highlighting based on file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.sh': 'bash',
            '.bash': 'bash',
        }
        ext = Path(filepath).suffix.lower()
        return ext_map.get(ext, 'text')
