#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keyboard Shortcuts Manager for Clarify Application

Defines and manages keyboard shortcuts for common actions.
Sprint 8 - v1.1.0 Features
"""

from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtCore import Qt


class ShortcutManager:
    """Manages keyboard shortcuts for the application."""
    
    # Define shortcuts
    SHORTCUTS = {
        # File operations
        "open_file": ("Ctrl+O", "Open file"),
        "save_file": ("Ctrl+S", "Save file"),
        "save_as": ("Ctrl+Shift+S", "Save as..."),
        "exit": ("Ctrl+Q", "Exit application"),
        
        # Edit operations
        "copy": ("Ctrl+C", "Copy"),
        "paste": ("Ctrl+V", "Paste"),
        "cut": ("Ctrl+X", "Cut"),
        "select_all": ("Ctrl+A", "Select all"),
        "undo": ("Ctrl+Z", "Undo"),
        "redo": ("Ctrl+Shift+Z", "Redo"),
        
        # Processing
        "process": ("F5", "Process/Run"),
        "interrupt": ("Esc", "Interrupt/Cancel"),
        "clear": ("Ctrl+L", "Clear results"),
        
        # View
        "toggle_fullscreen": ("F11", "Toggle fullscreen"),
        "zoom_in": ("Ctrl++", "Zoom in"),
        "zoom_out": ("Ctrl+-", "Zoom out"),
        "reset_zoom": ("Ctrl+0", "Reset zoom"),
        
        # Navigation
        "next_dock": ("Ctrl+Tab", "Next dock"),
        "prev_dock": ("Ctrl+Shift+Tab", "Previous dock"),
        "focus_search": ("Ctrl+F", "Focus search"),
        
        # Help
        "help": ("F1", "Show help"),
        "about": ("Ctrl+H", "About Clarify"),
    }
    
    @classmethod
    def get_shortcut(cls, action_name: str) -> tuple[str, str]:
        """Get shortcut and description for an action."""
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
    def get_all_shortcuts(cls) -> dict:
        """Get all shortcuts as dict."""
        return cls.SHORTCUTS.copy()
    
    @classmethod
    def format_shortcuts_table(cls) -> str:
        """Format shortcuts as readable table."""
        lines = ["Keyboard Shortcuts", "=" * 60, ""]
        
        categories = {
            "File Operations": ["open_file", "save_file", "save_as", "exit"],
            "Edit Operations": ["copy", "paste", "cut", "select_all", "undo", "redo"],
            "Processing": ["process", "interrupt", "clear"],
            "View": ["toggle_fullscreen", "zoom_in", "zoom_out", "reset_zoom"],
            "Navigation": ["next_dock", "prev_dock", "focus_search"],
            "Help": ["help", "about"],
        }
        
        for category, actions in categories.items():
            lines.append(f"\n{category}:")
            lines.append("-" * 60)
            for action in actions:
                shortcut, description = cls.get_shortcut(action)
                if shortcut:
                    lines.append(f"  {shortcut:20} {description}")
        
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
        from PySide6.QtGui import QShortcut
        
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
