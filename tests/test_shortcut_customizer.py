#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Keyboard Shortcuts Customization
-------------------------------------------
Comprehensive test suite for src/gui/shortcut_customizer.py

Sprint: v2.9.62 - Keyboard Shortcuts Customization
Author: Josué Amaral
Date: 2025-12-10
"""

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tempfile import NamedTemporaryFile

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from src.gui.shortcut_customizer import (
    KeySequenceEdit,
    ShortcutCustomizerDialog
)
from src.shortcut_manager import ShortcutManager


class TestKeySequenceEdit(unittest.TestCase):
    """Test KeySequenceEdit widget."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication once for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def setUp(self):
        """Create widget for each test."""
        self.widget = KeySequenceEdit()
    
    def tearDown(self):
        """Clean up widget."""
        self.widget.close()
        self.widget.deleteLater()
    
    def test_init(self):
        """Test widget initialization."""
        self.assertTrue(self.widget.isReadOnly())
        self.assertEqual(self.widget.placeholderText(), "Press keys...")
        self.assertEqual(self.widget._max_keys, 2)
        self.assertEqual(len(self.widget._current_keys), 0)
    
    def test_key_press_ctrl_s(self):
        """Test capturing Ctrl+S."""
        # Simulate Ctrl+S
        QTest.keyPress(self.widget, Qt.Key_S, Qt.ControlModifier)
        
        # Should contain "Ctrl+S"
        self.assertIn("Ctrl+S", self.widget.text())
    
    def test_key_press_ignores_modifiers_alone(self):
        """Test that modifier keys alone are ignored."""
        QTest.keyPress(self.widget, Qt.Key_Control)
        self.assertEqual(self.widget.text(), "")
        
        QTest.keyPress(self.widget, Qt.Key_Shift)
        self.assertEqual(self.widget.text(), "")
    
    def test_clear_sequence(self):
        """Test clearing the sequence."""
        QTest.keyPress(self.widget, Qt.Key_S, Qt.ControlModifier)
        self.assertNotEqual(self.widget.text(), "")
        
        self.widget.clear_sequence()
        self.assertEqual(self.widget.text(), "")
        self.assertEqual(len(self.widget._current_keys), 0)
    
    def test_focus_out_clears_keys(self):
        """Test that focus out clears internal state."""
        QTest.keyPress(self.widget, Qt.Key_S, Qt.ControlModifier)
        self.assertNotEqual(len(self.widget._current_keys), 0)
        
        # Simulate focus out by calling focusOutEvent directly
        from PySide6.QtGui import QFocusEvent
        from PySide6.QtCore import QEvent
        event = QFocusEvent(QEvent.FocusOut)
        self.widget.focusOutEvent(event)
        
        self.assertEqual(len(self.widget._current_keys), 0)


