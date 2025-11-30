#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for EditorDock

Tests:
- File opening and loading
- File saving (save/save as)
- Syntax highlighting setup
- Tab management (new, close, switch)
- Modified state tracking
- Recent files list
- Tab title updates
"""

import unittest
import tempfile
import os
from pathlib import Path

# Import Qt test utilities
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# Import module to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.editor_dock import EditorDock, EditorTab, SyntaxHighlighter


class TestEditorTab(unittest.TestCase):
    """Test EditorTab functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Setup test fixtures."""
        self.tab = EditorTab()
    
    def tearDown(self):
        """Cleanup."""
        self.tab.deleteLater()
    
    def test_initial_state(self):
        """Test initial state of EditorTab."""
        self.assertIsNone(self.tab.file_path)
        self.assertFalse(self.tab.is_modified)
        self.assertEqual(self.tab.get_tab_title(), "Untitled")
    
    def test_load_file(self):
        """Test loading file into editor."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!\nLine 2\nLine 3")
            temp_path = f.name
        
        try:
            # Load file
            success = self.tab.load_file(temp_path)
            self.assertTrue(success)
            self.assertEqual(self.tab.file_path, temp_path)
            self.assertFalse(self.tab.is_modified)
            self.assertIn("Hello, World!", self.tab.editor.toPlainText())
        finally:
            os.unlink(temp_path)
    
    def test_save_file(self):
        """Test saving file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            # Set content and file path
            self.tab.editor.setPlainText("Test content")
            self.tab.file_path = temp_path
            self.tab.is_modified = True
            
            # Save
            success = self.tab.save_file()
            self.assertTrue(success)
            self.assertFalse(self.tab.is_modified)
            
            # Verify content
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Test content")
        finally:
            os.unlink(temp_path)
    
    def test_modified_state(self):
        """Test modified state tracking."""
        modified_emitted = []
        self.tab.modified_changed.connect(lambda m: modified_emitted.append(m))
        
        # Initial state: not modified
        self.assertFalse(self.tab.is_modified)
        
        # Edit text
        self.tab.editor.setPlainText("Some text")
        QApplication.processEvents()
        
        # Should be modified
        self.assertTrue(self.tab.is_modified)
        self.assertEqual(len(modified_emitted), 1)
        self.assertTrue(modified_emitted[0])
    
    def test_tab_title_with_modification(self):
        """Test tab title includes asterisk when modified."""
        self.tab.file_path = "/path/to/test.py"
        self.tab.is_modified = False
        self.assertEqual(self.tab.get_display_title(), "test.py")
        
        self.tab.is_modified = True
        self.assertEqual(self.tab.get_display_title(), "test.py *")
    
    def test_syntax_highlighter_setup(self):
        """Test syntax highlighter is set up based on file extension."""
        # Python file
        self.tab.file_path = "/path/to/test.py"
        self.tab._setup_highlighter()
        self.assertIsNotNone(self.tab.highlighter)
        self.assertEqual(self.tab.highlighter.file_type, "py")
        
        # JSON file
        self.tab.file_path = "/path/to/data.json"
        self.tab._setup_highlighter()
        self.assertIsNotNone(self.tab.highlighter)
        self.assertEqual(self.tab.highlighter.file_type, "json")


class TestSyntaxHighlighter(unittest.TestCase):
    """Test SyntaxHighlighter functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_html_rules(self):
        """Test HTML syntax highlighting rules."""
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = SyntaxHighlighter(doc, "html")
        
        # Should have rules for tags, attributes, strings
        self.assertGreater(len(highlighter.rules), 0)
    
    def test_json_rules(self):
        """Test JSON syntax highlighting rules."""
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = SyntaxHighlighter(doc, "json")
        
        # Should have rules for keys, strings, numbers, brackets
        self.assertGreater(len(highlighter.rules), 0)
    
    def test_python_rules(self):
        """Test Python syntax highlighting rules."""
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = SyntaxHighlighter(doc, "py")
        
        # Should have rules for keywords, strings, comments
        self.assertGreater(len(highlighter.rules), 0)
    
    def test_javascript_rules(self):
        """Test JavaScript syntax highlighting rules."""
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        highlighter = SyntaxHighlighter(doc, "js")
        
        # Should have rules for keywords, strings, comments
        self.assertGreater(len(highlighter.rules), 0)


