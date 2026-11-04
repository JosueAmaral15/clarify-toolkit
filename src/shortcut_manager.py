#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keyboard Shortcuts Manager for Clarify Application

Defines and manages keyboard shortcuts for common actions.
v2.9.33 - Comprehensive Keyboard Shortcuts System
"""

# pylint: disable=no-name-in-module  # PySide6 has dynamic module structure

from dataclasses import dataclass
import platform
from typing import Dict, List, Tuple
from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from shiboken6 import isValid


class _ShortcutEvents(QObject):
    """GUI-thread notifications for effective shortcut binding changes."""

    changed = Signal()


@dataclass(frozen=True)
class RegisteredShortcut:
    """One deduplicated shortcut currently bound to a live Qt object."""

    action_name: str
    category: str
    label: str
    sequences: tuple[str, ...]
    customized: bool
    enabled: bool


@dataclass(frozen=True)
class _ShortcutBinding:
    action_name: str
    category: str
    label: str
    label_key: str
    managed: bool


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
        "open_set_operations": ("Ctrl+K, Ctrl+Shift+S", "Set Operations"),
        "open_ai_processor": ("Ctrl+Shift+A", "AI Processor"),
        "open_case_converter": ("Ctrl+Shift+C", "Case Converter"),
        "open_advanced_extractor": ("Ctrl+Shift+E", "Advanced Extractor"),
        "open_text_to_json": ("Ctrl+Shift+J", "Text to JSON"),
        "open_placeholder_replacer": ("Ctrl+Shift+P", "Placeholder Replacer"),
        "open_translate": ("Ctrl+Shift+T", "JSON Translate"),
        # Compatibility key retained for existing shortcut customizations.
        "open_file_list": ("Ctrl+Shift+L", "File Searcher"),
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
        # Clarify Editor: File
        "editor.file.open_path": ("Ctrl+Alt+O", "Open file by typed path"),
        "editor.file.open_folder": ("Ctrl+K, Ctrl+O", "Open folder"),
        "editor.file.close_folder": ("Ctrl+K, Ctrl+F", "Close folder"),
        "editor.file.recover_unsaved": ("Ctrl+K, Ctrl+U", "Recover unsaved documents"),
        "editor.file.recovery_retention": ("Ctrl+K, Ctrl+Shift+U", "Set recovery retention"),
        "editor.file.save_temp_note": ("Ctrl+K, Ctrl+T", "Save as temporary note"),
        "editor.file.manage_temp_notes": ("Ctrl+K, Ctrl+M", "Manage temporary notes"),
        "editor.file.temp_note_retention": ("Ctrl+K, Ctrl+Shift+T", "Set temporary-note retention"),
        "editor.file.compare_with_saved": ("Ctrl+K, Ctrl+D", "Compare with saved file"),
        "editor.file.reload_from_disk": ("Ctrl+K, Ctrl+R", "Reload from disk"),
        "editor.file.enable_saving": ("Ctrl+K, Ctrl+E", "Enable saving"),
        "editor.file.export": ("Ctrl+K, Ctrl+X", "Export current document"),
        "editor.file.auto_save": ("Ctrl+K, Ctrl+A", "Toggle auto-save"),
        "editor.file.restore_folder_sessions": ("Ctrl+K, Ctrl+Shift+R", "Toggle folder-session restore"),
        "editor.file.clear_folder_sessions": ("Ctrl+K, Ctrl+Shift+C", "Clear folder sessions"),
        # Clarify Editor: Edit
        "editor.edit.delete": ("Delete", "Delete selection"),
        "editor.edit.select_line": ("Ctrl+Alt+Shift+L", "Select current line"),
        "editor.edit.go_to_line": ("Ctrl+G", "Go to line"),
        "editor.edit.duplicate_line": ("Ctrl+D", "Duplicate line or selection"),
        "editor.edit.toggle_line_comment": ("Ctrl+/", "Toggle line comment"),
        "editor.edit.indent": ("Ctrl+]", "Indent line or selection"),
        "editor.edit.outdent": ("Ctrl+[", "Outdent line or selection"),
        "editor.edit.indent_use_tabs": ("Ctrl+K, Ctrl+Tab", "Toggle tabs for indentation"),
        "editor.edit.indent_width": ("Ctrl+K, Ctrl+I", "Set indentation width"),
        "editor.edit.move_line_up": ("Alt+Up", "Move line or selection up"),
        "editor.edit.move_line_down": ("Alt+Down", "Move line or selection down"),
        "editor.edit.insert_datetime": ("Ctrl+K, Ctrl+5", "Insert date and time"),
        "editor.edit.trim_trailing_spaces": ("Ctrl+K, Ctrl+W", "Trim trailing spaces"),
        # Clarify Editor: View
        "editor.view.show_explorer": ("Ctrl+K, Ctrl+B", "Toggle Editor Explorer"),
        "editor.view.word_wrap": ("Alt+Z", "Toggle word wrap"),
        "editor.view.render_whitespace": ("Ctrl+K, Ctrl+.", "Toggle whitespace rendering"),
        "editor.view.show_line_numbers": ("Ctrl+K, Ctrl+L", "Toggle line numbers"),
    }

    # Additional defaults for actions that conventionally have more than one
    # portable key sequence. A custom shortcut replaces the complete default set.
    SHORTCUT_ALIASES = {
        "redo": ("Ctrl+Shift+Z",),
        "editor.edit.indent": ("Ctrl+I",),
    }

    # OS-specific shortcuts that might conflict (for notification purposes)
    OS_SHORTCUTS = {
        "Linux": [
            "Ctrl+Alt+T",  # Terminal
            "Ctrl+Alt+L",  # Lock screen
            "Alt+F4",  # Close window
            "Super+L",  # Lock
        ],
        "Windows": [
            "Win+L",  # Lock
            "Ctrl+Shift+Esc",  # Task Manager
            "Alt+F4",  # Close window
            "Win+D",  # Show desktop
        ],
        "Darwin": [  # macOS
            "Cmd+Q",  # Quit
            "Cmd+H",  # Hide
            "Cmd+M",  # Minimize
            "Cmd+Space",  # Spotlight
        ],
    }

    # Custom shortcuts (loaded from settings)
    _custom_shortcuts: Dict[str, str] = {}
    _bindings = WeakKeyDictionary()
    _events = _ShortcutEvents()

    @classmethod
    def events(cls) -> _ShortcutEvents:
        """Return the shared GUI-thread notifier for registry consumers."""
        return cls._events

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
    def get_key_sequences(cls, action_name: str) -> List[QKeySequence]:
        """Return every active key sequence for an action."""
        shortcut, _ = cls.get_shortcut(action_name)
        if not shortcut:
            return []
        shortcuts = [shortcut]
        if action_name not in cls._custom_shortcuts:
            shortcuts.extend(cls.SHORTCUT_ALIASES.get(action_name, ()))
        return [QKeySequence(item) for item in shortcuts]

    @classmethod
    def get_description(cls, action_name: str) -> str:
        """Get description for an action."""
        _, description = cls.get_shortcut(action_name)
        return description

    @classmethod
    def add_shortcut_to_action(cls, action: QAction, action_name: str) -> None:
        """Apply and register a managed shortcut on a QAction."""
        cls.register_action(action, action_name)

    @classmethod
    def register_action(
        cls,
        action: QAction,
        action_name: str,
        *,
        category: str | None = None,
        label: str = "",
        label_key: str = "",
        managed: bool | None = None,
    ) -> None:
        """Register a live QAction, optionally managed by the central defaults."""
        if managed is None:
            managed = action_name in cls.SHORTCUTS
        if managed:
            action.setShortcuts(cls.get_key_sequences(action_name))
        cls._register_target(
            action,
            action_name,
            category=category,
            label=label,
            label_key=label_key,
            managed=managed,
        )

    @classmethod
    def register_shortcut(
        cls,
        shortcut: QShortcut,
        action_name: str,
        *,
        category: str | None = None,
        label: str = "",
        label_key: str = "",
        managed: bool | None = None,
    ) -> None:
        """Register a live QShortcut using the same effective registry."""
        if managed is None:
            managed = action_name in cls.SHORTCUTS
        if managed:
            shortcut.setKey(cls.get_key_sequence(action_name))
        cls._register_target(
            shortcut,
            action_name,
            category=category,
            label=label,
            label_key=label_key,
            managed=managed,
        )

    @classmethod
    def _register_target(
        cls,
        target,
        action_name: str,
        *,
        category: str | None,
        label: str,
        label_key: str,
        managed: bool,
    ) -> None:
        binding = _ShortcutBinding(
            action_name=action_name,
            category=category or cls.get_category(action_name),
            label=label,
            label_key=label_key,
            managed=managed,
        )
        is_new = target not in cls._bindings
        cls._bindings[target] = binding
        target.setProperty("clarify_shortcut_action", action_name)
        target.setProperty("clarify_shortcut_category", binding.category)
        if is_new:
            target.destroyed.connect(lambda *_unused: cls._events.changed.emit())
        cls._events.changed.emit()

    @classmethod
    def _refresh_registered_targets(cls) -> None:
        stale = []
        for target, binding in list(cls._bindings.items()):
            if not isValid(target):
                stale.append(target)
                continue
            if not binding.managed:
                continue
            if isinstance(target, QAction):
                target.setShortcuts(cls.get_key_sequences(binding.action_name))
            elif isinstance(target, QShortcut):
                target.setKey(cls.get_key_sequence(binding.action_name))
        for target in stale:
            cls._bindings.pop(target, None)
        cls._events.changed.emit()

    @classmethod
    def get_registered_shortcuts(cls, owner=None) -> List[RegisteredShortcut]:
        """Return deduplicated bindings backed by live Qt objects under owner."""
        registered = {}
        stale = []
        for target, binding in list(cls._bindings.items()):
            if not isValid(target):
                stale.append(target)
                continue
            if owner is not None and not cls._belongs_to(target, owner):
                continue
            try:
                if isinstance(target, QAction):
                    sequences = tuple(
                        sequence.toString(QKeySequence.PortableText)
                        for sequence in target.shortcuts()
                        if not sequence.isEmpty()
                    )
                    label = target.text().replace("&", "") or binding.label
                    enabled = target.isEnabled()
                else:
                    sequence = target.key()
                    sequences = (sequence.toString(QKeySequence.PortableText),) if not sequence.isEmpty() else ()
                    if binding.label_key:
                        from src.i18n import tr  # pylint: disable=import-outside-toplevel

                        label = tr(binding.label_key, binding.label)
                    else:
                        label = binding.label or cls.get_description(binding.action_name)
                    enabled = target.isEnabled()
            except RuntimeError:
                stale.append(target)
                continue
            if not sequences:
                continue
            item = RegisteredShortcut(
                action_name=binding.action_name,
                category=binding.category,
                label=label or binding.action_name,
                sequences=sequences,
                customized=binding.action_name in cls._custom_shortcuts,
                enabled=enabled,
            )
            key = (item.action_name, item.category, item.label, item.sequences)
            registered[key] = item
        for target in stale:
            cls._bindings.pop(target, None)
        return sorted(
            registered.values(),
            key=lambda item: (item.category.casefold(), item.label.casefold()),
        )

    @staticmethod
    def _belongs_to(target, owner) -> bool:
        current = target
        while current is not None:
            if current is owner:
                return True
            try:
                current = current.parent()
            except RuntimeError:
                return False
        return False

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
        cls._refresh_registered_targets()
        return True

    @classmethod
    def reset_custom_shortcut(cls, action_name: str) -> None:
        """Reset shortcut to default."""
        if action_name in cls._custom_shortcuts:
            del cls._custom_shortcuts[action_name]
            cls._refresh_registered_targets()

    @classmethod
    def reset_all_custom_shortcuts(cls) -> None:
        """Reset all shortcuts to defaults."""
        cls._custom_shortcuts.clear()
        cls._refresh_registered_targets()

    @classmethod
    def load_custom_shortcuts(cls, custom_dict: Dict[str, str]) -> None:
        """Load custom shortcuts from settings."""
        cls._custom_shortcuts = custom_dict.copy()
        cls._refresh_registered_targets()

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
        normalized = QKeySequence(key_sequence).toString(QKeySequence.PortableText).lower()
        for action_name in cls.SHORTCUTS:
            active = {
                shortcut.toString(QKeySequence.PortableText).lower() for shortcut in cls.get_key_sequences(action_name)
            }
            if normalized in active:
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
        editor_prefixes = {
            "editor.file.": "Editor File",
            "editor.edit.": "Editor Edit",
            "editor.view.": "Editor View",
        }
        for prefix, category in editor_prefixes.items():
            if action_name.startswith(prefix):
                return category
        categories = {
            "File": ["new_file", "open_file", "save_file", "save_as", "close_tab", "exit"],
            "Edit": ["copy", "paste", "cut", "select_all", "undo", "redo", "find", "replace"],
            "Tools": [
                "open_editor",
                "open_json_search",
                "open_json_rewriter",
                "open_set_operations",
                "open_ai_processor",
                "open_case_converter",
                "open_advanced_extractor",
                "open_text_to_json",
                "open_placeholder_replacer",
                "open_translate",
                "open_file_list",
            ],
            "Navigation": [
                "next_dock",
                "prev_dock",
                "next_dock_dynamic",
                "prev_dock_dynamic",
                "next_file_tab",
                "previous_file_tab",
                "jump_dock_1",
                "jump_dock_2",
                "jump_dock_3",
                "jump_dock_4",
                "jump_dock_5",
                "jump_dock_6",
                "jump_dock_7",
                "jump_dock_8",
                "jump_dock_9",
            ],
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
            "Tools (Docks)": [
                "open_editor",
                "open_json_search",
                "open_json_rewriter",
                "open_set_operations",
                "open_ai_processor",
                "open_case_converter",
                "open_advanced_extractor",
                "open_text_to_json",
                "open_placeholder_replacer",
                "open_translate",
                "open_file_list",
            ],
            "Navigation": [
                "next_dock",
                "prev_dock",
                "next_dock_dynamic",
                "prev_dock_dynamic",
                "next_file_tab",
                "previous_file_tab",
                "jump_dock_1",
                "jump_dock_2",
                "jump_dock_3",
                "jump_dock_4",
                "jump_dock_5",
                "jump_dock_6",
                "jump_dock_7",
                "jump_dock_8",
                "jump_dock_9",
            ],
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
                    if action not in cls._custom_shortcuts:
                        aliases = cls.SHORTCUT_ALIASES.get(action, ())
                        shortcut = " / ".join((shortcut, *aliases))
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
