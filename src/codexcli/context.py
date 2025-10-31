"""
Context and conversation history management
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from .utils import get_history_file, get_context_file


@dataclass
class Message:
    """Represents a single message in the conversation"""

    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: str
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(**data)


class ConversationContext:
    """Manages conversation context and history"""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[Message] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.context_file = get_context_file()
        self.history_file = get_history_file()
        self._load_context()

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        self.messages.append(message)

        # Keep only the last max_history messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

        self._save_context()

    def add_user_message(self, content: str):
        """Add a user message"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        """Add an assistant message"""
        self.add_message("assistant", content, metadata)

    def add_system_message(self, content: str):
        """Add a system message"""
        self.add_message("system", content)

    def get_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages

    def get_messages_for_api(self) -> List[Dict]:
        """Get messages formatted for API calls"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self._save_context()

    def _save_context(self):
        """Save context to file"""
        try:
            data = {
                "session_id": self.session_id,
                "messages": [msg.to_dict() for msg in self.messages],
                "last_updated": datetime.now().isoformat(),
            }
            self.context_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Warning: Could not save context: {e}")

    def _load_context(self):
        """Load context from file"""
        try:
            if self.context_file.exists():
                data = json.loads(self.context_file.read_text())
                self.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        except Exception:
            # If loading fails, start with empty context
            self.messages = []

    def save_to_history(self):
        """Save the current session to permanent history"""
        try:
            history = []
            if self.history_file.exists():
                history = json.loads(self.history_file.read_text())

            history.append(
                {
                    "session_id": self.session_id,
                    "messages": [msg.to_dict() for msg in self.messages],
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Keep only last 100 sessions
            history = history[-100:]

            self.history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            print(f"Warning: Could not save to history: {e}")

    def get_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.messages:
            return "No conversation history"

        summary = f"Session: {self.session_id}\n"
        summary += f"Messages: {len(self.messages)}\n"
        summary += f"Last updated: {self.messages[-1].timestamp if self.messages else 'N/A'}"
        return summary


class ProjectContext:
    """Manages project-specific context"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_context: Dict[str, str] = {}
        self.relevant_files: List[Path] = []

    def add_file(self, filepath: Path, content: Optional[str] = None):
        """Add a file to the context"""
        if filepath.exists():
            if content is None:
                try:
                    content = filepath.read_text(encoding="utf-8")
                except Exception:
                    content = "[Binary or unreadable file]"

            relative_path = str(filepath.relative_to(self.project_root))
            self.files_context[relative_path] = content
            if filepath not in self.relevant_files:
                self.relevant_files.append(filepath)

    def get_context_summary(self) -> str:
        """Get a summary of the project context"""
        summary = f"Project: {self.project_root.name}\n"
        summary += f"Files in context: {len(self.files_context)}\n"
        if self.relevant_files:
            summary += "Recent files:\n"
            for file in self.relevant_files[-5:]:
                summary += f"  - {file.relative_to(self.project_root)}\n"
        return summary

    def get_files_content(self) -> str:
        """Get formatted content of all files in context"""
        if not self.files_context:
            return ""

        content = "=== Project Files Context ===\n\n"
        for filepath, file_content in self.files_context.items():
            content += f"File: {filepath}\n"
            content += f"{'=' * 80}\n"
            content += file_content
            content += f"\n{'=' * 80}\n\n"
        return content
