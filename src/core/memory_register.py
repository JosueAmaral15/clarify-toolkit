#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory Register System - Regex Capture & Reuse

Sistema para capturar valores via regex patterns e reutilizá-los
para inserção de chaves/valores em JSON.

Pattern: Memento (GoF) + Command (GoF)
- Armazena estados capturados
- Permite operações com valores capturados

Use Case:
1. User define regex para capturar valores (ex: r'"name": "(.*?)"')
2. Sistema busca matches e armazena em registers ($0, $1, $2, ...)
3. User usa registers para inserir novos campos (ex: "fullName": "$1")

Features:
- Captura múltiplos grupos via regex
- Named registers ($0-$99)
- Register history
- Clear/reset operations
- Export/import registers
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import re
import json
from datetime import datetime


@dataclass
class RegisterEntry:
    """
    Single register entry.

    Attributes:
        index: Register index ($0, $1, etc.)
        value: Captured value
        source_text: Original text where captured
        pattern: Regex pattern used
        timestamp: When captured
    """
    index: int
    value: str
    source_text: str
    pattern: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'index': self.index,
            'value': self.value,
            'source_text': self.source_text[:100],  # Truncate for size
            'pattern': self.pattern,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RegisterEntry:
        """Create from dictionary."""
        return cls(
            index=data['index'],
            value=data['value'],
            source_text=data['source_text'],
            pattern=data['pattern'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class MemoryRegister:
    """
    Memory Register system for regex captures.

    Pattern: Memento (GoF)
    - Stores captured state
    - Allows restoration

    Usage:
        register = MemoryRegister()
        register.capture(text, r'"name": "(.*?)"')
        value = register.get(1)  # Get $1
        register.replace_in_text('"fullName": "$1"')
    """

    def __init__(self, max_registers: int = 100):
        """
        Initialize memory register.

        Args:
            max_registers: Maximum number of registers ($0-$N)
        """
        self.max_registers = max_registers
        self.registers: Dict[int, RegisterEntry] = {}
        self.history: List[List[RegisterEntry]] = []  # History of captures
        self.last_pattern: Optional[str] = None

    def capture(self, text: str, pattern: str, flags: int = 0) -> Tuple[int, List[str]]:
        """
        Capture values from text using regex pattern.

        Args:
            text: Source text to search
            pattern: Regex pattern with capture groups
            flags: Regex flags (re.IGNORECASE, etc.)

        Returns:
            Tuple of (num_captures, captured_values)

        Raises:
            re.error: If pattern is invalid

        Example:
            text = '{"name": "John", "age": 30}'
            num, values = register.capture(text, r'"name": "(.*?)"')
            # num = 1, values = ["John"]
            # $0 = whole match, $1 = "John"
        """
        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            raise re.error(f"Invalid regex pattern: {e}")

        # Find all matches
        matches = compiled.finditer(text)
        captured_values = []

        # Clear current registers
        self.registers.clear()

        # Process matches
        match_count = 0
        for match in matches:
            match_count += 1

            # $0 = whole match
            entry = RegisterEntry(
                index=0,
                value=match.group(0),
                source_text=text,
                pattern=pattern
            )
            self.registers[0] = entry
            captured_values.append(match.group(0))

            # $1, $2, ... = capture groups
            for i, group in enumerate(match.groups(), start=1):
                if i >= self.max_registers:
                    break

                entry = RegisterEntry(
                    index=i,
                    value=group if group is not None else "",
                    source_text=text,
                    pattern=pattern
                )
                self.registers[i] = entry

                if match_count == 1:  # Only add first match groups to values
                    captured_values.append(group if group is not None else "")

        # Store in history
        if self.registers:
            self.history.append(list(self.registers.values()))

        self.last_pattern = pattern

        return (len(self.registers), captured_values)

    def get(self, index: int, default: str = "") -> str:
        """
        Get value from register.

        Args:
            index: Register index (0-99)
            default: Default value if not found

        Returns:
            Register value or default
        """
        entry = self.registers.get(index)
        return entry.value if entry else default

    def get_all(self) -> Dict[int, str]:
        """Get all register values as dict."""
        return {idx: entry.value for idx, entry in self.registers.items()}

    def replace_in_text(self, template: str) -> str:
        """
        Replace $N placeholders in template with register values.

        Args:
            template: Text with $0, $1, ... placeholders

        Returns:
            Text with placeholders replaced

        Example:
            template = '"fullName": "$1"'
            result = register.replace_in_text(template)
            # result = '"fullName": "John"'
        """
        result = template

        # Sort by index descending to avoid replacing $1 before $10
        for idx in sorted(self.registers.keys(), reverse=True):
            placeholder = f"${idx}"
            if placeholder in result:
                result = result.replace(placeholder, self.registers[idx].value)

        return result

    def clear(self):
        """Clear all registers."""
        self.registers.clear()

    def has_registers(self) -> bool:
        """Check if any registers exist."""
        return len(self.registers) > 0

    def get_register_count(self) -> int:
        """Get number of active registers."""
        return len(self.registers)

    def get_history_count(self) -> int:
        """Get number of history entries."""
        return len(self.history)

    def restore_from_history(self, index: int = -1) -> bool:
        """
        Restore registers from history.

        Args:
            index: History index (-1 = last)

        Returns:
            True if restored, False if no history
        """
        if not self.history:
            return False

        try:
            entries = self.history[index]
            self.registers.clear()
            for entry in entries:
                self.registers[entry.index] = entry
            return True
        except IndexError:
            return False

    def export_to_dict(self) -> Dict[str, Any]:
        """Export registers to dictionary (for persistence)."""
        return {
            'registers': [entry.to_dict() for entry in self.registers.values()],
            'last_pattern': self.last_pattern,
            'history_count': len(self.history)
        }

    def import_from_dict(self, data: Dict[str, Any]):
        """Import registers from dictionary."""
        self.registers.clear()
        for entry_dict in data.get('registers', []):
            entry = RegisterEntry.from_dict(entry_dict)
            self.registers[entry.index] = entry

        self.last_pattern = data.get('last_pattern')

    def export_to_json(self) -> str:
        """Export registers to JSON string."""
        return json.dumps(self.export_to_dict(), indent=2)

    def import_from_json(self, json_str: str):
        """Import registers from JSON string."""
        data = json.loads(json_str)
        self.import_from_dict(data)

    def __repr__(self) -> str:
        """String representation."""
        registers_str = ", ".join(f"${idx}={entry.value[:20]}"
                                 for idx, entry in sorted(self.registers.items()))
        return f"MemoryRegister({len(self.registers)} registers: {registers_str})"


# Global singleton instance (optional)
_global_register: Optional[MemoryRegister] = None  # pylint: disable=invalid-name


def get_global_register() -> MemoryRegister:
    """Get global memory register singleton."""
    global _global_register  # pylint: disable=global-statement  # Singleton pattern
    if _global_register is None:
        _global_register = MemoryRegister()
    return _global_register


def reset_global_register():
    """Reset global memory register."""
    global _global_register  # pylint: disable=global-statement  # Singleton pattern
    _global_register = None
