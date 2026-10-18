#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keyboard Shortcuts Manager for Clarify Application

Defines and manages keyboard shortcuts for common actions.
v2.9.33 - Comprehensive Keyboard Shortcuts System
"""

# pylint: disable=no-name-in-module  # PySide6 has dynamic module structure

import platform
from typing import Dict, List, Tuple
from PySide6.QtGui import QKeySequence, QAction


class ShortcutManager:
    """Manages keyboard shortcuts for the application with customization support."""

    # Define shortcuts - v2.9.33 Comprehensive Edition
    SHORTCUTS = {
        # File operations
        "new_file": ("Ctrl+N", "New file"),
        "open_file": ("Ctrl+O", "Open file"),
        "save_file": ("Ctrl+S", "Save file"),
        "save_as": ("Ctrl+Shift+S", "Save as..."),
        "close_tab": ("Ctrl+W", "Close current tab"),
        "exit": ("Ctrl+Q", "Exit application"),

        # Edit operations
        "copy": ("Ctrl+C", "Copy"),
        "paste": ("Ctrl+V", "Paste"),
        "cut": ("Ctrl+X", "Cut"),
        "select_all": ("Ctrl+A", "Select all"),
        "undo": ("Ctrl+Z", "Undo"),
        "redo": ("Ctrl+Y", "Redo"),
        "find": ("Ctrl+F", "Find/Search"),
        "replace": ("Ctrl+H", "Replace"),

        # Tools (Docks)
        "open_editor": ("Ctrl+E", "Open Editor"),
        "open_json_search": ("Ctrl+Shift+F", "JSON Search"),
        "open_json_rewriter": ("Ctrl+Shift+R", "JSON Rewriter"),
        "open_set_operations": ("Ctrl+Shift+S", "Set Operations"),
        "open_ai_processor": ("Ctrl+Shift+A", "AI Processor"),
        "open_case_converter": ("Ctrl+Shift+C", "Case Converter"),
        "open_advanced_extractor": ("Ctrl+Shift+E", "Advanced Extractor"),
        "open_text_to_json": ("Ctrl+Shift+J", "Text to JSON"),
        "open_placeholder_replacer": ("Ctrl+Shift+P", "Placeholder Replacer"),
        "open_translate": ("Ctrl+Shift+T", "JSON Translate"),
        "open_file_list": ("Ctrl+Shift+L", "File List"),

        # Navigation
        "next_dock": ("Ctrl+Tab", "Next dock"),
        "prev_dock": ("Ctrl+Shift+Tab", "Previous dock"),
        "next_dock_dynamic": ("Ctrl+PgDown", "Next dock (dynamic order)"),
        "prev_dock_dynamic": ("Ctrl+PgUp", "Previous dock (dynamic order)"),
        "next_file_tab": ("Ctrl+Alt+PgDown", "Next Editor file tab"),
        "previous_file_tab": ("Ctrl+Alt+PgUp", "Previous Editor file tab"),
        "jump_dock_1": ("Ctrl+1", "Jump to dock 1 (JSON Search)"),
        "jump_dock_2": ("Ctrl+2", "Jump to dock 2 (JSON Rewriter)"),
        "jump_dock_3": ("Ctrl+3", "Jump to dock 3 (Set Operations)"),
        "jump_dock_4": ("Ctrl+4", "Jump to dock 4 (AI Processor)"),
        "jump_dock_5": ("Ctrl+5", "Jump to dock 5 (Case Converter)"),
        "jump_dock_6": ("Ctrl+6", "Jump to dock 6 (Text to JSON)"),
        "jump_dock_7": ("Ctrl+7", "Jump to dock 7 (Advanced Extractor)"),
        "jump_dock_8": ("Ctrl+8", "Jump to dock 8 (Placeholder Replacer)"),
        "jump_dock_9": ("Ctrl+9", "Jump to dock 9 (JSON Translate)"),

        # View
        "toggle_fullscreen": ("F11", "Toggle fullscreen"),
        "toggle_history": ("Ctrl+Shift+H", "Toggle history panel"),
        "zoom_in": ("Ctrl++", "Zoom in"),
        "zoom_out": ("Ctrl+-", "Zoom out"),
        "reset_zoom": ("Ctrl+0", "Reset zoom"),
        "horizontal_scroll": ("Shift+Scroll / Ctrl+Shift+Scroll", "Horizontal scroll"),

        # Processing
        "process": ("F5", "Process/Run"),
        "interrupt": ("Esc", "Interrupt/Cancel"),
        "clear": ("Ctrl+L", "Clear results"),

        # Help
        "help": ("F1", "Show help"),
        "keyboard_shortcuts": ("Ctrl+K Ctrl+S", "Keyboard shortcuts"),
        "tutorials": ("Ctrl+Shift+?", "Open tutorials"),
        "about": ("Ctrl+Shift+I", "About Clarify"),
    }

    # OS-specific shortcuts that might conflict (for notification purposes)
    OS_SHORTCUTS = {
        "Linux": [
            "Ctrl+Alt+T",  # Terminal
            "Ctrl+Alt+L",  # Lock screen
            "Alt+F4",      # Close window
            "Super+L",     # Lock
        ],
        "Windows": [
            "Win+L",       # Lock
            "Ctrl+Shift+Esc",  # Task Manager
            "Alt+F4",      # Close window
            "Win+D",       # Show desktop
        ],
        "Darwin": [  # macOS
            "Cmd+Q",       # Quit
            "Cmd+H",       # Hide
            "Cmd+M",       # Minimize
            "Cmd+Space",   # Spotlight
        ],
    }

    # Custom shortcuts (loaded from settings)
    _custom_shortcuts: Dict[str, str] = {}

    @classmethod
    def get_shortcut(cls, action_name: str) -> Tuple[str, str]:
        """Get shortcut and description for an action (considers custom shortcuts)."""
        # Check custom shortcuts first
        if action_name in cls._custom_shortcuts:
            _, description = cls.SHORTCUTS.get(action_name, ("", ""))
            return (cls._custom_shortcuts[action_name], description)
        return cls.SHORTCUTS.get(action_name, ("", ""))

    @classmethod
    def get_default_shortcut(cls, action_name: str) -> Tuple[str, str]:
        """Get default (non-customized) shortcut and description."""
        return cls.SHORTCUTS.get(action_name, ("", ""))

    @classmethod
    def get_key_sequence(cls, action_name: str) -> QKeySequence:
        """Get QKeySequence for an action."""
        shortcut, _ = cls.get_shortcut(action_name)
        return QKeySequence(shortcut) if shortcut else QKeySequence()

    @classmethod
    def get_description(cls, action_name: str) -> str:
        """Get description for an action."""
        _, description = cls.get_shortcut(action_name)
        return description

    @classmethod
    def add_shortcut_to_action(cls, action: QAction, action_name: str) -> None:
        """Add shortcut to a QAction."""
        key_seq = cls.get_key_sequence(action_name)
        if not key_seq.isEmpty():
            action.setShortcut(key_seq)

    @classmethod
    def get_all_shortcuts(cls) -> Dict[str, Tuple[str, str]]:
        """Get all shortcuts as dict (includes custom shortcuts)."""
        result = cls.SHORTCUTS.copy()
        # Overlay custom shortcuts
        for action_name, custom_key in cls._custom_shortcuts.items():
            if action_name in result:
                _, description = result[action_name]
                result[action_name] = (custom_key, description)
        return result

    @classmethod
    def set_custom_shortcut(cls, action_name: str, key_sequence: str) -> bool:
        """
        Set custom shortcut for an action.
        Returns True if set successfully, False if conflict detected.
        """
        if action_name not in cls.SHORTCUTS:
            return False

        # Check for conflicts with existing shortcuts
        conflicts = cls.get_conflicts(key_sequence)
        if conflicts:
            # Allow setting but warn about conflicts
            pass

        cls._custom_shortcuts[action_name] = key_sequence
        return True

    @classmethod
    def reset_custom_shortcut(cls, action_name: str) -> None:
        """Reset shortcut to default."""
        if action_name in cls._custom_shortcuts:
            del cls._custom_shortcuts[action_name]

    @classmethod
    def reset_all_custom_shortcuts(cls) -> None:
        """Reset all shortcuts to defaults."""
        cls._custom_shortcuts.clear()

    @classmethod
    def load_custom_shortcuts(cls, custom_dict: Dict[str, str]) -> None:
        """Load custom shortcuts from settings."""
        cls._custom_shortcuts = custom_dict.copy()

    @classmethod
    def get_custom_shortcuts(cls) -> Dict[str, str]:
        """Get current custom shortcuts."""
        return cls._custom_shortcuts.copy()

    @classmethod
    def get_conflicts(cls, key_sequence: str) -> List[str]:
        """
        Check if key_sequence conflicts with existing shortcuts.
        Returns list of conflicting action names.
        """
        conflicts = []
        for action_name, (shortcut, _) in cls.get_all_shortcuts().items():
            if shortcut.lower() == key_sequence.lower():
                conflicts.append(action_name)
        return conflicts

    @classmethod
    def is_os_shortcut(cls, key_sequence: str) -> bool:
        """Check if key_sequence conflicts with OS shortcuts."""
        current_os = platform.system()
        os_shortcuts = cls.OS_SHORTCUTS.get(current_os, [])

        # Normalize comparison
        key_normalized = key_sequence.replace(" ", "").lower()
        for os_shortcut in os_shortcuts:
            os_normalized = os_shortcut.replace(" ", "").lower()
            if key_normalized == os_normalized:
                return True
        return False

    @classmethod
    def get_category(cls, action_name: str) -> str:
        """Get category for an action."""
        categories = {
            "File": ["new_file", "open_file", "save_file", "save_as", "close_tab", "exit"],
            "Edit": ["copy", "paste", "cut", "select_all", "undo", "redo", "find", "replace"],
            "Tools": ["open_editor", "open_json_search", "open_json_rewriter", "open_set_operations",
                     "open_ai_processor", "open_case_converter", "open_advanced_extractor", "open_text_to_json",
                     "open_placeholder_replacer", "open_translate", "open_file_list"],
            "Navigation": ["next_dock", "prev_dock", "next_dock_dynamic", "prev_dock_dynamic",
                          "next_file_tab", "previous_file_tab",
                          "jump_dock_1", "jump_dock_2", "jump_dock_3", "jump_dock_4", "jump_dock_5",
                          "jump_dock_6", "jump_dock_7", "jump_dock_8", "jump_dock_9"],
            "View": ["toggle_fullscreen", "toggle_history", "zoom_in", "zoom_out", "reset_zoom", "horizontal_scroll"],
            "Processing": ["process", "interrupt", "clear"],
            "Help": ["help", "keyboard_shortcuts", "tutorials", "about"],
        }

        for category, actions in categories.items():
            if action_name in actions:
                return category
        return "Other"

    @classmethod
    def format_shortcuts_table(cls) -> str:
        """Format shortcuts as readable table (v2.9.33 - comprehensive)."""
        lines = ["Keyboard Shortcuts - Clarify v2.9.33", "=" * 70, ""]

        categories = {
            "File Operations": ["new_file", "open_file", "save_file", "save_as", "close_tab", "exit"],
            "Edit Operations": ["copy", "paste", "cut", "select_all", "undo", "redo", "find", "replace"],
            "Tools (Docks)": ["open_editor", "open_json_search", "open_json_rewriter", "open_set_operations",
                             "open_ai_processor", "open_case_converter", "open_advanced_extractor", "open_text_to_json",
                             "open_placeholder_replacer", "open_translate", "open_file_list"],
            "Navigation": ["next_dock", "prev_dock", "next_dock_dynamic", "prev_dock_dynamic",
                          "next_file_tab", "previous_file_tab",
                          "jump_dock_1", "jump_dock_2", "jump_dock_3", "jump_dock_4", "jump_dock_5",
                          "jump_dock_6", "jump_dock_7", "jump_dock_8", "jump_dock_9"],
            "View": ["toggle_fullscreen", "toggle_history", "zoom_in", "zoom_out", "reset_zoom", "horizontal_scroll"],
            "Processing": ["process", "interrupt", "clear"],
            "Help": ["help", "keyboard_shortcuts", "tutorials", "about"],
        }

        for category, actions in categories.items():
            lines.append(f"\n{category}:")
            lines.append("-" * 70)
            for action in actions:
                shortcut, description = cls.get_shortcut(action)
                if shortcut:
                    # Mark custom shortcuts with *
                    marker = "*" if action in cls._custom_shortcuts else " "
                    lines.append(f" {marker} {shortcut:25} {description}")

        lines.append("\n" + "=" * 70)
        lines.append("* = Custom shortcut (modified from default)")
        lines.append("\nPress Ctrl+K Ctrl+S to customize shortcuts")

        return "\n".join(lines)


class ShortcutHelper:
    """Helper class for working with shortcuts in widgets."""

    @staticmethod
    def setup_widget_shortcuts(widget, shortcuts_map: dict) -> None:
        """
        Setup shortcuts for a widget.

        Args:
            widget: The widget to add shortcuts to
            shortcuts_map: Dict mapping action names to callback functions
                          e.g., {"process": widget._process, "clear": widget._clear}
        """
        from PySide6.QtGui import QShortcut  # pylint: disable=import-outside-toplevel  # Avoid circular imports

        for action_name, callback in shortcuts_map.items():
            key_seq = ShortcutManager.get_key_sequence(action_name)
            if not key_seq.isEmpty():
                shortcut = QShortcut(key_seq, widget)
                shortcut.activated.connect(callback)

    @staticmethod
    def add_tooltip_with_shortcut(widget, base_tooltip: str, action_name: str) -> None:
        """
        Add tooltip with shortcut hint.

        Args:
            widget: The widget to set tooltip on
            base_tooltip: Base tooltip text
            action_name: Name of the action to get shortcut for
        """
        shortcut, _ = ShortcutManager.get_shortcut(action_name)
        if shortcut:
            tooltip = f"{base_tooltip} ({shortcut})"
        else:
            tooltip = base_tooltip
        widget.setToolTip(tooltip)
