#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for ShortcutsDialog (v2.9.33)
Tests dialog UI, editing, validation, and conflict detection.
"""

import os
import sys
import unittest

# Setup path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from gui.shortcuts_dialog import ShortcutsDialog
    from shortcut_manager import ShortcutManager

    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


@unittest.skipIf(not PYSIDE_AVAILABLE, "PySide6 not available")
class TestShortcutsDialog(unittest.TestCase):
    """Test ShortcutsDialog UI and functionality."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Create dialog for each test."""
        ShortcutManager._custom_shortcuts = {}
        self.dialog = ShortcutsDialog()

    def tearDown(self):
        """Clean up dialog after each test."""
        self.dialog.close()
        self.dialog.deleteLater()
        ShortcutManager._custom_shortcuts = {}

    def test_dialog_creation(self):
        """Test that dialog is created successfully."""
        self.assertIsNotNone(self.dialog)
        self.assertEqual(self.dialog.windowTitle(), "Keyboard Shortcuts")

    def test_dialog_has_table(self):
        """Test that dialog contains a table widget."""
        self.assertIsNotNone(self.dialog.table)

        # Table should have 4 columns
        self.assertEqual(self.dialog.table.columnCount(), 4)

        # Table should have rows (at least 40 shortcuts)
        self.assertGreaterEqual(self.dialog.table.rowCount(), 40)

    def test_table_headers(self):
        """Test that table has correct headers."""
        headers = []
        for col in range(self.dialog.table.columnCount()):
            header = self.dialog.table.horizontalHeaderItem(col)
            headers.append(header.text() if header else "")

        self.assertEqual(headers[0], "Category")
        self.assertEqual(headers[1], "Action")
        self.assertEqual(headers[2], "Shortcut")
        self.assertEqual(headers[3], "Description")

    def test_table_populated(self):
        """Test that table is populated with shortcuts."""
        # Check first few rows have content
        for row in range(min(5, self.dialog.table.rowCount())):
            category_item = self.dialog.table.item(row, 0)
            action_item = self.dialog.table.item(row, 1)
            shortcut_item = self.dialog.table.item(row, 2)

            self.assertIsNotNone(category_item)
            self.assertIsNotNone(action_item)
            self.assertIsNotNone(shortcut_item)

            self.assertNotEqual(category_item.text(), "")
            self.assertNotEqual(action_item.text(), "")

    def test_search_filter(self):
        """Test search functionality."""
        initial_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Search for "undo"
        self.dialog.search_box.setText("undo")
        self.dialog._filter_shortcuts("undo")

        filtered_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Should have fewer visible rows
        self.assertLess(filtered_visible, initial_visible)
        self.assertGreater(filtered_visible, 0)  # At least "undo" should be visible

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        # Search lowercase
        self.dialog.search_box.setText("undo")
        self.dialog._filter_shortcuts("undo")
        lowercase_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Clear and search uppercase
        self.dialog.search_box.setText("")
        self.dialog._filter_shortcuts("")

        self.dialog.search_box.setText("UNDO")
        self.dialog._filter_shortcuts("UNDO")
        uppercase_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Should return same results
        self.assertEqual(lowercase_visible, uppercase_visible)

    def test_search_clear(self):
        """Test clearing search shows all rows."""
        # Filter first
        self.dialog.search_box.setText("undo")
        self.dialog._filter_shortcuts("undo")

        filtered_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Clear search
        self.dialog.search_box.setText("")
        self.dialog._filter_shortcuts("")

        all_visible = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Should show more rows after clearing
        self.assertGreater(all_visible, filtered_visible)

    def test_pending_changes_tracking(self):
        """Test that pending changes are tracked."""
        self.assertEqual(len(self.dialog._pending_changes), 0)

        # Simulate a change
        self.dialog._pending_changes["undo"] = "Ctrl+U"

        self.assertEqual(len(self.dialog._pending_changes), 1)
        self.assertEqual(self.dialog._pending_changes["undo"], "Ctrl+U")

    def test_reset_selected_button_exists(self):
        """Test that reset selected button exists."""
        self.assertIsNotNone(self.dialog.btn_reset_selected)
        self.assertEqual(self.dialog.btn_reset_selected.text(), "Reset Selected")

    def test_reset_all_button_exists(self):
        """Test that reset all button exists."""
        self.assertIsNotNone(self.dialog.btn_reset_all)
        self.assertEqual(self.dialog.btn_reset_all.text(), "Reset All")

    def test_save_button_exists(self):
        """Test that save button exists."""
        self.assertIsNotNone(self.dialog.btn_save)
        self.assertEqual(self.dialog.btn_save.text(), "Save Changes")

    def test_cancel_button_exists(self):
        """Test that cancel button exists."""
        self.assertIsNotNone(self.dialog.btn_cancel)
        self.assertEqual(self.dialog.btn_cancel.text(), "Cancel")

    def test_cancel_closes_dialog(self):
        """Test that cancel button closes dialog."""
        self.dialog.show()
        self.assertTrue(self.dialog.isVisible())

        # Click cancel
        QTest.mouseClick(self.dialog.btn_cancel, Qt.LeftButton)

        # Dialog should be closed
        self.assertFalse(self.dialog.isVisible())

    def test_shortcuts_changed_signal_exists(self):
        """Test that shortcuts_changed signal exists."""
        self.assertTrue(hasattr(self.dialog, "shortcuts_changed"))

    def test_find_action_in_table(self):
        """Test finding specific action in table."""
        found = False
        undo_row = -1

        for row in range(self.dialog.table.rowCount()):
            action_item = self.dialog.table.item(row, 1)
            if action_item and action_item.text() == "undo":
                found = True
                undo_row = row
                break

        self.assertTrue(found, "Action 'undo' not found in table")
        self.assertGreaterEqual(undo_row, 0)

        # Check shortcut is correct
        shortcut_item = self.dialog.table.item(undo_row, 2)
        self.assertEqual(shortcut_item.text(), "Ctrl+Z")

    def test_custom_shortcuts_highlighted(self):
        """Test that custom shortcuts are highlighted in yellow."""
        # Set a custom shortcut
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+U")

        # Reload dialog
        self.dialog.close()
        self.dialog = ShortcutsDialog()

        # Find undo row
        for row in range(self.dialog.table.rowCount()):
            action_item = self.dialog.table.item(row, 1)
            if action_item and action_item.text() == "undo":
                shortcut_item = self.dialog.table.item(row, 2)

                # Should be highlighted in yellow
                bg_color = shortcut_item.background().color()
                # Yellow-ish color (RGB close to 255, 255, 200)
                self.assertGreater(bg_color.red(), 200)
                self.assertGreater(bg_color.green(), 200)
                break

    def test_validate_shortcut_no_conflict(self):
        """Test validation of shortcut without conflicts."""
        # Ctrl+K is not used by default
        result = self.dialog._validate_shortcut("undo", "Ctrl+K")

        # Should return True (no conflicts)
        self.assertTrue(result)

    def test_dialog_modal(self):
        """Test that dialog is modal."""
        self.assertTrue(self.dialog.isModal())

    def test_table_read_only_columns(self):
        """Test that category, action, and description columns are read-only."""
        # Category column (0) should not be editable
        item = self.dialog.table.item(0, 0)
        if item:
            flags = item.flags()
            self.assertFalse(flags & Qt.ItemIsEditable)

        # Action column (1) should not be editable
        item = self.dialog.table.item(0, 1)
        if item:
            flags = item.flags()
            self.assertFalse(flags & Qt.ItemIsEditable)