class TestEditorDock(unittest.TestCase):
    """Test EditorDock functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Setup test fixtures."""
        self.dock = EditorDock()
    
    def tearDown(self):
        """Cleanup."""
        self.dock.deleteLater()
    
    def test_initial_state(self):
        """Test initial state of EditorDock."""
        self.assertEqual(self.dock.tab_widget.count(), 0)
        self.assertEqual(len(self.dock.recent_files), 0)
        self.assertEqual(self.dock.max_recent, 10)
    
    def test_new_file(self):
        """Test creating new file."""
        initial_count = self.dock.tab_widget.count()
        self.dock._new_file()
        QApplication.processEvents()
        
        self.assertEqual(self.dock.tab_widget.count(), initial_count + 1)
        tab = self.dock.tab_widget.widget(0)
        self.assertIsNone(tab.file_path)
        self.assertEqual(tab.get_tab_title(), "Untitled")
    
    def test_open_file(self):
        """Test opening file (programmatically)."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('Hello')")
            temp_path = f.name
        
        try:
            # Open file using public API
            self.dock.open_file_path(temp_path)
            QApplication.processEvents()
            
            # Should have one tab
            self.assertEqual(self.dock.tab_widget.count(), 1)
            tab = self.dock.tab_widget.widget(0)
            self.assertEqual(tab.file_path, temp_path)
            self.assertIn("Hello", tab.editor.toPlainText())
            
            # Should be in recent files
            self.assertIn(temp_path, self.dock.recent_files)
        finally:
            os.unlink(temp_path)
    
    def test_close_tab(self):
        """Test closing tab."""
        # Create new file
        self.dock._new_file()
        QApplication.processEvents()
        
        initial_count = self.dock.tab_widget.count()
        
        # Close tab (unmodified, should close without prompt)
        tab = self.dock.tab_widget.widget(0)
        tab.is_modified = False  # Ensure not modified
        self.dock._close_tab(0)
        QApplication.processEvents()
        
        self.assertEqual(self.dock.tab_widget.count(), initial_count - 1)
    
    def test_tab_switching(self):
        """Test switching between tabs."""
        # Create two files
        self.dock._new_file()
        self.dock._new_file()
        QApplication.processEvents()
        
        self.assertEqual(self.dock.tab_widget.count(), 2)
        
        # Switch to first tab
        self.dock.tab_widget.setCurrentIndex(0)
        QApplication.processEvents()
        self.assertEqual(self.dock.tab_widget.currentIndex(), 0)
        
        # Switch to second tab
        self.dock.tab_widget.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertEqual(self.dock.tab_widget.currentIndex(), 1)
    
    def test_recent_files_list(self):
        """Test recent files list management."""
        # Add files to recent list
        files = [f"/path/to/file{i}.txt" for i in range(15)]
        
        for file in files:
            self.dock._add_recent_file(file)
        
        # Should be limited to max_recent (10)
        self.assertEqual(len(self.dock.recent_files), self.dock.max_recent)
        
        # Most recent should be first
        self.assertEqual(self.dock.recent_files[0], files[-1])
    
    def test_duplicate_file_open(self):
        """Test opening same file twice (should switch to existing tab)."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            # Open file twice
            self.dock.open_file_path(temp_path)
            QApplication.processEvents()
            
            initial_count = self.dock.tab_widget.count()
            
            self.dock.open_file_path(temp_path)
            QApplication.processEvents()
            
            # Should still have same number of tabs (no duplicate)
            self.assertEqual(self.dock.tab_widget.count(), initial_count)
        finally:
            os.unlink(temp_path)
    
    def test_open_nonexistent_file(self):
        """Test opening non-existent file (should show warning)."""
        initial_count = self.dock.tab_widget.count()
        
        # Try to open non-existent file
        self.dock.open_file_path("/nonexistent/path/file.txt")
        QApplication.processEvents()
        
        # Should not create new tab
        self.assertEqual(self.dock.tab_widget.count(), initial_count)


if __name__ == '__main__':
    unittest.main()
