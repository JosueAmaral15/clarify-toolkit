#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command Pattern Implementation for Undo/Redo System (Task #12 - v2.9.8)

Provides a generic command manager with undo/redo capabilities.
Maintains a history stack with configurable max depth (default: 10 levels).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from collections import deque


class Command(ABC):
    """
    Abstract base class for all commands.
    Each command must implement execute(), undo(), and optionally redo().
    """

    @abstractmethod
    def execute(self) -> None:
        """Execute the command (perform the action)."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command (revert the action)."""

    def redo(self) -> None:
        """Redo the command (re-execute after undo). Default: calls execute()."""
        self.execute()

    def get_description(self) -> str:
        """Return a human-readable description of the command."""
        return self.__class__.__name__


class FileModificationCommand(Command):
    """
    Command for file modification operations.
    Stores file content before and after modification for undo/redo.
    """

    def __init__(self, filepath: str, original_content: str, new_content: str, description: str = "File modification"):
        self.filepath = filepath
        self.original_content = original_content
        self.new_content = new_content
        self.description = description

    def execute(self) -> None:
        """Write new content to file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.new_content)
        except (IOError, OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot write to {self.filepath}: {e}") from e

    def undo(self) -> None:
        """Restore original content."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.original_content)
        except (IOError, OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot restore {self.filepath}: {e}") from e

    def redo(self) -> None:
        """Re-apply new content."""
        self.execute()

    def get_description(self) -> str:
        return f"{self.description}: {self.filepath}"


class MultiFileCommand(Command):
    """
    Command for operations affecting multiple files.
    Aggregates multiple FileModificationCommand instances.
    """

    def __init__(self, commands: List[FileModificationCommand], description: str = "Multi-file operation"):
        self.commands = commands
        self.description = description

    def execute(self) -> None:
        """Execute all sub-commands."""
        for cmd in self.commands:
            cmd.execute()

    def undo(self) -> None:
        """Undo all sub-commands in reverse order."""
        for cmd in reversed(self.commands):
            cmd.undo()

    def redo(self) -> None:
        """Redo all sub-commands."""
        for cmd in self.commands:
            cmd.redo()

    def get_description(self) -> str:
        return f"{self.description} ({len(self.commands)} file(s))"


class CommandManager:
    """
    Manages command history with undo/redo stack.

    Features:
    - Configurable history depth (default: 10)
    - Undo/Redo operations with Ctrl+Z / Ctrl+Y
    - Clear history
    - Get history statistics
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.undo_stack: deque[Command] = deque(maxlen=max_history)
        self.redo_stack: deque[Command] = deque(maxlen=max_history)

    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the undo stack.
        Clears the redo stack since we're making a new change.
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self) -> bool:
        """
        Undo the last command.
        Returns True if undo was successful, False if no commands to undo.
        """
        if not self.undo_stack:
            return False

        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """
        Redo the last undone command.
        Returns True if redo was successful, False if no commands to redo.
        """
        if not self.redo_stack:
            return False

        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        return True

    def can_undo(self) -> bool:
        """Check if there are commands available to undo."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if there are commands available to redo."""
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of the next command to undo."""
        if self.undo_stack:
            return self.undo_stack[-1].get_description()
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of the next command to redo."""
        if self.redo_stack:
            return self.redo_stack[-1].get_description()
        return None

    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_history_stats(self) -> dict:
        """Get statistics about current history state."""
        return {
            'undo_available': len(self.undo_stack),
            'redo_available': len(self.redo_stack),
            'max_history': self.max_history,
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        }
