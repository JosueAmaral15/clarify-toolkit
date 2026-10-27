#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Keyboard Shortcuts System (v2.9.33)
Tests ShortcutManager, custom shortcuts, conflict detection, and OS warnings.

NOTE: ShortcutManager API returns tuples:
- get_shortcut(action) -> (shortcut_str, description)
- get_default_shortcut(action) -> (shortcut_str, description)
"""

import os
import platform

# Test ShortcutManager independently
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shortcut_manager import ShortcutManager


class TestShortcutManager(unittest.TestCase):
    """Test ShortcutManager functionality."""

    def setUp(self):
        """Reset ShortcutManager before each test."""
        ShortcutManager._custom_shortcuts = {}

    def tearDown(self):
        """Clean up after each test."""
        ShortcutManager._custom_shortcuts = {}

    def test_default_shortcuts_exist(self):
        """Test that all default shortcuts are defined."""
        # File menu
        self.assertIn("open_editor", ShortcutManager.SHORTCUTS)
        self.assertIn("new_file", ShortcutManager.SHORTCUTS)
        self.assertIn("save_file", ShortcutManager.SHORTCUTS)

        # Edit menu
        self.assertIn("undo", ShortcutManager.SHORTCUTS)
        self.assertIn("redo", ShortcutManager.SHORTCUTS)

        # Tools menu
        self.assertIn("open_json_search", ShortcutManager.SHORTCUTS)
        self.assertIn("open_ai_processor", ShortcutManager.SHORTCUTS)
        self.assertIn("open_advanced_extractor", ShortcutManager.SHORTCUTS)
        self.assertNotIn("open_text_extractor", ShortcutManager.SHORTCUTS)

        # Navigation
        self.assertIn("next_dock", ShortcutManager.SHORTCUTS)
        self.assertIn("jump_dock_1", ShortcutManager.SHORTCUTS)

        # Should have at least 40 shortcuts
        self.assertGreaterEqual(len(ShortcutManager.SHORTCUTS), 40)

    def test_get_default_shortcut(self):
        """Test getting default shortcuts."""
        shortcut, desc = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+Z")
        self.assertEqual(desc, "Undo")

        shortcut, _ = ShortcutManager.get_shortcut("redo")
        self.assertEqual(shortcut, "Ctrl+Y")

        shortcut, _ = ShortcutManager.get_shortcut("save_file")
        self.assertEqual(shortcut, "Ctrl+S")

    def test_get_nonexistent_shortcut(self):
        """Test getting a non-existent shortcut returns empty tuple."""
        shortcut, desc = ShortcutManager.get_shortcut("nonexistent_action")
        self.assertEqual(shortcut, "")
        self.assertEqual(desc, "")

    def test_set_custom_shortcut(self):
        """Test setting a custom shortcut."""
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+U")
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+U")

    def test_custom_shortcut_overrides_default(self):
        """Test that custom shortcuts override defaults."""
        default, _ = ShortcutManager.get_default_shortcut("redo")
        self.assertEqual(default, "Ctrl+Y")

        ShortcutManager.set_custom_shortcut("redo", "Ctrl+R")
        custom, _ = ShortcutManager.get_shortcut("redo")
        self.assertEqual(custom, "Ctrl+R")

        # Default should still be the same
        default_after, _ = ShortcutManager.get_default_shortcut("redo")
        self.assertEqual(default_after, "Ctrl+Y")

    def test_reset_custom_shortcut(self):
        """Test resetting a custom shortcut to default."""
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+U")
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+U")

        ShortcutManager.reset_custom_shortcut("undo")
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+Z")

    def test_load_custom_shortcuts(self):
        """Test loading multiple custom shortcuts."""
        custom_dict = {"undo": "Ctrl+U", "redo": "Ctrl+R", "save_file": "Ctrl+W"}

        ShortcutManager.load_custom_shortcuts(custom_dict)

        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+U")
        shortcut, _ = ShortcutManager.get_shortcut("redo")
        self.assertEqual(shortcut, "Ctrl+R")
        shortcut, _ = ShortcutManager.get_shortcut("save_file")
        self.assertEqual(shortcut, "Ctrl+W")

    def test_get_conflicts_no_conflicts(self):
        """Test conflict detection when there are no conflicts."""
        conflicts = ShortcutManager.get_conflicts("Ctrl+Alt+Shift+F12")
        # This sequence is intentionally absent from the defaults.
        self.assertEqual(conflicts, [])

    def test_get_conflicts_with_conflict(self):
        """Test conflict detection when there is a conflict."""
        # Ctrl+Z is used by undo
        conflicts = ShortcutManager.get_conflicts("Ctrl+Z")
        self.assertIn("undo", conflicts)

    def test_get_conflicts_multiple(self):
        """Test detecting multiple conflicts."""
        # Set two actions to the same shortcut
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+Alt+Shift+F12")
        ShortcutManager.set_custom_shortcut("redo", "Ctrl+Alt+Shift+F12")

        conflicts = ShortcutManager.get_conflicts("Ctrl+Alt+Shift+F12")
        self.assertIn("undo", conflicts)
        self.assertIn("redo", conflicts)

    def test_is_os_shortcut_linux(self):
        """Test OS shortcut detection for Linux."""
        if platform.system() == "Linux":
            # Common Linux shortcuts
            self.assertTrue(ShortcutManager.is_os_shortcut("Ctrl+Alt+T"))
            self.assertTrue(ShortcutManager.is_os_shortcut("Alt+F4"))

            # Not an OS shortcut
            self.assertFalse(ShortcutManager.is_os_shortcut("Ctrl+G"))

    def test_is_os_shortcut_windows(self):
        """Test OS shortcut detection for Windows."""
        if platform.system() == "Windows":
            # Common Windows shortcuts
            self.assertTrue(ShortcutManager.is_os_shortcut("Win+D"))
            self.assertTrue(ShortcutManager.is_os_shortcut("Alt+Tab"))

            # Not an OS shortcut
            self.assertFalse(ShortcutManager.is_os_shortcut("Ctrl+G"))

    def test_is_os_shortcut_macos(self):
        """Test OS shortcut detection for macOS."""
        if platform.system() == "Darwin":
            # Common macOS shortcuts
            self.assertTrue(ShortcutManager.is_os_shortcut("Cmd+Space"))
            self.assertTrue(ShortcutManager.is_os_shortcut("Cmd+Tab"))

            # Not an OS shortcut
            self.assertFalse(ShortcutManager.is_os_shortcut("Ctrl+G"))

    def test_get_category(self):
        """Test getting category for actions."""
        # Note: categories are based on ShortcutManager implementation
        self.assertEqual(ShortcutManager.get_category("undo"), "Edit")
        self.assertEqual(ShortcutManager.get_category("open_json_search"), "Tools")
        self.assertEqual(ShortcutManager.get_category("next_dock"), "Navigation")
        self.assertEqual(ShortcutManager.get_category("toggle_history"), "View")
        self.assertEqual(ShortcutManager.get_category("process"), "Processing")
        self.assertEqual(ShortcutManager.get_category("help"), "Help")

    def test_format_shortcuts_table(self):
        """Test formatting shortcuts table."""
        table = ShortcutManager.format_shortcuts_table()

        # Should contain category headers
        self.assertIn("File Operations", table)
        self.assertIn("Edit Operations", table)
        self.assertIn("Navigation", table)

        # Should contain some shortcuts
        self.assertIn("Ctrl+Z", table)
        self.assertIn("Ctrl+Y", table)
        self.assertIn("Ctrl+S", table)

    def test_format_shortcuts_table_with_custom(self):
        """Test that custom shortcuts are marked with (*)."""
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+U")
        table = ShortcutManager.format_shortcuts_table()

        # Custom shortcut should be marked with * prefix
        self.assertIn("* Ctrl+U", table)

    def test_empty_custom_shortcuts_dict(self):
        """Test loading empty custom shortcuts dict."""
        ShortcutManager.load_custom_shortcuts({})

        # Should still have default shortcuts
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+Z")

    def test_invalid_action_name(self):
        """Test setting custom shortcut for invalid action."""
        # Should not raise exception
        ShortcutManager.set_custom_shortcut("nonexistent_action", "Ctrl+G")

        # Should still return empty (not in SHORTCUTS)
        shortcut, desc = ShortcutManager.get_shortcut("nonexistent_action")
        self.assertEqual(shortcut, "")

    def test_all_navigation_shortcuts(self):
        """Test that all navigation shortcuts (Ctrl+1-9, Tab, PageUp/PageDown) exist."""
        # Ctrl+Tab navigation (uses next_dock/prev_dock)
        self.assertIn("next_dock", ShortcutManager.SHORTCUTS)
        self.assertIn("prev_dock", ShortcutManager.SHORTCUTS)

        # Ctrl+PageUp/PageDown navigation (uses next_dock_dynamic/prev_dock_dynamic)
        self.assertIn("next_dock_dynamic", ShortcutManager.SHORTCUTS)
        self.assertIn("prev_dock_dynamic", ShortcutManager.SHORTCUTS)

        # Ctrl+1-9 shortcuts (uses jump_dock_1 through jump_dock_9)
        for i in range(1, 10):
            action = f"jump_dock_{i}"
            self.assertIn(action, ShortcutManager.SHORTCUTS)

    def test_fullscreen_shortcut(self):
        """Test that fullscreen shortcut exists."""
        self.assertIn("toggle_fullscreen", ShortcutManager.SHORTCUTS)
        shortcut, _ = ShortcutManager.get_shortcut("toggle_fullscreen")
        self.assertEqual(shortcut, "F11")


class TestShortcutManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Reset ShortcutManager before each test."""
        ShortcutManager._custom_shortcuts = {}

    def tearDown(self):
        """Clean up after each test."""
        ShortcutManager._custom_shortcuts = {}

    def test_unicode_shortcuts(self):
        """Test that unicode characters don't break the system."""
        # Should not raise exception
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+Ñ")

        # Should retrieve correctly
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+Ñ")

    def test_empty_shortcut_string(self):
        """Test setting empty shortcut string."""
        ShortcutManager.set_custom_shortcut("undo", "")

        # Should return empty string
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "")

    def test_none_shortcut_handling(self):
        """Test that None shortcuts are handled gracefully."""
        # Setting None should be handled without crashing
        try:
            ShortcutManager.set_custom_shortcut("undo", None)
            # If it doesn't raise, check conflicts handles None
            conflicts = ShortcutManager.get_conflicts(None)
        except (AttributeError, TypeError):
            # Expected - None is not a valid shortcut
            pass

    def test_very_long_shortcut_combination(self):
        """Test handling of complex shortcut combinations."""
        complex_shortcut = "Ctrl+Shift+Alt+Meta+F12"
        ShortcutManager.set_custom_shortcut("undo", complex_shortcut)

        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, complex_shortcut)

    def test_load_malformed_custom_shortcuts(self):
        """Test loading custom shortcuts with invalid data."""
        # Should not crash - handle None gracefully
        try:
            ShortcutManager.load_custom_shortcuts(None)
        except AttributeError:
            # Expected - None doesn't have .copy()
            pass

        # After error, should still have defaults
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+Z")

    def test_load_custom_shortcuts_with_safety(self):
        """Test safe loading of custom shortcuts."""
        # Load valid dict
        ShortcutManager.load_custom_shortcuts({"undo": "Ctrl+U"})
        shortcut, _ = ShortcutManager.get_shortcut("undo")
        self.assertEqual(shortcut, "Ctrl+U")


if __name__ == "__main__":
    unittest.main()