@unittest.skipIf(not PYSIDE_AVAILABLE, "PySide6 not available")
class TestShortcutsDialogIntegration(unittest.TestCase):
    """Integration tests for ShortcutsDialog."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Create dialog for each test."""
        ShortcutManager._custom_shortcuts = {}
        self.dialog = ShortcutsDialog()

    def tearDown(self):
        """Clean up dialog after each test."""
        self.dialog.close()
        self.dialog.deleteLater()
        ShortcutManager._custom_shortcuts = {}

    def test_load_with_custom_shortcuts(self):
        """Test loading dialog with existing custom shortcuts."""
        # Set some custom shortcuts
        ShortcutManager.set_custom_shortcut("undo", "Ctrl+U")
        ShortcutManager.set_custom_shortcut("redo", "Ctrl+R")

        # Create new dialog
        dialog = ShortcutsDialog()

        # Find undo and redo in table
        undo_found = False
        redo_found = False

        for row in range(dialog.table.rowCount()):
            action_item = dialog.table.item(row, 1)
            shortcut_item = dialog.table.item(row, 2)

            if action_item.text() == "undo":
                self.assertEqual(shortcut_item.text(), "Ctrl+U")
                undo_found = True
            elif action_item.text() == "redo":
                self.assertEqual(shortcut_item.text(), "Ctrl+R")
                redo_found = True

        self.assertTrue(undo_found)
        self.assertTrue(redo_found)

        dialog.close()
        dialog.deleteLater()

    def test_reset_all_clears_pending(self):
        """Test that reset all clears pending changes."""
        # Add some pending changes
        self.dialog._pending_changes["undo"] = "Ctrl+U"
        self.dialog._pending_changes["redo"] = "Ctrl+R"

        self.assertEqual(len(self.dialog._pending_changes), 2)

        # Reset all
        self.dialog._reset_all()

        # Pending changes should be cleared
        self.assertEqual(len(self.dialog._pending_changes), 0)

    def test_search_matches_multiple_columns(self):
        """Test that search matches in multiple columns."""
        # Search for "file" should match category, action, or description
        self.dialog.search_box.setText("file")
        self.dialog._filter_shortcuts("file")

        visible_rows = sum(
            1
            for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )

        # Should find multiple matches
        self.assertGreater(visible_rows, 0)


if __name__ == "__main__":
    unittest.main()