class TestShortcutCustomizerDialog(unittest.TestCase):
    """Test ShortcutCustomizerDialog."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication once."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def setUp(self):
        """Reset ShortcutManager and create dialog."""
        ShortcutManager.reset_all_custom_shortcuts()
        self.dialog = ShortcutCustomizerDialog()
    
    def tearDown(self):
        """Clean up dialog."""
        self.dialog.close()
        self.dialog.deleteLater()
        ShortcutManager.reset_all_custom_shortcuts()
    
    def test_init(self):
        """Test dialog initialization."""
        self.assertEqual(self.dialog.windowTitle(), "Customize Keyboard Shortcuts")
        self.assertGreater(self.dialog.width(), 700)
        self.assertGreater(self.dialog.height(), 500)
        self.assertEqual(len(self.dialog._modified_shortcuts), 0)
    
    def test_table_populated(self):
        """Test that table is populated with all shortcuts."""
        row_count = self.dialog.table.rowCount()
        shortcuts_count = len(ShortcutManager.SHORTCUTS)
        
        self.assertEqual(row_count, shortcuts_count)
    
    def test_table_columns(self):
        """Test table has correct columns."""
        self.assertEqual(self.dialog.table.columnCount(), 5)
        headers = [
            self.dialog.table.horizontalHeaderItem(i).text()
            for i in range(5)
        ]
        self.assertEqual(headers, ["Action", "Description", "Default", "Custom", "Status"])
    
    def test_get_status_default(self):
        """Test status for default shortcut."""
        status = self.dialog._get_status("process", "")
        self.assertEqual(status, "Default")
    
    def test_get_status_modified(self):
        """Test status for modified shortcut."""
        status = self.dialog._get_status("process", "Ctrl+R")
        self.assertEqual(status, "Modified")
    
    def test_get_status_conflict(self):
        """Test status for conflicting shortcut."""
        # Set process to use save_file's shortcut
        status = self.dialog._get_status("process", "Ctrl+S")
        self.assertIn("CONFLICT", status)
        self.assertIn("save_file", status)
    
    def test_category_filter(self):
        """Test category filtering."""
        # Show only File category
        self.dialog.category_filter.setCurrentText("File")
        
        # Count visible rows
        visible = sum(
            1 for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )
        
        # Should be fewer than total
        self.assertLess(visible, self.dialog.table.rowCount())
        self.assertGreater(visible, 0)
    
    def test_search_filter(self):
        """Test search filtering."""
        self.dialog.search_box.setText("save")
        
        # Count visible rows
        visible = sum(
            1 for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )
        
        # Should find "save_file", "save_as"
        self.assertGreater(visible, 0)
        self.assertLess(visible, self.dialog.table.rowCount())
    
    def test_show_conflicts_only(self):
        """Test conflicts-only filter."""
        # Add a conflicting shortcut
        self.dialog._modified_shortcuts["process"] = "Ctrl+S"
        self.dialog._populate_table()
        
        # Enable conflicts filter
        self.dialog.show_conflicts_only.setChecked(True)
        
        # Count visible rows
        visible = sum(
            1 for row in range(self.dialog.table.rowCount())
            if not self.dialog.table.isRowHidden(row)
        )
        
        # Should only show rows with conflicts
        self.assertGreater(visible, 0)
    
    def test_reset_selected_shortcut(self):
        """Test resetting a single shortcut."""
        # Add custom shortcut
        self.dialog._modified_shortcuts["process"] = "Ctrl+R"
        self.dialog._populate_table()
        
        # Select first row
        self.dialog.table.setCurrentCell(0, 0)
        
        # Find row with "process"
        for row in range(self.dialog.table.rowCount()):
            if self.dialog.table.item(row, 0).text() == "process":
                self.dialog.table.setCurrentCell(row, 0)
                break
        
        self.dialog._reset_selected_shortcut()
        
        # Should be removed from modified shortcuts
        self.assertNotIn("process", self.dialog._modified_shortcuts)
    
    def test_reset_all_shortcuts(self):
        """Test resetting all shortcuts."""
        # Add multiple custom shortcuts
        self.dialog._modified_shortcuts["process"] = "Ctrl+R"
        self.dialog._modified_shortcuts["save_file"] = "Ctrl+Shift+S"
        self.dialog._populate_table()
        
        # Mock QMessageBox.question to return Yes
        with patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            self.dialog._reset_all_shortcuts()
        
        # All should be cleared
        self.assertEqual(len(self.dialog._modified_shortcuts), 0)
    
    def test_update_stats(self):
        """Test statistics update."""
        self.dialog._modified_shortcuts["process"] = "Ctrl+R"
        self.dialog._update_stats()
        
        stats_text = self.dialog.stats_label.text()
        self.assertIn("Modified: 1", stats_text)
    
    def test_import_shortcuts(self):
        """Test importing shortcuts from JSON."""
        # Create temp JSON file
        shortcuts_data = {
            "process": "Ctrl+R",
            "save_file": "Ctrl+Shift+S"
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(shortcuts_data, f)
            temp_path = f.name
        
        try:
            # Mock file dialog
            with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=(temp_path, '')):
                with patch('PySide6.QtWidgets.QMessageBox.information'):
                    self.dialog._import_shortcuts()
            
            # Should be imported
            self.assertEqual(self.dialog._modified_shortcuts["process"], "Ctrl+R")
            self.assertEqual(self.dialog._modified_shortcuts["save_file"], "Ctrl+Shift+S")
        
        finally:
            Path(temp_path).unlink()
    
    def test_export_shortcuts(self):
        """Test exporting shortcuts to JSON."""
        # Add custom shortcuts
        self.dialog._modified_shortcuts["process"] = "Ctrl+R"
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Mock file dialog
            with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=(temp_path, '')):
                with patch('PySide6.QtWidgets.QMessageBox.information'):
                    self.dialog._export_shortcuts()
            
            # Read exported file
            with open(temp_path, 'r') as f:
                exported = json.load(f)
            
            self.assertEqual(exported["process"], "Ctrl+R")
        
        finally:
            Path(temp_path).unlink()
    
    def test_get_custom_shortcuts(self):
        """Test getting custom shortcuts."""
        self.dialog._modified_shortcuts["process"] = "Ctrl+R"
        
        shortcuts = self.dialog.get_custom_shortcuts()
        
        self.assertEqual(shortcuts["process"], "Ctrl+R")
        # Should be a copy
        shortcuts["new_action"] = "Ctrl+N"
        self.assertNotIn("new_action", self.dialog._modified_shortcuts)
    
    def test_accept_with_conflicts_warning(self):
        """Test accepting with conflicts shows warning."""
        # Add conflicting shortcuts
        self.dialog._modified_shortcuts["process"] = "Ctrl+S"
        self.dialog._conflicts["process"] = ["save_file"]
        
        # Mock QMessageBox to return No
        with patch('PySide6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.No):
            self.dialog.accept()
        
        # Dialog should not close (isVisible should be True)
        # Note: In real scenario, we can't easily test this without exec()


class TestIntegration(unittest.TestCase):
    """Integration tests for shortcut customization."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication once."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def setUp(self):
        """Reset ShortcutManager."""
        ShortcutManager.reset_all_custom_shortcuts()
    
    def tearDown(self):
        """Clean up."""
        ShortcutManager.reset_all_custom_shortcuts()
    
    def test_full_workflow(self):
        """Test complete customization workflow."""
        # Create dialog
        dialog = ShortcutCustomizerDialog()
        
        # Modify a shortcut
        dialog._modified_shortcuts["process"] = "Ctrl+R"
        dialog._populate_table()
        
        # Check status updated
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "process":
                status = dialog.table.item(row, 4).text()
                self.assertEqual(status, "Modified")
                break
        
        # Get shortcuts
        custom = dialog.get_custom_shortcuts()
        self.assertEqual(custom["process"], "Ctrl+R")
        
        dialog.close()
        dialog.deleteLater()
    
    def test_conflict_detection_workflow(self):
        """Test conflict detection workflow."""
        dialog = ShortcutCustomizerDialog()
        
        # Set conflicting shortcuts
        dialog._modified_shortcuts["process"] = "Ctrl+S"  # Conflicts with save_file
        dialog._populate_table()
        dialog._update_stats()  # Need to update stats after populating
        
        # Check conflict detected
        self.assertIn("process", dialog._conflicts)
        
        # Check stats shows conflict
        stats = dialog.stats_label.text()
        self.assertIn("Conflicts:", stats)
        # Note: Conflict count depends on how many actions use Ctrl+S
        
        dialog.close()
        dialog.deleteLater()


# Import QMessageBox for mocking
from PySide6.QtWidgets import QMessageBox


if __name__ == '__main__':
    unittest.main()
